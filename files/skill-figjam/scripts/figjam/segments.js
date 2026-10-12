// ---- action: segments ----
// DATA: { board, batch: [{ segNode, name, intro, jobs: [job], copies: [job] }] }
const out = [];
for (const b of DATA.batch) {
  const seg = await figma.getNodeByIdAsync(b.segNode);
  if (!seg) { out.push({ seg: b.segNode, error: 'segment section not found' }); continue; }
  for (const c of [...seg.children]) c.remove(); // allow safe rebuild of one column
  const head = txt(b.name, 40, BOLD, C.brown, CW);
  seg.appendChild(head); head.x = 60; head.y = 60;
  let y = Math.round(head.y + head.height + 48);
  if (b.intro) {
    const intro = txt(b.intro, 24, REG, C.dark, CW);
    seg.appendChild(intro); intro.x = 60; intro.y = Math.round(head.y + head.height + 16);
    y = Math.round(intro.y + intro.height + 48);
  }
  const cards = [];
  for (const j of b.jobs) { const c = mkCard(seg, j, 60, y, false); cards.push({ n: j.n, id: c.id }); y += c.h + 60; }
  for (const j of (b.copies || [])) { const c = mkCard(seg, j, 60, y, true, b.name); cards.push({ n: j.n, id: c.id, copy: true }); y += c.h + 60; }
  seg.resizeWithoutConstraints(SEGW, y);
  out.push({ seg: seg.id, height: y, cards });
}
// re-fit the board to its content
const board = await figma.getNodeByIdAsync(DATA.board);
if (board) {
  let maxB = 0;
  for (const c of board.children) maxB = Math.max(maxB, c.y + c.height);
  board.resizeWithoutConstraints(board.width, Math.round(maxB + 80));
}
return out;
