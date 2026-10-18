#!/usr/bin/env python3
"""Plot the two identical saved solver-assisted schedules; no new solving."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'results/summary/report-details-20261018.json'
OUT = ROOT / 'docs/figures/report-timetable-20261018'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT)
    args = parser.parse_args()
    case = json.loads(SOURCE.read_text())['worked_case']
    outputs = [v['solver_augmented'] for v in case['outputs'].values()]
    schedules = [v['pipeline_result']['schedule'] for v in outputs]
    if not all(v['accepted'] for v in outputs) or schedules[0] != schedules[1]:
        raise ValueError('The figure requires matching, accepted recorded schedules')
    problem = case['gold_case']['problem']
    activities = {a['id']: a for a in problem['activities']}
    plt.rcParams.update({'font.size': 11, 'font.family': 'DejaVu Sans'})
    fig, ax = plt.subplots(figsize=(6.2, 2.1), dpi=300)
    fig.subplots_adjust(left=.22, right=.95, top=.76, bottom=.10)
    palette = {'P1': '#DCEAF7', 'P2': '#FAE3CD'}
    positions = {'P1': 0, 'P2': 1, 'R1': 2.3}
    for y in positions.values():
        ax.axhspan(y-.36, y+.36, color='#F4F6F8', zorder=0)
    ax.axhline(1.65, color='#A9B6C4', linewidth=.7, zorder=0)
    blocks = []
    for entry in schedules[0]:
        activity = activities[entry['activity_id']]
        start, duration = entry['start_slot'], activity['duration_slots']
        person = activity['participant_ids'][0]
        for entity in activity['participant_ids'] + activity['resource_ids']:
            y = positions[entity]
            ax.add_patch(Rectangle((start, y-.34), duration, .68,
                                  facecolor=palette[person], edgecolor='#405469', linewidth=.8, zorder=2))
            ax.text(start+duration/2, y, activity['id'], ha='center', va='center', color='#172536', zorder=3)
            blocks.append({'entity': entity, 'activity': activity['id'], 'start_slot': start, 'duration_slots': duration})
    ax.set_xlim(0, 10)
    ax.set_ylim(2.8, -.5)
    ax.set_yticks(list(positions.values()), ['Person 1 (P1)', 'Person 2 (P2)', 'Room (R1)'])
    ax.set_xticks(range(0, 11, 2), [f'{9+i//2:02}:00' for i in range(0, 11, 2)])
    ax.set_xticks(range(1, 10, 2), minor=True)
    ax.xaxis.tick_top()
    ax.tick_params(axis='y', length=0, pad=9, labelcolor='#172536')
    ax.tick_params(axis='x', which='major', length=4, pad=7, color='#8C9CAC', labelcolor='#172536')
    ax.tick_params(axis='x', which='minor', length=2, color='#A9B6C4')
    ax.grid(axis='x', which='major', color='#C4CDD7', linewidth=.6, zorder=0)
    ax.grid(axis='x', which='minor', color='#DFE5EB', linewidth=.45, linestyle='--', zorder=0)
    for edge in ax.spines.values():
        edge.set_visible(False)
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output / 'worked-timetable.png'
    exports = {}
    for extension in ('png', 'pdf', 'svg'):
        exported = target.with_suffix('.'+extension)
        fig.savefig(exported, facecolor='white')
        if extension == 'svg':
            exported.write_text('\n'.join(line.rstrip() for line in exported.read_text().splitlines())+'\n')
        exports[exported.name] = hashlib.sha256(exported.read_bytes()).hexdigest()
    plt.close(fig)
    receipt = {'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               'figure_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
               'case_id': case['case_id'], 'font_size_pt_at_native_width': 11,
               'renderer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'exports': exports,
               'native_width_inches': 6.2, 'blocks': blocks,
               'recorded_schedules_equal': True, 'new_model_calls': 0}
    (args.output / 'worked-timetable-data.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
