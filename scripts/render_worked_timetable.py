#!/usr/bin/env python3
"""Plot the two identical saved solver-assisted schedules; no new solving."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'results/summary/report-details-20261018.json'
OUT = ROOT / 'docs/figures/report-compact-20261018'


def main():
    case = json.loads(SOURCE.read_text())['worked_case']
    outputs = [v['solver_augmented'] for v in case['outputs'].values()]
    schedules = [v['pipeline_result']['schedule'] for v in outputs]
    if not all(v['accepted'] for v in outputs) or schedules[0] != schedules[1]:
        raise ValueError('The figure requires matching, accepted recorded schedules')
    problem = case['gold_case']['problem']
    activities = {a['id']: a for a in problem['activities']}
    plt.rcParams.update({'font.size': 11, 'font.family': 'DejaVu Sans'})
    fig, ax = plt.subplots(figsize=(6.2, 1.65), dpi=220)
    fig.subplots_adjust(left=.10, right=.94, top=.74, bottom=.06)
    rows = ['P1', 'P2', 'R1']
    palette = {'P1': '#dceafa', 'P2': '#fbe5cf'}
    blocks = []
    for entry in schedules[0]:
        activity = activities[entry['activity_id']]
        start, duration = entry['start_slot'], activity['duration_slots']
        person = activity['participant_ids'][0]
        for entity in activity['participant_ids'] + activity['resource_ids']:
            y = rows.index(entity)
            ax.add_patch(Rectangle((start, y-.46), duration, .92,
                                  facecolor=palette[person], edgecolor='#405469', linewidth=.8, zorder=2))
            ax.text(start+duration/2, y, activity['id'], ha='center', va='center', color='#172536', zorder=3)
            blocks.append({'entity': entity, 'activity': activity['id'], 'start_slot': start, 'duration_slots': duration})
    ax.set_xlim(0, 10)
    ax.set_ylim(2.5, -.5)
    ax.set_yticks(range(3), rows)
    ax.set_xticks(range(0, 11, 2), [f'{9+i//2:02}:00' for i in range(0, 11, 2)])
    ax.set_xticks(range(11), minor=True)
    ax.xaxis.tick_top()
    ax.get_xticklabels()[0].set_ha('left')
    ax.get_xticklabels()[-1].set_ha('right')
    ax.tick_params(axis='both', length=0, pad=7)
    ax.tick_params(axis='x', which='minor', length=0)
    ax.grid(axis='x', which='both', color='#c9d3df', linewidth=.6, zorder=0)
    for edge in ax.spines.values():
        edge.set_visible(False)
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / 'worked-timetable.png'
    fig.savefig(target, facecolor='white')
    plt.close(fig)
    receipt = {'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               'figure_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
               'case_id': case['case_id'], 'font_size_pt_at_native_width': 11,
               'native_width_inches': 6.2, 'blocks': blocks,
               'recorded_schedules_equal': True, 'new_model_calls': 0}
    (OUT / 'worked-timetable-data.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
