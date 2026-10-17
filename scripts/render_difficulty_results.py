#!/usr/bin/env python3
"""Render difficulty-study comparisons from the checked summary, offline."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter
from render_benchmark_results import plot_data, render_block, COLORS, LABELS, INK, MUTED

ROOT = Path(__file__).resolve().parents[1]
MODELS = ('qwen36', 'glm53flash')
ARMS = ('direct', 'solver_augmented')
TIERS = ('easy', 'moderate', 'hard', 'very_hard', 'extreme')
BLOCKS = {
    'controlled': ('Controlled scheduling', '60 canonical cases per approach; generation and repair',
                   'Known synthetic development cases. GLM direct rejections are HTTP 502 failures.'),
    'realistic': ('Fictional scenarios', '20 scenarios per approach; generation and repair',
                  'AI-assisted fictional templates; human interpretation review remains pending.'),
    'language': ('Additional wording', '20 wording conditions per approach; 10 controlled bases',
                 'GLM: Direct has two HTTP 502 errors; LLM + CP-SAT has two invalid schedules.'),
}


def style_axis(ax):
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines[['left', 'bottom']].set_color('#C7D0D9')
    ax.grid(axis='y', color='#E1E7ED', linewidth=.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, pad=6)


def tier_figure(summary):
    fig, axes = plt.subplots(2, 1, figsize=(6.2, 5.0))
    fig.subplots_adjust(left=.14, right=.98, bottom=.10, top=.81, hspace=.55)
    fig.text(.14, .97, 'Controlled acceptance by construction tier', fontsize=13, weight='bold')
    fig.legend(handles=[Patch(color=COLORS[a], label=LABELS[a]) for a in ARMS],
               loc='upper left', bbox_to_anchor=(.125,.95), ncol=2, frameon=False, fontsize=11)
    for ax, model in zip(axes, MODELS):
        data = summary['models'][model]
        ax.set_title(data['model'], loc='left', fontsize=11, pad=8)
        for j, arm in enumerate(ARMS):
            rows = [data['controlled_tiers'][tier][arm] for tier in TIERS]
            bars = ax.bar([x+(j-.5)*.36 for x in range(5)],
                          [100*r['accepted']/r['attempts'] for r in rows],
                          width=.33, color=COLORS[arm])
            # Exact counts avoid tiny decimal labels; every cell has 12 attempts.
            ax.bar_label(bars, labels=[str(r['accepted']) for r in rows], fontsize=11, padding=3)
        ax.set_xticks(range(5), ['Easy', 'Moderate', 'Hard', 'Very hard', 'Extreme'], fontsize=11)
        ax.set_ylim(0,125); ax.set_yticks([0,50,100]);ax.yaxis.set_major_formatter(PercentFormatter(100,decimals=0))
        ax.set_ylabel('Accepted', fontsize=11);style_axis(ax)
    return fig


def resource_figure(summary):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.7))
    fig.subplots_adjust(left=.09, right=.97, bottom=.24, top=.70, wspace=.38)
    fig.text(.07,.95,'Model-call time and reported token use',fontsize=18,weight='bold')
    fig.legend(handles=[Patch(color=COLORS[a],label=LABELS[a]) for a in ARMS],
               loc='upper left',bbox_to_anchor=(.06,.89),ncol=2,frameon=False,fontsize=11)
    for ax, metric, ylabel in zip(axes, ['model_seconds','total_tokens'],['Mean call time (seconds)','Mean reported tokens']):
        for j, arm in enumerate(ARMS):
            rows=[summary['models'][m]['resources'][arm][metric] for m in MODELS]
            bars=ax.bar([i+(j-.5)*.32 for i in range(2)], [r['mean'] for r in rows],width=.29,color=COLORS[arm])
            ax.bar_label(bars,labels=[f"{r['mean']:,.1f}" for r in rows],fontsize=11,padding=4)
        ax.set_xticks(range(2),['Qwen3.6','GLM5.3 Flash'],fontsize=11)
        ax.set_ylim(0,ax.get_ylim()[1]*1.16);ax.set_ylabel(ylabel,fontsize=11);style_axis(ax)
    fig.text(.07,.10,'Time includes failed requests (100/100 per bar). Token coverage: Qwen A 96/100, B 98/100; GLM A 91/100, B 100/100.',fontsize=10)
    fig.text(.07,.05,'Missing usage is unknown. Shared-service timings do not isolate model speed; GLM A includes nine ~300-second HTTP 502s.',fontsize=10)
    return fig


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=ROOT/'results/summary/difficulty-comparison-20261014.json')
    parser.add_argument('--output',type=Path,default=ROOT/'results/figures/difficulty-comparison-20261014')
    parser.add_argument('--report',action='store_true')
    args=parser.parse_args()
    raw=args.source.read_bytes();summary=json.loads(raw)
    data=plot_data(summary,models=MODELS,blocks=BLOCKS)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':INK,
        'axes.labelcolor':INK,'xtick.color':MUTED,'ytick.color':MUTED,'pdf.fonttype':42,'figure.facecolor':'white'})
    args.output.mkdir(parents=True,exist_ok=True)
    figures={block+'-accepted':render_block(block,data[block],report=args.report,models=MODELS,blocks=BLOCKS)
             for block in BLOCKS}
    figures['controlled-tiers']=tier_figure(summary)
    if not args.report:
        figures['resources']=resource_figure(summary)
    outputs={}
    for name,fig in figures.items():
        for ext in ('png','pdf'):
            path=args.output/(name+'.'+ext)
            metadata={'Creator':'CS3263 offline difficulty comparison','CreationDate':None,'ModDate':None} if ext=='pdf' else {'Software':'CS3263 offline difficulty comparison'}
            fig.savefig(path,dpi=180,metadata=metadata)
            outputs[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
        plt.close(fig)
    receipt={'source_sha256':hashlib.sha256(raw).hexdigest(),'renderer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'shared_renderer_sha256':hashlib.sha256((ROOT/'scripts/render_benchmark_results.py').read_bytes()).hexdigest(),
        'new_model_calls':0,'matplotlib_version':matplotlib.__version__,'layout':'report' if args.report else 'standalone',
        'plotted_data':data,'controlled_tiers':{m:summary['models'][m]['controlled_tiers'] for m in MODELS},'output_sha256':outputs}
    (args.output/'figure-data.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(f'Rendered {len(outputs)} figures into {args.output}')


if __name__=='__main__':
    main()
