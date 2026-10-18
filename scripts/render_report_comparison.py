#!/usr/bin/env python3
"""Render publication comparisons from saved data; never invoke models or rescore."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter
from render_diverse_results import ARMS, CATEGORIES, COLORS, INK, MODELS, NAMES, ROOT, plot_data

LABELS = {'direct': 'A  Direct LLM', 'solver_augmented': 'B  LLM + CP-SAT'}
CATEGORY_LABELS = ['Constraint violation', 'False UNSAT', 'Output format', 'Infrastructure']


def style(ax):
    ax.set_axisbelow(True)
    ax.grid(axis='x', color='#E4E8ED', linewidth=.6)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.spines['bottom'].set_color('#B8C1CB')
    ax.spines['bottom'].set_linewidth(.6)
    ax.tick_params(axis='both', length=0, pad=7, labelsize=11)


def legend(fig):
    fig.legend(handles=[Patch(facecolor=COLORS[a], label=LABELS[a]) for a in ARMS],
               loc='upper center', bbox_to_anchor=(.52, .995), ncol=2,
               frameon=False, fontsize=11, handlelength=1.25,
               handletextpad=.55, columnspacing=1.8)


def acceptance(data):
    fig, ax = plt.subplots(figsize=(6.2, 2.65))
    fig.subplots_adjust(left=.20, right=.65, top=.80, bottom=.24)
    legend(fig)
    centers = [2.9, 1.1]
    for j, arm in enumerate(ARMS):
        y = [v + (.32 if j == 0 else -.32) for v in centers]
        values = [data[m][arm]['percent'] for m in MODELS]
        ax.barh(y, values, height=.44, color=COLORS[arm], edgecolor='none', zorder=3)
        for yy, model in zip(y, MODELS):
            row = data[model][arm]
            ax.text(1.045, yy, f'{row["percent"]:.1f}%  ({row["accepted"]:,}/{row["attempts"]:,})',
                    transform=ax.get_yaxis_transform(), ha='left', va='center',
                    fontsize=11, color=INK, clip_on=False)
    ax.set_ylim(.35, 3.65)
    ax.set_yticks(centers, ['Qwen3.6', 'GLM5.3\nFlash'])
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.xaxis.set_major_formatter(PercentFormatter(100, decimals=0))
    ax.set_xlabel('Acceptance rate', fontsize=11, labelpad=9)
    style(ax)
    return fig


def failures(data):
    fig, axes = plt.subplots(1, 2, figsize=(6.2, 3.25), sharex=True, sharey=True)
    fig.subplots_adjust(left=.285, right=.97, top=.76, bottom=.18, wspace=.38)
    legend(fig)
    for ax, model in zip(axes, MODELS):
        ax.set_title(NAMES[model], fontsize=11, weight='bold', loc='left', pad=12)
        for j, arm in enumerate(ARMS):
            y = [i + (-.17 if j == 0 else .17) for i in range(4)]
            values = [data[model][arm]['failures'][c] for c in CATEGORIES]
            bars = ax.barh(y, values, height=.28, color=COLORS[arm], edgecolor='none', zorder=3)
            ax.bar_label(bars, labels=[str(v) for v in values], padding=3, fontsize=11, color=INK)
        ax.set_xlim(0, 340)
        ax.set_xticks([0, 100, 200, 300])
        ax.set_ylim(3.55, -.55)
        style(ax)
    axes[0].set_yticks(range(4), CATEGORY_LABELS)
    axes[1].tick_params(axis='y', labelleft=False)
    fig.supxlabel('Failed attempts (same scale in both panels)', fontsize=11, x=.62, y=.035)
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'results/summary/diverse-comparison-20261018.json')
    parser.add_argument('--output', type=Path, default=ROOT/'docs/figures/report-polished-20261018')
    args = parser.parse_args()
    raw = args.source.read_bytes()
    data = plot_data(json.loads(raw))
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'text.color': INK, 'axes.labelcolor': INK,
                         'xtick.color': '#52606D', 'ytick.color': INK,
                         'figure.facecolor': 'white', 'pdf.fonttype': 42})
    args.output.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for name, fig in [('diverse-acceptance', acceptance(data)), ('diverse-failures', failures(data))]:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        for text in fig.findobj(matplotlib.text.Text):
            if not text.get_visible() or not text.get_text():
                continue
            assert text.get_fontsize() >= 11
            bounds = text.get_window_extent(renderer)
            if not fig.bbox.contains(bounds.x0, bounds.y0) or not fig.bbox.contains(bounds.x1, bounds.y1):
                raise ValueError(f'Text outside figure: {text.get_text()}')
        for suffix in ['png', 'pdf']:
            path = args.output/f'{name}.{suffix}'
            fig.savefig(path, dpi=300, facecolor='white')
            outputs[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        plt.close(fig)
    receipt = {'source_sha256': hashlib.sha256(raw).hexdigest(),
               'renderer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'data_helper_sha256': hashlib.sha256((ROOT/'scripts/render_diverse_results.py').read_bytes()).hexdigest(),
               'new_model_calls': 0, 'width_inches': 6.2, 'minimum_text_points': 11,
               'matplotlib_version': matplotlib.__version__, 'plotted_data': data,
               'output_sha256': outputs,
               'notes': ['All 1,000 attempts per method retained, including failures.',
                         'Acceptance labels show percent and accepted/attempted count.',
                         'Grouped horizontal failure bars use one common linear count scale.',
                         'Failure categories are mutually exclusive; suboptimal valid schedules remain accepted.',
                         'Earlier figure versions and original results remain unchanged.']}
    (args.output/'figure-data.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('Rendered two PNG/PDF figures with checked labels and preserved data; zero model calls.')


if __name__ == '__main__':
    main()
