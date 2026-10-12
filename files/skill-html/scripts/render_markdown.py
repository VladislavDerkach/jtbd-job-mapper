#!/usr/bin/env python3
"""Render work/jobs.json as a Markdown document (for Google Docs import or a plain .md deliverable).

Usage: render_markdown.py work/jobs.json work/jobs.md
"""
import json, sys


def val(v, indent='    '):
    if isinstance(v, list):
        return '\n' + '\n'.join(f'{indent}- {x}' for x in v)
    return ' ' + (v or '—')


def prefix(j):
    return {'b2b-business': 'Business job: ', 'b2b-personal': "Decision-maker's personal job: "}.get(j.get('type'), '')


JOB_TYPE = {
    'orientation': 'orientation — the person is choosing between solutions',
    'tax': "Tax Job — unplanned rework because a hired solution didn't work out",
    'fake': "Fake Job — no past investment behind it; don't build a product on it",
    'emotional': 'emotional — the expected outcome is an emotional shift, there is no higher-level job',
    'viral': 'viral — the person does it for, or together with, someone else',
}


def main(src, dst):
    d = json.load(open(src, encoding='utf-8'))
    out = [f"# {d['project']['title']}", '']
    out += ['Format: When / Want to / So that (Advanced JTBD + Next Move Theory). "—" = no data. '
            '"(hypothesis)" = the research author\'s conclusion. **[AI-ASSUMPTION]** = an AI conclusion, needs checking.', '']
    src_list = d['project'].get('sources') or []
    if src_list:
        out += ['## Sources', ''] + [f"- **{s['id']}** ({s.get('kind', '')}): {s['title']}" for s in src_list] + ['']
    jobs = sorted(d['jobs'], key=lambda j: j.get('n', 999))
    for s in sorted(d['segments'], key=lambda s: s.get('n', 999)):
        out += [f"## Segment {s.get('n', '')}. {s['name']}", '']
        if s.get('intro'):
            out += [s['intro'], '']
        seg_jobs = [j for j in jobs if j['segment'] == s['id']]
        copies = [j for j in jobs if s['id'] in (j.get('also_segments') or [])]
        for j in seg_jobs:
            w = j.get('when') or {}
            out += [f"### {j['n']}. {prefix(j)}{j['title']}", '',
                    f"**Segment:** {j.get('who', '—')}  ", f"**Basis:** {j.get('basis', '—')}", '']
            if JOB_TYPE.get(j.get('job_type')):
                out += [f"**Job type:** {JOB_TYPE[j['job_type']]}", '']
            out += [
                    '**When:**', f"- **Context:**{val(w.get('context'))}", f"- **Trigger:**{val(w.get('trigger'))}",
                    f"- **Negative emotions:**{val(w.get('neg'))}", f"- **Consideration Set:**{val(w.get('cs'))}", '',
                    f"**{j.get('want', 'Want to —')}**", f"- **{j.get('criteria_label') or 'Success criteria:'}**{val(j.get('criteria'))}", '',
                    f"**So that** {j.get('why', '—')}", f"- **Arrive at positive emotions:**{val(j.get('pos'))}", '']
            ev = j.get('evidence') or []
            if ev:
                out += ['<details><summary>Evidence</summary>', '']
                out += [f"- {e.get('source', '')}: «{e.get('quote', '')}» {e.get('where', '')}".rstrip() for e in ev]
                out += ['', '</details>', '']
            if j.get('fit'):
                lab = {'now': 'covers it now', 'min': 'with minimal extra work', 'none': 'not related'}[j['fit']]
                out += [f"*Product fit: {lab}. {j.get('fit_note', '')}*", '']
        if copies:
            out += ['The same job also belongs to this segment: ' + ', '.join(f"#{j['n']} “{j['title']}”" for j in copies) + '.', '']
    edges = d.get('edges') or []
    if edges:
        by = {j['id']: j for j in jobs}
        out += ['## Links between jobs', '']
        for e in edges:
            a, b = by.get(e['from']), by.get(e['to'])
            if a and b:
                kind = 'then' if e['kind'] == 'seq' else 'for the sake of / part of'
                out.append(f"- {a['n']} → {b['n']} ({kind}): {a['title']} → {b['title']}. Basis: {e.get('basis', '—')}")
        out.append('')
    open(dst, 'w', encoding='utf-8').write('\n'.join(out))
    print(dst)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
