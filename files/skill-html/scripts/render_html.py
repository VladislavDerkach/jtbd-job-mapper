#!/usr/bin/env python3
"""Render work/jobs.json into ONE self-contained HTML file: job cards in segment
columns, the job graph drawn over them, and the Next Move Theory segment map.

Usage:
  render_html.py JOBS OUT.html [--open] [--no-graph] [--no-segmap] [--only SEG_ID ...]

The output has no external dependencies: no CDN, no fonts, no network. Edges are
drawn client-side with SVG after layout, so nothing has to be positioned by hand.
"""
import argparse, html, json, os, subprocess, sys, webbrowser

AI = '[AI-ASSUMPTION]'

CSS = """
:root{
  --dark:#1e1e1e; --brown:#a9702f; --soft:#5f554b; --orange:#d66400;
  --seq:#e07b00; --part:#0e8fa8; --same:#969696;
  --blue-f:#90def0; --blue-t:#004658; --green-f:#aaf0b9; --green-t:#006000;
  --gray-f:#eeeeee; --gray-t:#1e1e1e; --alt-f:#e2d6ff; --alt-t:#46288c;
  --beige:#f3e3c8; --beige-line:#c9b79c; --dot:#7ed0e8; --dot-light:#d6eff7;
  --page:#fbfaf8; --card:#ffffff; --line:#e3ded6;
}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--dark);
  font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--part)}
h1{font-size:30px;line-height:1.25;color:var(--brown);margin:0 0 14px}
h2{font-size:21px;margin:0 0 10px}
.wrap{padding:28px 32px 80px}
.legend{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 20px;margin:0 0 20px}
.legend ul{margin:8px 0 0;padding-left:22px}
.legend li{margin:4px 0}
.counts{color:var(--soft);font-size:13px;margin-top:10px}

/* ---- controls ---- */
.bar{position:sticky;top:0;z-index:30;background:rgba(251,250,248,.94);backdrop-filter:blur(6px);
  border-bottom:1px solid var(--line);padding:10px 32px;margin:0 -32px 22px;
  display:flex;gap:18px;align-items:center;flex-wrap:wrap}
.bar label{display:inline-flex;gap:6px;align-items:center;font-size:13px;cursor:pointer;white-space:nowrap}
.bar input[type=search]{font:inherit;font-size:13px;padding:5px 9px;border:1px solid var(--line);
  border-radius:8px;min-width:230px;background:#fff}
.swatch{width:26px;height:0;border-top-width:3px;border-top-style:solid;display:inline-block}
.sw-seq{border-color:var(--seq)} .sw-part{border-color:var(--part);border-top-style:dashed}
.sw-same{border-color:var(--same);border-top-style:dotted}
.btn{font:inherit;font-size:13px;padding:5px 11px;border:1px solid var(--line);background:#fff;
  border-radius:8px;cursor:pointer}
.btn:hover{border-color:var(--brown)}

/* ---- board ---- */
#board{position:relative}
#edges{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:1;overflow:visible}
.cols{display:flex;gap:28px;align-items:flex-start;position:relative;z-index:2}
.col{flex:0 0 440px;min-width:0;background:#f5fbff;border:1px solid var(--line);border-radius:14px;padding:16px}
.col:nth-child(8n+2){background:#fffbf0} .col:nth-child(8n+3){background:#ebffee}
.col:nth-child(8n+4){background:#f8f5ff} .col:nth-child(8n+5){background:#fff7f0}
.col:nth-child(8n+6){background:#f1fefd} .col:nth-child(8n+7){background:#fafaf0}
.col:nth-child(8n+0){background:#fff2f7}
.col > h2{color:var(--brown);font-size:18px}
.col-intro{font-size:13px;color:var(--soft);margin:0 0 14px}

.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px;margin:0 0 16px;
  scroll-margin-top:90px;transition:box-shadow .12s,border-color .12s,opacity .12s}
.card:hover{box-shadow:0 2px 14px rgba(0,0,0,.07)}
.card.sel{border-color:var(--brown);box-shadow:0 0 0 2px rgba(169,112,47,.25)}
.card.dim{opacity:.22}
.card.hide{display:none}
.chip{border-radius:18px;padding:9px 14px;margin:0 0 9px;font-size:13px}
.chip b{font-weight:700}
.c-title{background:var(--blue-f);color:var(--blue-t);font-size:16px;font-weight:700}
.c-seg{background:var(--green-f);color:var(--green-t)}
.c-basis{background:var(--gray-f);color:var(--gray-t)}
.c-alt{background:var(--alt-f);color:var(--alt-t);font-weight:700}
.tags{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 9px}
.tag{font-size:11px;text-transform:uppercase;letter-spacing:.04em;padding:3px 8px;border-radius:20px;
  border:1px solid var(--line);color:var(--soft);background:#fff}
.tag.tax{border-color:#d08a00;color:#8a5a00;background:#fff6e2}
.tag.fake{border-color:#c23c3c;color:#9b2a2a;background:#ffeeee}
.tag.emotional{border-color:#8a4fd0;color:#5c2f94;background:#f4eeff}
.tag.orientation{border-color:#2f8fd0;color:#1d5c88;background:#eaf5fd}
.tag.viral{border-color:#2f9b6a;color:#1c6646;background:#eafaf2}
.tag.fit-now{border-color:var(--dot);background:var(--dot);color:#00323f}
.tag.fit-min{border-color:var(--dot);background:var(--dot-light);color:#00323f}
.body{font-size:13.5px}
.body .h{font-weight:700;margin:11px 0 3px}
.body ul{margin:2px 0 0;padding-left:20px}
.body ul ul{padding-left:18px}
.body li{margin:2px 0}
.ai{color:var(--orange)}
details.ev{margin-top:10px;font-size:12.5px;color:var(--soft)}
details.ev summary{cursor:pointer}
details.ev ul{padding-left:20px;margin:6px 0 0}
.rel{margin-top:10px;font-size:12.5px;color:var(--soft)}

/* ---- segment map ---- */
.map{margin-top:46px;padding-top:26px;border-top:1px solid var(--line)}
.mapgrid{display:flex;gap:22px;flex-wrap:wrap;align-items:flex-start}
.mcard{flex:0 0 400px;border:1px solid var(--beige-line);border-radius:14px;padding:18px;background:#fff}
.mcard.compete{background:var(--beige)}
.price{font-size:22px;font-weight:700;letter-spacing:.06em;color:var(--brown)}
.badge{display:inline-block;margin:8px 0;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:700;
  background:#fff;border:1px solid var(--beige-line)}
.mcard.compete .badge{background:var(--brown);color:#fff;border-color:var(--brown)}
.msmall{font-size:12px;color:var(--soft);margin:2px 0 8px}
.mgoal{font-size:16px;font-weight:700;margin:0 0 12px}
.mlist{list-style:none;margin:0;padding:0;font-size:13px}
.mlist li{display:flex;gap:9px;align-items:flex-start;margin:6px 0}
.o{flex:0 0 14px;width:14px;height:14px;border-radius:50%;margin-top:3px;box-sizing:border-box}
.o-now{background:var(--dot);border:1px solid var(--dot)}
.o-min{background:var(--dot-light);border:2px solid var(--dot)}
.o-none{background:#fff;border:1.5px solid #767676}
.foot{margin-top:30px;font-size:12px;color:var(--soft)}
@media print{.bar{display:none} .card{break-inside:avoid}}
"""

JS = r"""
const EDGES = __EDGES__;
const state = {seq:true, part:true, same:true, sel:null};

function cardEl(jid, seg){ return document.getElementById('card-'+jid+'--'+seg); }
function anchors(el, box){
  const r = el.getBoundingClientRect();
  return {l:r.left-box.left, t:r.top-box.top, w:r.width, h:r.height,
          cx:r.left-box.left+r.width/2, cy:r.top-box.top+r.height/2};
}
function path(a, b, kind){
  const sameCol = Math.abs(a.cx-b.cx) < 8;
  if (sameCol){
    const near = Math.abs(a.cy-b.cy) < a.h/2 + b.h/2 + 60;
    if (near){
      const down = a.cy < b.cy;
      const y1 = down ? a.t+a.h : a.t, y2 = down ? b.t : b.t+b.h;
      const m = (y1+y2)/2;
      return 'M '+a.cx+' '+y1+' C '+a.cx+' '+m+', '+b.cx+' '+m+', '+b.cx+' '+y2;
    }
    const right = kind === 'part';
    const x = right ? Math.max(a.l+a.w, b.l+b.w)+18 : Math.min(a.l, b.l)-18;
    const ax = right ? a.l+a.w : a.l, bx = right ? b.l+b.w : b.l;
    return 'M '+ax+' '+a.cy+' C '+x+' '+a.cy+', '+x+' '+b.cy+', '+bx+' '+b.cy;
  }
  const ltr = a.cx < b.cx;
  const ax = ltr ? a.l+a.w : a.l, bx = ltr ? b.l : b.l+b.w;
  const mx = (ax+bx)/2;
  return 'M '+ax+' '+a.cy+' C '+mx+' '+a.cy+', '+mx+' '+b.cy+', '+bx+' '+b.cy;
}
function draw(){
  const board = document.getElementById('board');
  const svg = document.getElementById('edges');
  if (!svg) return;
  const box = board.getBoundingClientRect();
  svg.setAttribute('viewBox', '0 0 '+box.width+' '+box.height);
  svg.setAttribute('width', box.width); svg.setAttribute('height', box.height);
  const defs = svg.querySelector('defs');
  while (svg.lastChild && svg.lastChild !== defs) svg.removeChild(svg.lastChild);
  for (const e of EDGES){
    if (!state[e.kind]) continue;
    const A = cardEl(e.from, e.fseg), B = cardEl(e.to, e.tseg);
    if (!A || !B) continue;
    if (A.classList.contains('hide') || B.classList.contains('hide')) continue;
    if (state.sel && e.from !== state.sel && e.to !== state.sel) continue;
    const p = document.createElementNS('http://www.w3.org/2000/svg','path');
    p.setAttribute('d', path(anchors(A,box), anchors(B,box), e.kind));
    p.setAttribute('fill','none');
    p.setAttribute('stroke', e.kind==='seq' ? 'var(--seq)' : e.kind==='part' ? 'var(--part)' : 'var(--same)');
    p.setAttribute('stroke-width', e.kind==='same' ? '2' : '2.5');
    if (e.kind==='part') p.setAttribute('stroke-dasharray','9 7');
    if (e.kind==='same') p.setAttribute('stroke-dasharray','2 6');
    if (e.kind!=='same') p.setAttribute('marker-end','url(#ar-'+e.kind+')');
    p.setAttribute('opacity', state.sel ? '0.95' : '0.6');
    const t = document.createElementNS('http://www.w3.org/2000/svg','title');
    t.textContent = e.label; p.appendChild(t);
    svg.appendChild(p);
  }
}
function select(jid, n){
  state.sel = (state.sel === jid) ? null : jid;
  const keep = new Set();
  if (state.sel){
    keep.add(state.sel);
    for (const e of EDGES){
      if (!state[e.kind]) continue;
      if (e.from === state.sel) keep.add(e.to);
      if (e.to === state.sel) keep.add(e.from);
    }
  }
  document.querySelectorAll('.card').forEach(function(c){
    c.classList.toggle('sel', state.sel === c.dataset.job);
    c.classList.toggle('dim', !!state.sel && !keep.has(c.dataset.job));
  });
  document.getElementById('selinfo').textContent =
    state.sel ? 'showing only the links of job #'+n : '';
  draw();
}
function filter(q){
  q = q.trim().toLowerCase();
  document.querySelectorAll('.card').forEach(function(c){
    c.classList.toggle('hide', !!q && c.innerText.toLowerCase().indexOf(q) === -1);
  });
  draw();
}
document.addEventListener('DOMContentLoaded', function(){
  document.querySelectorAll('.card').forEach(function(c){
    c.addEventListener('click', function(ev){
      if (ev.target.closest('a, summary, details')) return;
      select(c.dataset.job, c.dataset.n);
    });
  });
  ['seq','part','same'].forEach(function(k){
    const el = document.getElementById('t-'+k);
    if (el) el.addEventListener('change', function(){ state[k] = el.checked; draw(); });
  });
  const s = document.getElementById('q');
  if (s) s.addEventListener('input', function(){ filter(s.value); });
  const r = document.getElementById('reset');
  if (r) r.addEventListener('click', function(){
    state.sel = null; if (s) s.value = '';
    document.querySelectorAll('.card').forEach(function(c){ c.classList.remove('sel','dim','hide'); });
    document.getElementById('selinfo').textContent = '';
    draw();
  });
  draw();
  window.addEventListener('resize', draw);
  document.querySelectorAll('details').forEach(function(d){ d.addEventListener('toggle', draw); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(draw);
});
"""

JT = {'regular': 'regular', 'orientation': 'orientation', 'tax': 'Tax Job',
      'fake': 'Fake Job', 'emotional': 'emotional', 'viral': 'viral'}
FIT = {'now': 'covers it now', 'min': 'with minimal extra work', 'none': "doesn't cover it"}


def e(s):
    """Escape, then paint the AI marker orange."""
    t = html.escape('—' if s is None or s == '' else str(s))
    return t.replace(html.escape(AI), '<span class="ai">' + html.escape(AI) + '</span>')


def bullets(v):
    if isinstance(v, list):
        return '<ul>' + ''.join('<li>' + e(x) + '</li>' for x in v) + '</ul>'
    return ' ' + e(v)


def card(j, segs, rel=None, as_copy_of=None):
    cid = 'card-' + j['id'] + '--' + (as_copy_of or j['segment'])
    o = ['<div class="card" id="' + cid + '" data-job="' + html.escape(j['id']) + '" '
         'data-seg="' + html.escape(as_copy_of or j['segment']) + '" '
         'data-n="' + str(j.get('n', '')) + '">']
    pre = ('Business job: ' if j.get('type') == 'b2b-business'
           else "Decision-maker's personal job: " if j.get('type') == 'b2b-personal' else '')
    o.append('<div class="chip c-title">' + str(j.get('n', '')) + '. ' + e(pre + j['title']) + '</div>')
    jt = j.get('job_type', 'regular')
    tags = ['<span class="tag ' + jt + '">' + JT.get(jt, jt) + '</span>']
    if j.get('fit'):
        tags.append('<span class="tag fit-' + j['fit'] + '">product: ' + FIT[j['fit']] + '</span>')
    o.append('<div class="tags">' + ''.join(tags) + '</div>')
    who = segs[as_copy_of]['name'] if as_copy_of else j.get('who')
    o.append('<div class="chip c-seg"><b>Segment:</b> ' + e(who) + '</div>')
    o.append('<div class="chip c-basis"><b>Basis:</b> ' + e(j.get('basis')) + '</div>')
    if as_copy_of:
        o.append('<div class="chip c-alt">Alternative User Segment</div>')
    w = j.get('when') or {}
    o.append('<div class="body">')
    o.append('<div class="h">When:</div><ul>'
             '<li><b>Context:</b>' + bullets(w.get('context')) + '</li>'
             '<li><b>Trigger:</b>' + bullets(w.get('trigger')) + '</li>'
             '<li><b>Negative emotions:</b>' + bullets(w.get('neg')) + '</li>'
             '<li><b>Consideration Set:</b>' + bullets(w.get('cs')) + '</li></ul>')
    o.append('<div class="h">' + e(j.get('want')) + '</div><ul>'
             '<li><b>' + e(j.get('criteria_label') or 'Success criteria') + ':</b>'
             + bullets(j.get('criteria')) + '</li></ul>')
    o.append('<div class="h">So that ' + e(j.get('why')) + '</div><ul>'
             '<li><b>Arrive at positive emotions:</b> ' + e(j.get('pos')) + '</li></ul>')
    if j.get('fit_note'):
        o.append('<div class="h">Product fit</div><ul><li>' + e(j['fit_note']) + '</li></ul>')
    o.append('</div>')
    if j.get('evidence'):
        o.append('<details class="ev"><summary>Evidence (' + str(len(j['evidence'])) + ')</summary><ul>'
                 + ''.join('<li>' + e(v.get('source')) + ': «' + e(v.get('quote')) + '» — '
                           + e(v.get('where')) + '</li>' for v in j['evidence']) + '</ul></details>')
    if rel:
        o.append('<div class="rel"><b>Links:</b> ' + '; '.join(e(x) for x in rel) + '</div>')
    o.append('</div>')
    return ''.join(o)


def relations(d, byid):
    """Human-readable neighbour lists, keyed by job id."""
    out = {}
    for ed in d.get('edges', []):
        a, b = byid.get(ed['from']), byid.get(ed['to'])
        if not a or not b:
            continue
        k = 'for the sake of / part of' if ed['kind'] == 'part' else 'then'
        out.setdefault(a['id'], []).append(k + ' → #' + str(b.get('n')) + ' ' + b['title'])
        out.setdefault(b['id'], []).append(
            ('from it' if ed['kind'] == 'part' else 'before it') + ' ← #' + str(a.get('n')) + ' ' + a['title'])
    return out


def segmap(d):
    strict = bool(d['project'].get('strict_two_states'))
    cards = []
    for s in sorted(d['segments'], key=lambda x: (not x.get('compete'), x.get('n', 999))):
        jobs = [j for j in d['jobs']
                if j['segment'] == s['id'] or s['id'] in (j.get('also_segments') or [])]
        jobs.sort(key=lambda j: j.get('n', 999))
        items = []
        for j in jobs:
            f = j.get('fit') or 'none'
            if strict and f == 'min':
                f = 'none'
            items.append('<li><span class="o o-' + f + '"></span><span>#' + str(j.get('n'))
                         + ' ' + e(j['title']) + '</span></li>')
        note = (' <span class="msmall">(' + e(s['goal_basis']) + ')</span>') if s.get('goal_basis') else ''
        cards.append('<div class="mcard ' + ('compete' if s.get('compete') else '') + '">'
                     '<div class="price">' + e(s.get('price') or '—') + '</div>'
                     '<div class="badge">' + ('Competing' if s.get('compete') else 'Not competing') + '</div>'
                     '<div class="msmall">Segment ' + str(s.get('n', '')) + '. ' + e(s['name']) + '</div>'
                     '<div class="mgoal">' + e(s.get('goal') or '—') + note + '</div>'
                     '<ul class="mlist">' + ''.join(items) + '</ul></div>')
    return ('<div class="map"><h2>Segment map, Next Move Theory</h2>'
            '<p class="msmall">Price is the money the customer spends on the whole segment job, '
            'not the product\'s price. A filled circle — the product covers the job now; a light one with a ring — '
            'with minimal extra work; empty — doesn\'t cover it.</p>'
            '<div class="mapgrid">' + ''.join(cards) + '</div></div>')


def build(d, with_graph=True, with_map=True, only=None):
    P = d['project']
    segs = {s['id']: s for s in d['segments']}
    byid = {j['id']: j for j in d['jobs']}
    shown = [s for s in sorted(d['segments'], key=lambda x: x.get('n', 999))
             if not only or s['id'] in only]
    rel = relations(d, byid) if with_graph else {}

    cols = []
    for s in shown:
        jobs = sorted([j for j in d['jobs'] if j['segment'] == s['id']], key=lambda j: j.get('n', 999))
        copies = sorted([j for j in d['jobs'] if s['id'] in (j.get('also_segments') or [])],
                        key=lambda j: j.get('n', 999))
        body = [card(j, segs, rel.get(j['id'])) for j in jobs]
        body += [card(j, segs, rel.get(j['id']), as_copy_of=s['id']) for j in copies]
        intro = '<p class="col-intro">' + e(s['intro']) + '</p>' if s.get('intro') else ''
        cols.append('<section class="col"><h2>Segment ' + str(s.get('n', '')) + '. ' + e(s['name'])
                    + '</h2>' + intro + ''.join(body) + '</section>')

    edges = []
    if with_graph:
        ids = {s['id'] for s in shown}
        for ed in d.get('edges', []):
            a, b = byid.get(ed['from']), byid.get(ed['to'])
            if not a or not b or a['segment'] not in ids or b['segment'] not in ids:
                continue
            edges.append({'from': a['id'], 'to': b['id'], 'fseg': a['segment'], 'tseg': b['segment'],
                          'kind': ed['kind'],
                          'label': '#' + str(a.get('n')) + ' → #' + str(b.get('n')) + ' · '
                                   + ('for the sake of / part of' if ed['kind'] == 'part' else 'then')
                                   + ' · ' + str(ed.get('basis', ''))})
        for j in d['jobs']:
            for sid in (j.get('also_segments') or []):
                if j['segment'] in ids and sid in ids:
                    edges.append({'from': j['id'], 'to': j['id'], 'fseg': j['segment'], 'tseg': sid,
                                  'kind': 'same',
                                  'label': '#' + str(j.get('n')) + ' — the same job in another segment'})

    leg = ''.join('<li>' + e(x) + '</li>' for x in (P.get('legend') or []))
    cnt = {}
    for j in d['jobs']:
        k = j.get('job_type', 'regular')
        cnt[k] = cnt.get(k, 0) + 1
    counts = ('Jobs: ' + str(len(d['jobs'])) + '. Segments: ' + str(len(d['segments']))
              + '. Links: ' + str(len(d.get('edges', []))) + '. Job types: '
              + '; '.join(JT.get(k, k) + ' — ' + str(v)
                          for k, v in sorted(cnt.items(), key=lambda kv: -kv[1])) + '.')
    prod = ''
    if P.get('product'):
        prod = ('<p class="counts"><b>Product:</b> ' + e(P['product'].get('name')) + ' — '
                + e(P['product'].get('state')) + '</p>')

    bar = ''
    svg = ''
    if with_graph:
        bar = ('<div class="bar">'
               '<label><input type="checkbox" id="t-seq" checked><span class="swatch sw-seq"></span>'
               'sequence (seq)</label>'
               '<label><input type="checkbox" id="t-part" checked><span class="swatch sw-part"></span>'
               'level (part)</label>'
               '<label><input type="checkbox" id="t-same" checked><span class="swatch sw-same"></span>'
               'same job in another segment</label>'
               '<input type="search" id="q" placeholder="filter cards by text">'
               '<button class="btn" id="reset">reset</button>'
               '<span class="counts" id="selinfo"></span>'
               '<span class="counts">click a card to see only its links</span></div>')
        svg = ('<svg id="edges"><defs>'
               '<marker id="ar-seq" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
               'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#e07b00"/></marker>'
               '<marker id="ar-part" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
               'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#0e8fa8"/></marker>'
               '</defs></svg>')

    return ('<!doctype html>\n<html lang="ru"><head><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '<title>' + html.escape(P.get('title', 'Jobs')) + '</title>\n'
            '<style>' + CSS + '</style></head><body><div class="wrap">\n'
            '<h1>' + e(P.get('title', 'Jobs')) + '</h1>\n'
            '<div class="legend">'
            '<p>Format: <b>When / Want to / So that</b> (Advanced JTBD + Next Move Theory). '
            '"—" means there is no data. "(hypothesis)" is the research author\'s conclusion. '
            '<span class="ai">' + AI + '</span> is an AI conclusion that needs checking; such text is '
            'colored orange.</p>'
            + ('<ul>' + leg + '</ul>' if leg else '')
            + '<p class="counts">' + counts + '</p>' + prod + '</div>\n'
            + bar
            + '<div id="board">' + svg + '<div class="cols">' + ''.join(cols) + '</div></div>\n'
            + (segmap(d) if with_map else '')
            + '<p class="foot">Rendered by the jtbd-research-to-html skill from work/jobs.json. '
              'The file is self-contained: no external requests, opens from disk, prints to '
              'PDF from the browser.</p>\n</div>\n'
            + '<script>' + JS.replace('__EDGES__', json.dumps(edges, ensure_ascii=False)) + '</script>\n'
            + '</body></html>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('jobs')
    ap.add_argument('out')
    ap.add_argument('--open', action='store_true', help='open the result in a browser')
    ap.add_argument('--no-graph', action='store_true', help='no links, no control bar')
    ap.add_argument('--no-segmap', action='store_true', help='no segment map')
    ap.add_argument('--only', nargs='*', help='only these segments (ids)')
    a = ap.parse_args()
    with open(a.jobs, encoding='utf-8') as f:
        d = json.load(f)
    htm = build(d, with_graph=not a.no_graph, with_map=not a.no_segmap,
                only=set(a.only or []) or None)
    outdir = os.path.dirname(os.path.abspath(a.out))
    if outdir:
        os.makedirs(outdir, exist_ok=True)
    with open(a.out, 'w', encoding='utf-8') as f:
        f.write(htm)
    print(a.out + '  (' + str(len(htm)) + ' chars, ' + str(len(d['jobs'])) + ' jobs, '
          + str(len(d.get('edges', []))) + ' links)')
    if a.open:
        p = os.path.abspath(a.out)
        if sys.platform == 'darwin':
            subprocess.run(['open', p], check=False)
        elif os.name == 'nt':
            os.startfile(p)  # noqa: S606
        else:
            webbrowser.open('file://' + p)
        print('opened in browser')


if __name__ == '__main__':
    main()
