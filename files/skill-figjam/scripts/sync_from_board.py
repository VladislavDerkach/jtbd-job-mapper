#!/usr/bin/env python3
"""Compare the board dump (result of 90_read_board.js) with jobs.json after the user's manual edits.

Usage:
  sync_from_board.py work/jobs.json work/board_dump.json            # report only
  sync_from_board.py work/jobs.json work/board_dump.json --apply OUT # write an updated jobs.json

Rules used to read the board:
  solid line with an arrow        -> seq
  dashed line with an arrow       -> part (direction as drawn; report any arrow that points down a level)
  dashed line without arrows      -> same job in another segment (copy link), not an edge
Cards are matched by the number at the start of the blue title box.
"""
import argparse, copy, json, re


def norm_col(s):
    return re.sub(r'^Segment\s*\d+\.\s*', '', s or '').strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('jobs'); ap.add_argument('dump'); ap.add_argument('--apply')
    a = ap.parse_args()
    d = json.load(open(a.jobs, encoding='utf-8'))
    b = json.load(open(a.dump, encoding='utf-8'))
    jobs = {j['n']: j for j in d['jobs']}
    segs_by_name = {s['name']: s for s in d['segments']}
    primary = {c['n']: c for c in b['cards'] if not c.get('copy')}
    copies = [c for c in b['cards'] if c.get('copy')]

    print('== Columns (segments) ==')
    for col in b['columns']:
        name = norm_col(col)
        print(('   ' if name in segs_by_name else 'NEW ') + name)
    for s in d['segments']:
        if s['name'] not in {norm_col(c) for c in b['columns']}:
            print('GONE ' + s['name'])

    print('\n== Jobs ==')
    for n, j in sorted(jobs.items()):
        c = primary.get(n)
        if not c:
            print(f'REMOVED  {n}. {j["title"]}')
            continue
        title = re.sub(r"^\d+\.\s*(Business job: |Decision-maker's personal job: )?", '', c['title'])
        if title != j['title']:
            print(f'RENAMED  {n}. {j["title"]}  ->  {title}')
        col = norm_col(c['column'])
        seg = next((s for s in d['segments'] if s['id'] == j['segment']), None)
        if seg and col and col != seg['name']:
            print(f'MOVED    {n}. to column «{col}» (was «{seg["name"]}»)')
    for n, c in sorted(primary.items()):
        if n not in jobs:
            print(f'NEW      {c["title"]}')
    for c in copies:
        print(f'COPY     {c["title"]}  in «{norm_col(c["column"])}»')

    print('\n== Links ==')
    board_edges = set()
    for l in b['links']:
        if l['from'] is None or l['to'] is None:
            print(f'UNATTACHED link {l}')
            continue
        arrow_end = l.get('end_cap') not in (None, 'NONE')
        arrow_start = l.get('start_cap') not in (None, 'NONE')
        if l['dashed'] and not (arrow_end or arrow_start):
            continue  # copy link
        src, dst = (l['from'], l['to']) if arrow_end or not arrow_start else (l['to'], l['from'])
        kind = 'part' if l['dashed'] else 'seq'
        if l.get('from_copy') or l.get('to_copy'):
            print(f'NOTE     link touches a copy card: {src}->{dst} ({kind})')
        board_edges.add((src, dst, kind))
    id2n = {j['id']: j['n'] for j in d['jobs']}
    json_edges = {(id2n.get(e['from']), id2n.get(e['to']), e['kind']) for e in d.get('edges', [])}
    for e in sorted(board_edges - json_edges, key=str):
        print(f'ADDED    {e[0]} -> {e[1]} ({e[2]})')
    for e in sorted(json_edges - board_edges, key=str):
        print(f'DELETED  {e[0]} -> {e[1]} ({e[2]})')

    if a.apply:
        nd = copy.deepcopy(d)
        for col in b['columns']:
            name = norm_col(col)
            if name and name not in segs_by_name:
                sid = 'seg' + str(len(nd['segments']) + 1)
                nd['segments'].append({'id': sid, 'n': len(nd['segments']) + 1, 'name': name})
                segs_by_name[name] = nd['segments'][-1]
        nd['jobs'] = [j for j in nd['jobs'] if j['n'] in primary]
        for j in nd['jobs']:
            c = primary[j['n']]
            j['title'] = re.sub(r"^\d+\.\s*(Business job: |Decision-maker's personal job: )?", '', c['title'])
            col = norm_col(c['column'])
            if col in segs_by_name:
                j['segment'] = segs_by_name[col]['id']
            also = {segs_by_name[norm_col(x['column'])]['id'] for x in copies
                    if x['n'] == j['n'] and norm_col(x['column']) in segs_by_name}
            also.discard(j['segment'])
            j['also_segments'] = sorted(also)
        n2id = {j['n']: j['id'] for j in nd['jobs']}
        nd['edges'] = [{'from': n2id[s], 'to': n2id[t], 'kind': k, 'basis': 'board (manual edit)'}
                       for s, t, k in sorted(board_edges, key=str) if s in n2id and t in n2id]
        json.dump(nd, open(a.apply, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f'\nwritten {a.apply}. New cards that are not in jobs.json must be described by hand.')


if __name__ == '__main__':
    main()
