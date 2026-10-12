// ---- action: graph ----
// DATA: { board, title, legendAdd, edges: [{from:n, to:n, kind:'seq'|'part'}], same: [n] }
const src = await figma.getNodeByIdAsync(DATA.board);
const clone = src.clone();
clone.x = rightmostX(); clone.y = src.y;
const texts = clone.children.filter(c => c.type === 'TEXT');
if (texts[0]) texts[0].characters = DATA.title;
if (texts[1] && DATA.legendAdd) texts[1].insertCharacters(texts[1].characters.length, '\n' + DATA.legendAdd, 'AFTER');
const cards = findCards(clone);
const primary = {}; const copies = {};
for (const c of cards) { if (c.copy) (copies[c.n] = copies[c.n] || []).push(c.node); else primary[c.n] = c.node; }
const absY = n => n.absoluteBoundingBox.y;
function adjacent(a, b) {
  if (a.parent !== b.parent) return false;
  const sibs = a.parent.children.filter(c => c.type === 'SECTION').sort((p, q) => p.y - q.y);
  return Math.abs(sibs.indexOf(a) - sibs.indexOf(b)) === 1;
}
function connect(A, B, kind) {
  let m1 = 'AUTO', m2 = 'AUTO';
  if (A.parent === B.parent) {
    if (adjacent(A, B)) { if (absY(A) < absY(B)) { m1 = 'BOTTOM'; m2 = 'TOP'; } else { m1 = 'TOP'; m2 = 'BOTTOM'; } }
    else if (kind === 'seq') { m1 = 'LEFT'; m2 = 'LEFT'; } else { m1 = 'RIGHT'; m2 = 'RIGHT'; }
  }
  const c = figma.createConnector();
  c.connectorStart = { endpointNodeId: A.id, magnet: m1 };
  c.connectorEnd = { endpointNodeId: B.id, magnet: m2 };
  c.connectorLineType = 'ELBOWED';
  c.connectorEndStrokeCap = kind === 'same' ? 'NONE' : 'ARROW_LINES';
  c.strokes = [{ type: 'SOLID', color: kind === 'seq' ? C.seq : kind === 'part' ? C.part : C.same }];
  c.strokeWeight = kind === 'same' ? 4 : 6;
  if (kind !== 'seq') c.dashPattern = [16, 12];
  return c;
}
const made = [], missing = [];
for (const e of DATA.edges) {
  const A = primary[e.from], B = primary[e.to];
  if (!A || !B) { missing.push(e); continue; }
  connect(A, B, e.kind); made.push(e.from + '>' + e.to + ':' + e.kind);
}
for (const n of Object.keys(copies)) {
  if (!primary[n]) continue;
  for (const cp of copies[n]) { connect(primary[n], cp, 'same'); made.push(n + '~copy'); }
}
return { graph_board: clone.id, made, missing };
