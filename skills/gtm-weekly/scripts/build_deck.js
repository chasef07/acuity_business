#!/usr/bin/env node
// Build the GTM weekly deck from a JSON file.
// Usage: NODE_PATH=<dir>/node_modules node build_deck.js deck.json out.pptx
// The JSON shape is shown in ../references/deck-example.json. Optional slides
// (inbound, tracking, demo) are skipped when their key is missing.
// Row limits keep every slide inside its frame; the script exits 1 instead of
// letting text overflow.

const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const [dataPath, outPath] = process.argv.slice(2);
if (!dataPath || !outPath) {
  console.error("usage: build_deck.js deck.json out.pptx");
  process.exit(2);
}
const d = JSON.parse(fs.readFileSync(dataPath, "utf8"));

const LIMITS = { "deals.rows": 5, "inbound.rows": 4, "sprints.current.rows": 7, "sprints.upcoming.rows": 7,
  "channels.cols": 4, "tracking.table.rows": 6, "demo.pillars": 3, "decisions": 6 };
const get = (obj, key) => key.split(".").reduce((o, k) => (o == null ? o : o[k]), obj);
const errors = [];
for (const key of ["date", "cover", "standing", "deals", "sprints", "channels", "decisions"]) {
  if (get(d, key) == null) errors.push(`missing ${key}`);
}
for (const [key, max] of Object.entries(LIMITS)) {
  const v = get(d, key);
  if (Array.isArray(v) && v.length > max) errors.push(`${key} has ${v.length} items; limit is ${max}`);
}
if (errors.length) {
  console.error("deck data invalid:\n- " + errors.join("\n- "));
  process.exit(1);
}

const INK = "080808", PAPER = "F4F2ED", MUTED = "81817B", RULE = "D9D7D0";
const LOGO = path.join(__dirname, "..", "assets", "acuity-mark.png");
const LOGO_AR = 679 / 747;
const W = 13.333, M = 0.6;

const when = new Date(d.date + "T12:00:00");
const LONG = when.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" }).toUpperCase();
const SHORT = when.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }).toUpperCase();

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: "Cambria", bodyFontFace: "Arial" };
pres.title = `GTM Weekly — ${d.date}`;
pres.author = "Acuity Health";

const footer = [
  { image: { path: LOGO, x: M, y: 6.86, w: 0.3 * LOGO_AR, h: 0.3 } },
  { text: { text: `ACUITY HEALTH  ·  GTM WEEKLY  ·  ${SHORT}`, options: {
    x: M + 0.42, y: 6.85, w: 6, h: 0.32, fontSize: 10, charSpacing: 2, margin: 0, valign: "middle", color: MUTED } } },
];
pres.defineSlideMaster({ title: "Cover", background: { color: PAPER }, objects: footer });
pres.defineSlideMaster({
  title: "Content",
  background: { color: PAPER },
  objects: [
    ...footer,
    { placeholder: { options: { name: "kicker", type: "body", x: M, y: 0.5, w: 9, h: 0.35,
      fontSize: 11, bold: true, charSpacing: 3, color: MUTED, margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.85, w: W - 2 * M, h: 0.9,
      fontFace: "Cambria", fontSize: 36, color: INK, margin: 0, valign: "top", align: "left" }, text: "" } },
  ],
  slideNumber: { x: W - M - 0.5, y: 6.85, w: 0.5, h: 0.32, fontSize: 10, color: MUTED, align: "right" },
});

const content = (kicker, title, section) => {
  pres.addSection({ title: section });
  const s = pres.addSlide({ masterName: "Content", sectionTitle: section });
  s.addText(kicker, { placeholder: "kicker" });
  s.addText(title, { placeholder: "title" });
  return s;
};
const txt = (s, text, opts) => s.addText(text, { isTextBox: true, margin: 0, valign: "top", ...opts });
const label = (s, text, x, y, w) => txt(s, text.toUpperCase(), { x, y, w, h: 0.3, fontSize: 11, bold: true, charSpacing: 2, color: MUTED });
const dot = (s, x, y, size) => s.addShape(pres.shapes.OVAL, { x, y, w: size, h: size, fill: { color: INK }, line: { color: INK, width: 1 } });
const chip = (s, text, x, y, w) => {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h: 0.36, fill: { color: INK }, line: { type: "none" } });
  txt(s, text, { x: x + 0.12, y, w: w - 0.24, h: 0.36, fontSize: 11, bold: true, color: PAPER, valign: "middle" });
};
const bullets = (items) => items.map((t, i) => ({ text: t, options: { bullet: { indent: 16 }, breakLine: i < items.length - 1 } }));
const border = (pt, color) => [{ type: "none" }, { type: "none" }, { pt, color }, { type: "none" }];
const head = (t) => ({ text: t.toUpperCase(), options: { bold: true, fontSize: 11, charSpacing: 2, color: MUTED, border: border(1, INK) } });
const cell = (t, bold = false) => ({ text: t, options: { fontSize: 14, bold, color: INK, border: border(0.5, RULE) } });
const table = (s, heads, rows, colW, y = 2.0) => s.addTable(
  [heads.map(head), ...rows.map((r) => r.map((v, i) => cell(v, i === 0)))],
  { x: M, y, w: W - 2 * M, colW, rowH: [0.45, ...rows.map(() => 0.85)], valign: "middle", margin: [4, 8, 4, 0], fontFace: "Arial" });
const note = (s, text) => txt(s, text, { x: M, y: 6.15, w: W - 2 * M, h: 0.4, fontSize: 13, italic: true, color: MUTED });

// Cover
pres.addSection({ title: "Opening" });
{
  const s = pres.addSlide({ masterName: "Cover", sectionTitle: "Opening" });
  s.addImage({ path: LOGO, x: M, y: 0.8, w: 1.5 * LOGO_AR, h: 1.5 });
  txt(s, `GTM WEEKLY  ·  ${LONG}`, { x: M, y: 2.75, w: 8, h: 0.4, fontSize: 12, bold: true, charSpacing: 3, color: MUTED });
  txt(s, d.cover.headline, { x: M, y: 3.25, w: 10, h: 2.2, fontFace: "Cambria", fontSize: 54, color: INK });
  txt(s, d.cover.subhead, { x: M, y: 5.6, w: 9, h: 0.5, fontSize: 18, color: MUTED });
}

// Where we stand
{
  const st = d.standing;
  const s = content("WHERE WE STAND", st.title, "Where we stand");
  label(s, "The offer", M, 2.05, 5.6);
  txt(s, st.offer, { x: M, y: 2.45, w: 5.6, h: 2.2, fontFace: "Cambria", fontSize: 22, color: INK });
  txt(s, `Source: ${st.source}`, { x: M, y: 4.75, w: 5.6, h: 0.3, fontSize: 11, color: MUTED });
  const px = 7.1;
  label(s, "Three pillars", px, 2.05, 5.6);
  st.pillars.forEach(([h, b], i) => {
    const y = 2.5 + i * 0.95;
    dot(s, px, y + 0.06, 0.2);
    txt(s, h, { x: px + 0.4, y, w: 5.2, h: 0.35, fontSize: 16, bold: true, color: INK });
    txt(s, b, { x: px + 0.4, y: y + 0.36, w: 5.2, h: 0.5, fontSize: 14, color: INK });
  });
  s.addShape(pres.shapes.RECTANGLE, { x: M, y: 5.45, w: W - 2 * M, h: 1.05, fill: { color: INK }, line: { type: "none" } });
  txt(s, [{ text: "The gap:  ", options: { bold: true } }, { text: st.gap }],
    { x: M + 0.3, y: 5.6, w: W - 2 * M - 0.6, h: 0.8, fontSize: 15, color: PAPER, valign: "middle" });
}

// Deals
{
  const s = content("ACTIVE DEALS", d.deals.title, "Deals");
  table(s, ["Account", "Where it stands", "Next step", "Owner", "By"],
    d.deals.rows.map((r) => [r.account, r.stands, r.next, r.owner, r.by]), [2.4, 3.3, 4.2, 1.0, 1.233]);
  if (d.deals.note) note(s, d.deals.note);
}

// Sprints
{
  const s = content("LINEAR  ·  SALES", "This week and next", "Sprints");
  const col = (x, sp) => {
    txt(s, sp.label, { x, y: 2.0, w: 5.7, h: 0.4, fontFace: "Cambria", fontSize: 22, color: INK });
    txt(s, sp.dates, { x, y: 2.42, w: 5.7, h: 0.3, fontSize: 12, color: MUTED });
    sp.rows.forEach(([id, title, status], i) => {
      const y = 2.95 + i * 0.52;
      s.addShape(pres.shapes.LINE, { x, y: y - 0.06, w: 5.7, h: 0, line: { color: RULE, width: 0.75 } });
      txt(s, id, { x, y, w: 0.85, h: 0.45, fontSize: 12, bold: true, color: INK, valign: "middle" });
      txt(s, title, { x: x + 0.85, y, w: 3.35, h: 0.45, fontSize: 13, color: INK, valign: "middle" });
      txt(s, status, { x: x + 4.2, y, w: 1.5, h: 0.45, fontSize: 11, color: MUTED, align: "right", valign: "middle" });
    });
  };
  col(M, { label: "Current sprint", ...d.sprints.current });
  col(6.95, { label: "Upcoming sprint", ...d.sprints.upcoming });
  if (d.sprints.notes) s.addNotes(d.sprints.notes);
}

// Inbound outside the ICP
if (d.inbound) {
  const s = content("INBOUND  ·  OUTSIDE THE ICP", d.inbound.title, "Inbound");
  table(s, ["Account", "Where it stands", "Next step", "By"],
    d.inbound.rows.map((r) => [r.account, r.stands, r.next, r.by]), [2.8, 2.9, 4.6, 1.833]);
  if (d.inbound.callout) {
    const by = 5.35, bw = 6.4;
    s.addShape(pres.shapes.RECTANGLE, { x: M, y: by, w: bw, h: 1.0, fill: { color: INK }, line: { type: "none" } });
    txt(s, d.inbound.callout.label.toUpperCase(), { x: M + 0.35, y: by + 0.18, w: bw - 0.7, h: 0.28, fontSize: 10, bold: true, charSpacing: 2, color: MUTED });
    txt(s, d.inbound.callout.text, { x: M + 0.35, y: by + 0.48, w: bw - 0.7, h: 0.4, fontFace: "Cambria", fontSize: 20, color: PAPER });
  }
}

// Channels
{
  const s = content("HOW WE FIND CUSTOMERS", d.channels.title, "Channels");
  const n = d.channels.cols.length, gap = 0.35, cw = (W - 2 * M - (n - 1) * gap) / n;
  d.channels.cols.forEach((c, i) => {
    const x = M + i * (cw + gap);
    txt(s, c.name, { x, y: 2.0, w: cw, h: 0.5, fontFace: "Cambria", fontSize: 22, color: INK });
    chip(s, c.ticket, x, 2.55, cw);
    txt(s, c.tag.toUpperCase(), { x, y: 3.08, w: cw, h: 0.3, fontSize: 10, bold: true, charSpacing: 2, color: MUTED });
    txt(s, c.body, { x, y: 3.45, w: cw, h: 1.5, fontSize: 14, color: INK });
    s.addShape(pres.shapes.LINE, { x, y: 5.1, w: cw, h: 0, line: { color: INK, width: 1 } });
    txt(s, [{ text: "Measure  ", options: { bold: true } }, { text: c.measure }], { x, y: 5.2, w: cw, h: 0.6, fontSize: 13, color: INK });
  });
  if (d.channels.note) txt(s, d.channels.note, { x: M, y: 6.2, w: W - 2 * M, h: 0.4, fontSize: 13, italic: true, color: MUTED });
}

// Tracking
if (d.tracking) {
  const t = d.tracking;
  const s = content("TRACKING", t.title, "Tracking");
  txt(s, t.target, { x: M, y: 1.95, w: 3.2, h: 1.5, fontFace: "Cambria", fontSize: 96, color: INK });
  txt(s, t.targetLabel, { x: M, y: 3.45, w: 3.2, h: 0.4, fontSize: 18, bold: true, color: INK });
  txt(s, t.targetBody, { x: M, y: 3.9, w: 3.2, h: 0.9, fontSize: 14, color: INK });
  if (t.questions) txt(s, t.questions, { x: M, y: 4.85, w: 3.2, h: 1.0, fontSize: 13, italic: true, color: MUTED });
  const tx = 4.4, tw = W - M - tx;
  label(s, t.table.label, tx, 2.0, tw);
  const cols = t.table.columns;
  // Size each column to its header so long headers do not wrap.
  const first = 2.6, widths = cols.slice(1).map((c) => Math.max(c.length, 6));
  const scale = (tw - first) / widths.reduce((a, b) => a + b, 0);
  const sm = (v, i) => ({ text: v, options: { fontSize: 13, bold: i === 0, color: v === "—" ? MUTED : INK, align: i === 0 ? "left" : "center", border: border(0.5, RULE) } });
  const sh = (v) => ({ text: v.toUpperCase(), options: { bold: true, fontSize: 10, charSpacing: 1, color: MUTED, border: border(1, INK) } });
  s.addTable([cols.map(sh), ...t.table.rows.map((r) => r.map(sm))],
    { x: tx, y: 2.4, w: tw, colW: [first, ...widths.map((w) => w * scale)], rowH: 0.48, valign: "middle", margin: [3, 6, 3, 0], fontFace: "Arial" });
  if (t.note) txt(s, t.note, { x: tx, y: 5.45, w: tw, h: 0.4, fontSize: 12, color: MUTED });
  if (t.ticket) chip(s, t.ticket, M, 6.15, W - 2 * M);
}

// Demo
if (d.demo) {
  const dm = d.demo;
  const s = content(dm.kicker, dm.title, "Demo");
  if (dm.subtitle) txt(s, dm.subtitle, { x: M, y: 1.72, w: W - 2 * M, h: 0.4, fontSize: 16, color: MUTED });
  const sw = 3.75, gap = 0.415;
  dm.pillars.forEach(([h, b], i) => {
    const x = M + i * (sw + gap);
    dot(s, x, 2.4, 0.3);
    if (i < dm.pillars.length - 1) s.addShape(pres.shapes.LINE, { x: x + 0.3, y: 2.55, w: sw + gap - 0.3, h: 0, line: { color: INK, width: 1.25 } });
    txt(s, h, { x, y: 2.9, w: sw - 0.2, h: 0.5, fontFace: "Cambria", fontSize: 22, color: INK });
    txt(s, b, { x, y: 3.42, w: sw - 0.2, h: 1.0, fontSize: 15, color: INK });
  });
  label(s, "Rules", M, 4.6, 5);
  txt(s, bullets(dm.rules), { x: M, y: 4.95, w: 6.2, h: 1.05, fontSize: 14, color: INK, paraSpaceAfter: 4 });
  label(s, "In the room", 7.1, 4.6, 5);
  txt(s, bullets(dm.room), { x: 7.1, y: 4.95, w: 5.6, h: 1.05, fontSize: 14, color: INK, paraSpaceAfter: 4 });
  if (dm.ticket) chip(s, dm.ticket, M, 6.15, W - 2 * M);
}

// Decisions
pres.addSection({ title: "Decisions" });
{
  const s = pres.addSlide({ masterName: "Cover", sectionTitle: "Decisions" });
  txt(s, "DECISIONS TODAY", { x: M, y: 0.6, w: 8, h: 0.4, fontSize: 12, bold: true, charSpacing: 3, color: MUTED });
  txt(s, "Leave with an owner and a date for each", { x: M, y: 1.05, w: 11, h: 0.9, fontFace: "Cambria", fontSize: 36, color: INK });
  d.decisions.forEach(([h, b], i) => {
    const y = 2.2 + i * 0.72;
    s.addShape(pres.shapes.LINE, { x: M, y: y - 0.1, w: W - 2 * M, h: 0, line: { color: RULE, width: 0.75 } });
    txt(s, String(i + 1).padStart(2, "0"), { x: M, y, w: 0.7, h: 0.5, fontFace: "Cambria", fontSize: 22, color: MUTED });
    txt(s, h, { x: M + 0.8, y: y + 0.04, w: 2.7, h: 0.5, fontSize: 18, bold: true, color: INK });
    txt(s, b, { x: M + 3.6, y: y + 0.06, w: 8.5, h: 0.5, fontSize: 16, color: INK });
  });
}

pres.writeFile({ fileName: outPath }).then(() => console.log("wrote", outPath));
