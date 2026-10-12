// ---- jtbd-research-to-figjam: shared helpers (prepended to every action) ----
// Runs inside Figma MCP `use_figma` (FigJam editor). Top-level await and `return` are allowed there.
const h = (r, g, b) => ({ r: r / 255, g: g / 255, b: b / 255 });
const C = {
  dark: h(30, 30, 30), brown: h(169, 112, 47), white: h(255, 255, 255), soft: h(95, 85, 75),
  orange: h(214, 100, 0), seq: h(224, 123, 0), part: h(14, 143, 168), same: h(150, 150, 150),
  beige: h(243, 227, 200), beigeLine: h(201, 183, 156), dotBlue: h(126, 208, 232), dotLight: h(214, 239, 247),
};
const PAL = {
  blue: { f: h(144, 222, 240), t: h(0, 70, 88) },
  green: { f: h(170, 240, 185), t: h(0, 96, 0) },
  gray: { f: h(238, 238, 238), t: h(30, 30, 30) },
  alt: { f: h(226, 214, 255), t: h(70, 40, 140) },
};
const TINTS = [h(245, 251, 255), h(255, 251, 240), h(235, 255, 238), h(248, 245, 255), h(255, 247, 240), h(241, 254, 253), h(250, 250, 240), h(255, 242, 247)];
const REG = { family: 'Inter', style: 'Regular' }, MED = { family: 'Inter', style: 'Medium' }, BOLD = { family: 'Inter', style: 'Bold' };
await Promise.all([figma.loadFontAsync(REG), figma.loadFontAsync(MED), figma.loadFontAsync(BOLD)]);

// Card geometry
const CW = 1324, PAD = 48, LW = 420, GAP = 48, RW = CW - PAD * 2 - LW - GAP, SEGW = CW + 120, SEGGAP = 92;
const AI_MARK = '[AI';
const ALT_LABEL = 'Alternative User Segment';

function txt(chars, size, font, color, w) {
  const t = figma.createText();
  t.fontName = font; t.fontSize = size; t.characters = chars;
  t.fills = [{ type: 'SOLID', color }];
  if (w) { t.textAutoResize = 'HEIGHT'; t.resize(w, t.height); }
  return t;
}

function rightmostX() {
  let x = null;
  for (const n of figma.currentPage.children) { const r = n.x + n.width; if (x === null || r > x) x = r; }
  return x === null ? 0 : Math.round(x + 600);
}

function box(sec, bold, rest, pal, y, size) {
  const f = figma.createAutoLayout('VERTICAL');
  sec.appendChild(f);
  f.resize(LW, 40); f.primaryAxisSizingMode = 'AUTO'; f.counterAxisSizingMode = 'FIXED';
  f.paddingLeft = 24; f.paddingRight = 24; f.paddingTop = 20; f.paddingBottom = 20;
  f.cornerRadius = 24; f.fills = [{ type: 'SOLID', color: pal.f }];
  const t = txt(bold + rest, size, REG, pal.t, LW - 48);
  if (bold) t.setRangeFontName(0, bold.length, BOLD);
  if (rest.includes(AI_MARK)) t.setRangeFills(bold.length, bold.length + rest.length, [{ type: 'SOLID', color: C.orange }]);
  f.appendChild(t);
  f.x = PAD; f.y = y;
  return f;
}

function jobLines(j) {
  const L = [];
  const bl = (label, v) => {
    if (Array.isArray(v)) { L.push(['b1', label, '']); v.forEach(x => L.push(['b2', '', x])); }
    else L.push(['b1', label, ' ' + (v || '—')]);
  };
  const w = j.when || {};
  L.push(['h', 'When:', '']);
  bl('Context:', w.context); bl('Trigger:', w.trigger); bl('Negative emotions:', w.neg); bl('Consideration Set:', w.cs);
  L.push(['g', '', '']);
  L.push(['h', j.want || 'Want to —', '']);
  bl(j.criteria_label || 'Success criteria:', j.criteria);
  L.push(['g', '', '']);
  L.push(['h', 'So that', ' ' + (j.why || '—')]);
  bl('Arrive at positive emotions:', j.pos);
  return L;
}

function body(ls) {
  let s = ''; const spans = [];
  ls.forEach((L, i) => {
    const b = L[1] || '', r = L[2] || ''; const line = b + r;
    const start = s.length; const last = i === ls.length - 1;
    spans.push({ ty: L[0], start, end: start + line.length + (last ? 0 : 1), bl: b.length, len: line.length, ai: line.includes(AI_MARK) });
    s += line + (last ? '' : '\n');
  });
  const t = txt(s, 20, REG, C.dark, RW);
  for (const sp of spans) {
    if (sp.bl) t.setRangeFontName(sp.start, sp.start + sp.bl, BOLD);
    if (sp.ty === 'b1' || sp.ty === 'b2') {
      t.setRangeListOptions(sp.start, sp.end, { type: 'UNORDERED' });
      t.setRangeIndentation(sp.start, sp.end, sp.ty === 'b1' ? 1 : 2);
    } else {
      t.setRangeListOptions(sp.start, sp.end, { type: 'NONE' });
    }
    if (sp.ai && sp.len > sp.bl) t.setRangeFills(sp.start + sp.bl, sp.start + sp.len, [{ type: 'SOLID', color: C.orange }]);
  }
  return t;
}

function cardTitle(j) {
  const pre = j.type === 'b2b-business' ? 'Business job: ' : j.type === 'b2b-personal' ? "Decision-maker's personal job: " : '';
  return j.n + '. ' + pre + j.title;
}

function mkCard(seg, j, x, y, isCopy, segName) {
  const sec = figma.createSection(); seg.appendChild(sec); sec.name = '';
  sec.resizeWithoutConstraints(CW, 400);
  sec.fills = [{ type: 'SOLID', color: C.white }];
  sec.x = x; sec.y = y;
  const b1 = box(sec, cardTitle(j), '', PAL.blue, PAD, 28);
  const b2 = box(sec, 'Segment:', ' ' + (isCopy ? segName : (j.who || '—')), PAL.green, b1.y + b1.height + 24, 24);
  const b3 = box(sec, 'Basis:', ' ' + (j.basis || '—'), PAL.gray, b2.y + b2.height + 24, 20);
  let bottom = b3.y + b3.height;
  if (isCopy) { const b4 = box(sec, ALT_LABEL, '', PAL.alt, bottom + 24, 20); bottom = b4.y + b4.height; }
  const t = body(jobLines(j)); sec.appendChild(t); t.x = PAD + LW + GAP; t.y = PAD;
  const hg = Math.round(Math.max(bottom, t.y + t.height) + PAD);
  sec.resizeWithoutConstraints(CW, hg);
  return { id: sec.id, h: hg };
}

function dot(kind) {
  let e;
  try { e = figma.createEllipse(); } catch (err) { e = figma.createShapeWithText(); e.shapeType = 'ELLIPSE'; }
  e.resize(36, 36);
  if (kind === 'now') { e.fills = [{ type: 'SOLID', color: C.dotBlue }]; e.strokes = []; }
  else if (kind === 'min') { e.fills = [{ type: 'SOLID', color: C.dotLight }]; e.strokes = [{ type: 'SOLID', color: C.dotBlue }]; e.strokeWeight = 4; }
  else { e.fills = [{ type: 'SOLID', color: C.white }]; e.strokes = [{ type: 'SOLID', color: h(70, 70, 70) }]; e.strokeWeight = 3; }
  return e;
}

// Find job cards under a node: returns [{node, n, copy}]
function findCards(root) {
  const out = [];
  (function walk(n) {
    if (n.type === 'SECTION') {
      const frames = n.children.filter(c => c.type === 'FRAME');
      if (frames.length) {
        const ft = frames.map(f => { const t = f.children.find(c => c.type === 'TEXT'); return t ? t.characters : ''; });
        const num = parseInt(ft[0], 10);
        if (!isNaN(num)) { out.push({ node: n, n: num, copy: ft.includes(ALT_LABEL), title: ft[0], seg: ft[1] || '' }); return; }
      }
    }
    if ('children' in n && n.type !== 'CONNECTOR') for (const c of n.children) walk(c);
  })(root);
  return out;
}
// ---- end of shared helpers ----
