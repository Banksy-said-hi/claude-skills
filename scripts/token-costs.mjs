#!/usr/bin/env node
// Estimate how many prompt tokens each published skill costs, and rewrite the README section
// between <!-- tokens:start --> and <!-- tokens:end --> with a Mermaid bar chart and a table.
// Usage: node scripts/token-costs.mjs            (from the repo root)
//
// Estimate: ~4 characters per token. What counts:
//   own     = SKILL.md body + other .md files in the skill folder (references the skill reads)
//   invoke  = own + every skill it invokes ("invoke the `x` skill"), followed transitively
//   listing = the frontmatter description, which sits in context every session
// Code and vendor/ files are executed, not read into context, so they are not counted.

import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join } from "node:path";

const CHARS_PER_TOKEN = 4;
const tok = (s) => Math.round(s.length / CHARS_PER_TOKEN);

// Only skills tracked by git: private (gitignored) skills stay out of the README.
const tracked = execFileSync("git", ["ls-files", "skills"], { encoding: "utf8" }).split("\n");
const names = [...new Set(tracked.filter((p) => p.endsWith("/SKILL.md")).map((p) => p.split("/")[1]))];

const skills = {};
for (const name of names) {
  const dir = join("skills", name);
  const raw = readFileSync(join(dir, "SKILL.md"), "utf8");
  const fm = raw.match(/^---\n([\s\S]*?)\n---\n/);
  const description = fm?.[1].match(/^description:\s*(.*)$/m)?.[1] ?? "";
  const refs = readdirSync(dir).filter((f) => f.endsWith(".md") && f !== "SKILL.md");
  const own = tok(raw) + refs.reduce((n, f) => n + tok(readFileSync(join(dir, f), "utf8")), 0);
  const calls = [...raw.matchAll(/invoke the `([\w-]+)` skill/gi)].map((m) => m[1].toLowerCase());
  skills[name] = { own, listing: tok(description), calls };
}

const closure = (name, seen = new Set()) => {
  if (seen.has(name) || !skills[name]) return seen;
  seen.add(name);
  for (const c of skills[name].calls) closure(c, seen);
  return seen;
};
for (const [name, s] of Object.entries(skills)) {
  const chain = [...closure(name)];
  s.invoke = chain.reduce((n, c) => n + skills[c].own, 0);
  s.chained = chain.filter((c) => c !== name);
}

const rows = Object.entries(skills).sort((a, b) => b[1].invoke - a[1].invoke);
const max = Math.ceil(rows[0][1].invoke / 1000) * 1000;
const listingTotal = rows.reduce((n, [, s]) => n + s.listing, 0);

const section = `<!-- tokens:start -->
Estimated prompt tokens each skill loads when invoked (~4 chars/token; regenerate with \`node scripts/token-costs.mjs\`).
Runtime cost (files read, tool output) comes on top and depends on the repo.

\`\`\`mermaid
xychart-beta
  title "Tokens loaded per invocation (incl. chained skills)"
  x-axis [${rows.map(([n]) => `"${n}"`).join(", ")}]
  y-axis "tokens" 0 --> ${max}
  bar [${rows.map(([, s]) => s.invoke).join(", ")}]
\`\`\`

| Skill | Own | Chains into | Per invocation | Always loaded (description) |
|---|---:|---|---:|---:|
${rows.map(([n, s]) => `| \`/${n}\` | ${s.own} | ${s.chained.map((c) => `\`/${c}\``).join(", ") || "—"} | ${s.invoke} | ${s.listing} |`).join("\n")}
| **All descriptions** | | | | **${listingTotal}** |
<!-- tokens:end -->`;

const readme = readFileSync("README.md", "utf8");
const re = /<!-- tokens:start -->[\s\S]*?<!-- tokens:end -->/;
if (!re.test(readme)) {
  console.error("README.md has no <!-- tokens:start --> / <!-- tokens:end --> markers");
  process.exit(1);
}
writeFileSync("README.md", readme.replace(re, section));
console.log(rows.map(([n, s]) => `${n}: ${s.invoke}`).join("\n"));
