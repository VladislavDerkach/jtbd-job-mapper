// ---- action: read (dump the board after the user's manual edits) ----
// DATA: { root: optional node id; default = whole page }
const roots = DATA.root ? [await figma.getNodeByIdAsync(DATA.root)] : [...figma.currentPage.children];
const cards = [], headers = [], connectors = [], other = [];
function headerOf(n) {
  let p = n.parent;
  while (p && p.type !== 'PAGE') {
    if (p.type === 'SECTION') {
      const t = p.children.find(c => c.type === 'TEXT' && c.fontSize >= 36);
      if (t) return t.characters;
    }
    p = p.parent;
  }
  return '';
}
const byId = {};
for (const r of roots) for (const c of findCards(r)) {
  const b = c.node.children.find(x => x.type === 'TEXT');
  const rec = { node: c.node.id, n: c.n, copy: c.copy, title: c.title, seg_box: c.seg, column: headerOf(c.node), body: b ? b.characters.slice(0, 1800) : '' };
  cards.push(rec); byId[c.node.id] = rec;
}
async function resolve(id) {
  if (!id) return null;
  let n = await figma.getNodeByIdAsync(id);
  while (n && !byId[n.id] && n.parent) n = n.parent;
  return n && byId[n.id] ? byId[n.id] : null;
}
(function walk(n) {
  if (n.type === 'CONNECTOR') connectors.push(n);
  else if ((n.type === 'STICKY' || n.type === 'SHAPE_WITH_TEXT') && n.text && n.text.characters) other.push({ type: n.type, text: n.text.characters.slice(0, 300) });
  if ('children' in n && n.type !== 'CONNECTOR') for (const c of n.children) walk(c);
})({ type: 'ROOT', children: roots });
const links = [];
for (const c of connectors) {
  const a = await resolve(c.connectorStart && c.connectorStart.endpointNodeId);
  const b = await resolve(c.connectorEnd && c.connectorEnd.endpointNodeId);
  links.push({
    from: a ? a.n : null, from_copy: a ? a.copy : null, to: b ? b.n : null, to_copy: b ? b.copy : null,
    dashed: !!(c.dashPattern && c.dashPattern.length), start_cap: c.connectorStartStrokeCap, end_cap: c.connectorEndStrokeCap,
  });
}
const columns = [...new Set(cards.map(c => c.column))];
return { columns, cards, links, other };
