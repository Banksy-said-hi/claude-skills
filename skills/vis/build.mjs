#!/usr/bin/env node
// vis build: Markdown (with ```mermaid fences) -> self-contained HTML -> PDF via headless Chrome.
// Usage: node build.mjs <input.md> <output.pdf> [--html <out.html>] [--screenshot <out.png>]
// Fence options:  ```mermaid full level=2   ("full" = whole-page diagram, level = 1|2|3 breadcrumb)
// Every flowchart fence gets vocab.mmd appended. Every H1 section becomes a page; pages that
// contain a diagram get legend.html pinned at the bottom.
// Exit codes: 0 ok, 1 usage/IO error, 2 a mermaid diagram failed to render.

import { readFileSync, writeFileSync, existsSync, mkdtempSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { dirname, join, resolve } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const here = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
if (args.length < 2) {
  console.error("usage: node build.mjs <input.md> <output.pdf> [--html out.html] [--screenshot out.png]");
  process.exit(1);
}
const [mdPath, pdfPath] = args.map((a) => resolve(a));
const opt = (flag) => { const i = args.indexOf(flag); return i >= 0 ? resolve(args[i + 1]) : null; };
const htmlOut = opt("--html");
const shotOut = opt("--screenshot");

const CHROME_CANDIDATES = [
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Chromium.app/Contents/MacOS/Chromium",
  "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
];
const chrome = CHROME_CANDIDATES.find(existsSync);
if (!chrome) { console.error("no Chromium-based browser found in /Applications"); process.exit(1); }

const require = createRequire(import.meta.url);
const markedMod = require(join(here, "vendor", "marked.min.js")); // UMD build
const marked = markedMod.marked || markedMod;
const mermaidJs = readFileSync(join(here, "vendor", "mermaid.min.js"), "utf8");
const css = readFileSync(join(here, "style.css"), "utf8");
const vocab = readFileSync(join(here, "vocab.mmd"), "utf8");
const legend = readFileSync(join(here, "legend.html"), "utf8");
const md = readFileSync(mdPath, "utf8");

const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

// ```mermaid [full] [level=N]  ->  <pre class="mermaid" data-full data-level>
const renderer = new marked.Renderer();
const defaultCode = renderer.code.bind(renderer);
renderer.code = function (token) {
  const words = (token.lang || "").trim().split(/\s+/);
  if (words[0] !== "mermaid") return defaultCode(token);
  const size = words.includes("full") ? "full" : words.includes("short") ? "short" : "";
  const lvl = (words.find((w) => w.startsWith("level=")) || "").slice(6);
  let src = token.text.replace(/\s+$/, "");
  const head = src.trimStart().split(/\s/)[0];
  if (head === "flowchart" || head === "graph" || head === "block-beta") src += "\n" + vocab;
  return `<pre class="mermaid"${size ? ` data-size="${size}"` : ""}${lvl ? ` data-level="${lvl}"` : ""}>${esc(src)}</pre>\n`;
};
marked.use({ renderer, gfm: true });
let body = marked.parse(md);

// One <section class="page"> per H1. Pages with a diagram get the legend footer.
const chunks = body.split(/(?=<h1[\s>])/);
body = chunks.map((chunk) => {
  if (!chunk.trim()) return "";
  const hasDiagram = /class="mermaid"/.test(chunk);
  const lvl = (chunk.match(/data-level="(\d)"/) || [])[1];
  return `<section class="page"${lvl ? ` data-level="${lvl}"` : ""}>\n${chunk}\n${hasDiagram ? legend : ""}</section>\n`;
}).join("");

const title = (md.match(/^#\s+(.+)$/m) || [, "vis"])[1].trim();
const html = `<!doctype html>
<html><head><meta charset="utf-8"><title>${esc(title)}</title>
<style>${css}</style>
<script>${mermaidJs}</script>
</head><body>
<main>${body}</main>
<script>
  mermaid.initialize({ startOnLoad: false, theme: "neutral", securityLevel: "loose",
    flowchart: { htmlLabels: true, useMaxWidth: true, padding: 12, nodeSpacing: 45, rankSpacing: 50 },
    sequence: { useMaxWidth: true, wrap: true, width: 190, actorMargin: 60, messageMargin: 40, boxMargin: 12, noteMargin: 12 },
    block: { padding: 12 },
    er: { useMaxWidth: true, entityPadding: 15, minEntityWidth: 120, minEntityHeight: 60 },
    mindmap: { useMaxWidth: true, padding: 12 },
    state: { useMaxWidth: true },
    fontFamily: "-apple-system, Helvetica Neue, Helvetica, Arial, sans-serif" });
  (async () => {
    const nodes = [...document.querySelectorAll("pre.mermaid")];
    for (let i = 0; i < nodes.length; i++) {
      const src = nodes[i].textContent;
      const div = document.createElement("div");
      try {
        const { svg } = await mermaid.render("vis-d" + i, src);
        div.className = "diagram" + (nodes[i].dataset.size ? " " + nodes[i].dataset.size : "");
        div.innerHTML = svg;
      } catch (e) {
        div.className = "diagram-error";
        div.setAttribute("data-vis-error", String(i));
        div.textContent = "DIAGRAM " + i + " FAILED: " + (e && e.message ? e.message : e) + "\\n\\n" + src;
      }
      nodes[i].replaceWith(div);
    }
    document.documentElement.setAttribute("data-vis-done", "1");
  })();
</script>
</body></html>`;

const work = mkdtempSync(join(tmpdir(), "vis-"));
const htmlPath = htmlOut || join(work, "vis.html");
writeFileSync(htmlPath, html);

// NOTE: no --user-data-dir; with it, --dump-dom never exits on macOS Chrome.
const common = ["--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
  "--hide-scrollbars", "--virtual-time-budget=15000"];
const run = (extra) => execFileSync(chrome, [...common, ...extra, `file://${htmlPath}`],
  { stdio: ["ignore", "pipe", "ignore"], maxBuffer: 64 * 1024 * 1024, timeout: 90000 }).toString();

// 1) Render once with --dump-dom to detect diagram failures.
const dom = run(["--dump-dom"]);
const errs = [...dom.matchAll(/data-vis-error="(\d+)"[^>]*>([^<]*)/g)];
for (const [, i, text] of errs) console.error(`mermaid diagram #${i} failed:\n${text.slice(0, 600)}\n`);
const count = (dom.match(/class="diagram( full| short)?"/g) || []).length;

// 2) Print the PDF.
run(["--no-pdf-header-footer", `--print-to-pdf=${pdfPath}`]);

// 3) Optional full-page screenshot.
if (shotOut) run(["--window-size=1000,8000", `--screenshot=${shotOut}`]);

const pages = (readFileSync(pdfPath, "latin1").match(/\/Type\s*\/Page[^s]/g) || []).length;
console.log(`pdf: ${pdfPath}\npages: ${pages}\ndiagrams ok: ${count}\ndiagrams failed: ${errs.length}\nhtml: ${htmlPath}`);
process.exit(errs.length ? 2 : 0);
