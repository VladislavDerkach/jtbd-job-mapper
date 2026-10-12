#!/usr/bin/env python3
"""Generate ready-to-run `use_figma` scripts from work/jobs.json.

Usage:
  build_figjam_code.py scaffold JOBS OUTDIR
  build_figjam_code.py segments JOBS OUTDIR --state work/figjam_state.json [--only SEG_ID ...]
  build_figjam_code.py graph    JOBS OUTDIR --state work/figjam_state.json
  build_figjam_code.py segmap   JOBS OUTDIR
  build_figjam_code.py read     JOBS OUTDIR [--root NODE_ID]

Each generated .js file is passed verbatim as the `code` argument of the Figma MCP `use_figma` tool.
Files stay under ~45k characters (use_figma limit is 50k). Add --check to syntax-check them with node.
"""
import argparse, json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FJ = os.path.join(HERE, 'figjam')
LIMIT = 45000
JOB_KEYS = ['n', 'type', 'title', 'who', 'basis', 'when', 'want', 'criteria', 'criteria_label', 'why', 'pos']


def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def code(action, data):
    return ('const DATA = ' + json.dumps(data, ensure_ascii=False) + ';\n'
            + read(os.path.join(FJ, 'lib.js')) + '\n' + read(os.path.join(FJ, action + '.js')))


def write(outdir, name, src, check):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(src)
    if len(src) > 50000:
        sys.exit(f'ERROR: {name} is {len(src)} chars, over the 50k use_figma limit')
    if check:
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as t:
            t.write('(async () => {\n' + src + '\n})();\n')
        r = subprocess.run(['node', '--check', t.name], capture_output=True, text=True)
        os.unlink(t.name)
        if r.returncode:
            sys.exit(f'SYNTAX ERROR in {name}:\n{r.stderr}')
    print(f'{path}  ({len(src)} chars)')


def segs_sorted(d):
    return sorted(d['segments'], key=lambda s: s.get('n', 999))


def job_payload(j):
    return {k: j.get(k) for k in JOB_KEYS if j.get(k) is not None}


def default_legend(d):
    leg = d['project'].get('legend')
    if leg:
        return leg
    return [
        'Description format: When (context, trigger, negative emotions, consideration set), Want to (the job and success criteria), So that (the goal and positive emotions).',
        'A dash: no data. "(hypothesis)": the research author\'s conclusion. Orange text marked [AI-ASSUMPTION]: an AI conclusion, needs checking.',
        'Basis: corpus (customer voice), desk (market description with no customer voice), author (the job was named by the research author).',
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['scaffold', 'segments', 'graph', 'segmap', 'read'])
    ap.add_argument('jobs'); ap.add_argument('outdir')
    ap.add_argument('--state'); ap.add_argument('--only', nargs='*'); ap.add_argument('--root')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    d = json.loads(read(a.jobs))
    state = json.loads(read(a.state)) if a.state else None
    jobs = sorted(d['jobs'], key=lambda j: j.get('n', 999))

    if a.mode == 'scaffold':
        data = {'title': d['project']['title'], 'legend': default_legend(d),
                'segments': [{'id': s['id'], 'n': s.get('n'), 'name': s['name']} for s in segs_sorted(d)]}
        write(a.outdir, '01_scaffold.js', code('scaffold', data), a.check)

    elif a.mode == 'segments':
        if not state:
            sys.exit('--state is required (ids returned by 01_scaffold.js)')
        batches = []
        for s in segs_sorted(d):
            if a.only and s['id'] not in a.only:
                continue
            node = state['segments'].get(s['id'])
            if not node:
                print(f"WARN: segment {s['id']} has no column in state; re-run scaffold or add it", file=sys.stderr)
                continue
            batches.append({'segNode': node, 'name': f"Segment {s.get('n', '')}. {s['name']}".replace('Segment . ', ''),
                            'intro': s.get('intro') or None,
                            'jobs': [job_payload(j) for j in jobs if j['segment'] == s['id']],
                            'copies': [job_payload(j) for j in jobs if s['id'] in (j.get('also_segments') or [])]})
        files, cur = [], []
        base = len(code('segments', {'board': state['board'], 'batch': []}))
        for b in batches:
            trial = cur + [b]
            if cur and base + len(json.dumps(trial, ensure_ascii=False)) > LIMIT:
                files.append(cur); cur = [b]
            else:
                cur = trial
        if cur:
            files.append(cur)
        for i, f in enumerate(files, 1):
            write(a.outdir, f'02_segments_{i:02d}.js', code('segments', {'board': state['board'], 'batch': f}), a.check)

    elif a.mode == 'graph':
        if not state:
            sys.exit('--state is required')
        num = {j['id']: j['n'] for j in jobs}
        edges = []
        for e in d.get('edges', []):
            if e['from'] in num and e['to'] in num:
                edges.append({'from': num[e['from']], 'to': num[e['to']], 'kind': e['kind']})
            else:
                print(f'WARN: edge {e} points to a missing job', file=sys.stderr)
        data = {'board': state['board'], 'title': 'Job graph: ' + d['project']['title'],
                'legendAdd': 'Lines: a solid orange arrow = sequential jobs. A dashed teal arrow = from a job to a higher-level one (for its sake, or as part of it). A grey dotted line with no arrows = the same job in another segment.',
                'edges': edges}
        write(a.outdir, '03_graph.js', code('graph', data), a.check)

    elif a.mode == 'segmap':
        strict = d['project'].get('strict_two_states', False)
        cards, notes, guess = [], [], []
        missing_fit = [j['n'] for j in jobs if j.get('fit') not in ('now', 'min', 'none')]
        if missing_fit:
            print(f'WARN: jobs without fit (drawn as empty circles): {missing_fit}', file=sys.stderr)
        ordered = sorted(segs_sorted(d), key=lambda s: (not s.get('compete', False), s.get('n', 999)))
        for s in ordered:
            sj = [j for j in jobs if j['segment'] == s['id'] or s['id'] in (j.get('also_segments') or [])]
            steps = []
            for j in sj:
                k = j.get('fit') or 'none'
                if strict and k == 'min':
                    k = 'none'
                steps.append([k, j['title']])
            if 'AI-ASSUMPTION' in (s.get('goal_basis') or '').upper():
                guess.append(s['name'])
            cards.append({'price': s.get('price', '?'), 'compete': bool(s.get('compete')),
                          'cap': f"Segment {s.get('n', '')}. {s['name']}", 'title': s.get('goal') or s['name'], 'steps': steps})
        prod = d['project'].get('product', {})
        notes.append('A map per the Next Move Theory canon: a card = a segment defined by a customer job; circles = the segment\'s jobs.')
        notes.append(f"\"Competing\": {prod.get('name', 'the product')} covers at least one of the segment's jobs already. Product state: {prod.get('state', 'not specified')}.")
        notes.append("$ signs = the size of the money in the segment's job; where the research has no numbers, this is a hypothesis.")
        if guess:
            notes.append('Goal statements are an AI assumption for segments: ' + ', '.join(guess) + '.')
        legend = [['now', f"{prod.get('name', 'The product')} covers it now"], ['none', "doesn't cover it"]]
        if not strict:
            legend.insert(1, ['min', 'covers it with minimal extra work'])
        write(a.outdir, '04_segment_map.js', code('segmap', {'title': 'Segment map', 'notes': notes, 'legend': legend, 'cards': cards}), a.check)

    elif a.mode == 'read':
        write(a.outdir, '90_read_board.js', code('read', {'root': a.root}), a.check)


if __name__ == '__main__':
    main()
