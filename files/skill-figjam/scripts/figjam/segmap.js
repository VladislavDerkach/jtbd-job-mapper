// ---- action: segmap ----
// DATA: { title, notes: [str], legend: [[kind,label]], cards: [{price, compete, cap, title, steps:[[kind,text]]}] }
const COLW = 640, CG = 40, COLS = 4, W = 80 + COLS * COLW + (COLS - 1) * CG + 80;
function row(kind, text, tw) {
  const r = figma.createAutoLayout('HORIZONTAL');
  r.fills = []; r.itemSpacing = 20; r.counterAxisAlignItems = 'CENTER';
  r.appendChild(dot(kind)); r.appendChild(txt(text, 28, REG, C.soft, tw));
  return r;
}
function column(steps, cw) {
  const col = figma.createAutoLayout('VERTICAL');
  col.fills = []; col.itemSpacing = 22;
  col.resize(cw, 10); col.primaryAxisSizingMode = 'AUTO'; col.counterAxisSizingMode = 'FIXED';
  for (const [k, t] of steps) col.appendChild(row(k, t, cw - 56));
  return col;
}
function segCard(sec, s, w, span) {
  const f = figma.createAutoLayout('VERTICAL');
  sec.appendChild(f);
  f.resize(w, 100); f.primaryAxisSizingMode = 'AUTO'; f.counterAxisSizingMode = 'FIXED';
  f.paddingLeft = 40; f.paddingRight = 40; f.paddingTop = 36; f.paddingBottom = 44; f.itemSpacing = 22; f.cornerRadius = 44;
  if (s.compete) { f.fills = [{ type: 'SOLID', color: C.beige }]; f.strokes = []; }
  else { f.fills = [{ type: 'SOLID', color: C.white }]; f.strokes = [{ type: 'SOLID', color: C.beigeLine }]; f.strokeWeight = 4; }
  const hdr = figma.createAutoLayout('HORIZONTAL');
  f.appendChild(hdr); hdr.fills = []; hdr.layoutSizingHorizontal = 'FILL';
  hdr.primaryAxisAlignItems = 'SPACE_BETWEEN'; hdr.counterAxisAlignItems = 'CENTER';
  hdr.appendChild(txt(s.price || '?', 48, REG, h(160, 110, 50)));
  const badge = figma.createAutoLayout('HORIZONTAL'); hdr.appendChild(badge);
  badge.paddingLeft = 26; badge.paddingRight = 26; badge.paddingTop = 10; badge.paddingBottom = 10; badge.cornerRadius = 40;
  badge.fills = [{ type: 'SOLID', color: C.white }];
  if (!s.compete) { badge.strokes = [{ type: 'SOLID', color: h(200, 200, 200) }]; badge.strokeWeight = 2; }
  badge.appendChild(txt(s.compete ? 'Competing' : 'Not competing', 24, MED, s.compete ? h(47, 47, 47) : h(130, 130, 130)));
  f.appendChild(txt(s.cap, 22, REG, h(138, 122, 102), w - 80));
  f.appendChild(txt(s.title, 38, MED, h(47, 47, 47), w - 80));
  if (span === 2) {
    const wrap = figma.createAutoLayout('HORIZONTAL'); wrap.fills = []; wrap.itemSpacing = 40; wrap.counterAxisAlignItems = 'MIN';
    f.appendChild(wrap);
    const cw = (w - 80 - 40) / 2, half = Math.ceil(s.steps.length / 2);
    wrap.appendChild(column(s.steps.slice(0, half), cw)); wrap.appendChild(column(s.steps.slice(half), cw));
  } else f.appendChild(column(s.steps, w - 80));
  return f;
}
const sec = figma.createSection(); sec.name = '';
sec.resizeWithoutConstraints(W, 4000);
sec.fills = [{ type: 'SOLID', color: C.white }];
sec.x = rightmostX(); sec.y = 0;
const title = txt(DATA.title || 'Segment map', 72, BOLD, C.brown);
sec.appendChild(title); title.x = 80; title.y = 80;
const notes = txt((DATA.notes || []).join('\n') || ' ', 26, REG, C.soft, W - 240);
sec.appendChild(notes); notes.x = 80; notes.y = title.y + title.height + 24;
const lg = figma.createAutoLayout('HORIZONTAL'); lg.fills = []; lg.itemSpacing = 64; lg.counterAxisAlignItems = 'CENTER';
sec.appendChild(lg);
for (const [k, t] of DATA.legend) {
  const it = figma.createAutoLayout('HORIZONTAL'); it.fills = []; it.itemSpacing = 16; it.counterAxisAlignItems = 'CENTER';
  it.appendChild(dot(k)); it.appendChild(txt(t, 28, REG, C.dark)); lg.appendChild(it);
}
lg.x = 80; lg.y = Math.round(notes.y + notes.height + 40);
// pack cards into rows of COLS columns; long lists take 2 columns
const rows = []; let cur = [], used = 0;
for (const s of DATA.cards) {
  const span = s.steps.length > 6 ? 2 : 1;
  if (used + span > COLS) { rows.push(cur); cur = []; used = 0; }
  cur.push({ s, span, col: used }); used += span;
}
if (cur.length) rows.push(cur);
let y = Math.round(lg.y + lg.height + 80);
for (const r of rows) {
  const nodes = r.map(it => { const w = it.span * COLW + (it.span - 1) * CG; return { it, w, node: segCard(sec, it.s, w, it.span) }; });
  const rh = Math.max(...nodes.map(n => n.node.height));
  for (const n of nodes) {
    n.node.primaryAxisSizingMode = 'FIXED'; n.node.resize(n.w, rh);
    n.node.x = 80 + n.it.col * (COLW + CG); n.node.y = y;
  }
  y += rh + CG;
}
sec.resizeWithoutConstraints(W, Math.round(y - CG + 80));
return { segmap: sec.id, width: W, height: sec.height };
