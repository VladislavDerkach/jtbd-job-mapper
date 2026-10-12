#!/usr/bin/env python3
"""Validate work/jobs.json against the skill's rules. Exit code 1 if there are errors.

Usage: validate_jobs.py work/jobs.json
"""
import json, re, sys

TEXT = ['title', 'who', 'basis', 'want', 'why', 'pos']
WHEN = ['context', 'trigger', 'neg', 'cs']
TYPES = {'b2c', 'b2b-business', 'b2b-personal'}
JOB_TYPES = {'regular', 'orientation', 'tax', 'fake', 'emotional', 'viral'}

# Rough infinitive detector for English text: words following "to", plus the
# sentence's own leading verb when there's no "to" (titles and `why` are
# written as a bare infinitive, e.g. "Hand over the boat fast").
TO_VERB = re.compile(r'\bto\s+([a-z]+)\b', re.I)
NOT_VERB_START = {'a', 'an', 'the', 'this', 'that', 'these', 'those', 'my', 'our', 'their',
                   'his', 'her', 'its', 'more', 'better', 'no', 'some', 'all', 'one', 'two',
                   'i', 'you', 'we', 'they', 'he', 'she', 'it'}
STACK = re.compile(r'\s(?:and|then|plus|so that)\s', re.I)
AI_MARK = '[AI-ASSUMPTION]'


def empty(v):
    if v is None:
        return True
    if isinstance(v, str):
        return not v.strip()
    if isinstance(v, list):
        return not v or any(empty(x) for x in v)
    return False


def infinitives(text):
    """Words that look like verbs: everything after "to", plus the leading
    word when the text has no "to" and doesn't start with an obvious
    non-verb (article, pronoun, …)."""
    t = (text or '').strip()
    found = [w.lower() for w in TO_VERB.findall(t)]
    first = re.match(r"[a-zA-Z']+", t)
    if first and first.group(0).lower() not in NOT_VERB_START:
        found.append(first.group(0).lower())
    return found


def main(path):
    d = json.load(open(path, encoding='utf-8'))
    err, warn = [], []
    segs = {s['id'] for s in d.get('segments', [])}
    if len(segs) != len(d.get('segments', [])):
        err.append('duplicate segment ids')
    ids, nums = set(), set()
    for j in d.get('jobs', []):
        jid = j.get('id', '?')
        tag = f"job {jid} (#{j.get('n')})"
        if jid in ids: err.append(f'{tag}: duplicate id')
        ids.add(jid)
        if j.get('n') in nums: warn.append(f'{tag}: duplicate number n (cards will be confused on the board)')
        nums.add(j.get('n'))
        if j.get('segment') not in segs: err.append(f"{tag}: unknown segment {j.get('segment')}")
        for s in j.get('also_segments') or []:
            if s not in segs: err.append(f'{tag}: unknown also_segment {s}')
        if j.get('type', 'b2c') not in TYPES: err.append(f"{tag}: bad type {j.get('type')}")
        if j.get('type') == 'b2b-personal' and not j.get('pair_of'): warn.append(f'{tag}: b2b-personal without pair_of')
        if j.get('job_type') and j['job_type'] not in JOB_TYPES:
            err.append(f"{tag}: bad job_type {j.get('job_type')}; allowed: {', '.join(sorted(JOB_TYPES))}")
        for k in TEXT:
            if empty(j.get(k)): err.append(f'{tag}: field {k} is empty; use "—" when there is no data')
        for k in WHEN:
            if empty((j.get('when') or {}).get(k)): err.append(f'{tag}: when.{k} is empty; use "—"')
        if empty(j.get('criteria')): err.append(f'{tag}: criteria is empty; use "—"')
        # Wording gate: the canon requires "I want to + infinitive", exactly one verb (job-format.md)
        want = (j.get('want') or '').strip()
        if want and want != '—':
            if not want.lower().startswith('i want to'):
                err.append(f'{tag}: want must start with "I want to" ("I want to + infinitive")')
            if re.match(r'^i want (?:there|it|them|him|her)\s', want, re.I):
                err.append(f'{tag}: want is "I want there to be …" — the person performing the job is no '
                           f'longer the subject; reformulate as "I want to + infinitive"')
            inf = infinitives(want)
            if not inf:
                err.append(f'{tag}: want has no infinitive verb; a job is a verb phrase, not a noun phrase')
            elif STACK.search(want):
                warn.append(f'{tag}: want contains "{STACK.search(want).group(0).strip()}" — this may be a '
                            f'stack of jobs ({", ".join(inf)}); split it into levels, move constraints into criteria')
        why = (j.get('why') or '').strip()
        if why and why != '—':
            inf = infinitives(why)
            if not inf:
                warn.append(f'{tag}: why ("So that …") has no infinitive; the higher-level job must itself be a job')
            elif STACK.search(why):
                warn.append(f'{tag}: why contains "{STACK.search(why).group(0).strip()}" — keep one higher-level '
                            f'job, move constraints into criteria')
        if j.get('title') and j['title'] != '—' and not infinitives(j['title']):
            warn.append(f'{tag}: title has no infinitive verb; the job title is a verb phrase without "I want to"')
        if j.get('fit') not in (None, 'now', 'min', 'none'): err.append(f"{tag}: bad fit {j.get('fit')}")
        if not j.get('evidence') and 'AI-ASSUMPTION' not in (j.get('basis') or '').upper() \
                and 'author' not in (j.get('basis') or '').lower():
            warn.append(f'{tag}: no evidence quotes; check that basis explains where the job comes from')
        blob = json.dumps(j, ensure_ascii=False)
        if 'AI-ASSUMPTION' in blob.upper() and AI_MARK not in blob:
            warn.append(f'{tag}: AI assumption without the exact marker {AI_MARK}')
    for p in [j for j in d.get('jobs', []) if j.get('pair_of')]:
        if p['pair_of'] not in ids: err.append(f"job {p['id']}: pair_of {p['pair_of']} not found")
    for e in d.get('edges', []):
        if e.get('kind') not in ('seq', 'part'): err.append(f'edge {e}: kind must be seq or part')
        if e.get('from') not in ids or e.get('to') not in ids: err.append(f'edge {e}: unknown job id')
        if e.get('from') == e.get('to'): err.append(f'edge {e}: self-loop')
    for s in d.get('segments', []):
        if s.get('price') and s['price'].strip('$'): err.append(f"segment {s['id']}: price must be $..$$$$")
    for m in err: print('ERROR  ', m)
    for m in warn: print('WARN   ', m)
    print(f"{len(d.get('segments', []))} segments, {len(d.get('jobs', []))} jobs, {len(d.get('edges', []))} edges; {len(err)} errors, {len(warn)} warnings")
    sys.exit(1 if err else 0)


if __name__ == '__main__':
    main(sys.argv[1])
