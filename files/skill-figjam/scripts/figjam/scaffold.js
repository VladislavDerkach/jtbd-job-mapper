// ---- action: scaffold ----
// DATA: { title, legend: [str], segments: [{id, n, name}] }
const BW = 80 * 2 + DATA.segments.length * SEGW + (DATA.segments.length - 1) * SEGGAP;
const board = figma.createSection(); board.name = '';
board.resizeWithoutConstraints(BW, 4000);
board.fills = [{ type: 'SOLID', color: C.white }];
board.x = rightmostX(); board.y = 0;
const title = txt(DATA.title, 64, BOLD, C.brown);
board.appendChild(title); title.x = 80; title.y = 80;
let top = title.y + title.height;
if (DATA.legend && DATA.legend.length) {
  const legend = txt(DATA.legend.join('\n'), 24, REG, C.dark, Math.min(3600, BW - 160));
  board.appendChild(legend); legend.x = 80; legend.y = top + 32; top = legend.y + legend.height;
}
top = Math.round(top + 120);
const segments = {};
DATA.segments.forEach((s, i) => {
  const sec = figma.createSection(); board.appendChild(sec); sec.name = '';
  sec.resizeWithoutConstraints(SEGW, 1200);
  sec.fills = [{ type: 'SOLID', color: TINTS[i % TINTS.length] }];
  sec.x = 80 + i * (SEGW + SEGGAP); sec.y = top;
  segments[s.id] = sec.id;
});
return { board: board.id, segments, note: 'Save as work/figjam_state.json together with file_key' };
