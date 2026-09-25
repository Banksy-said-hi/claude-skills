---
name: perf
description: Autonomous, stack-aware performance audit. Studies the project, tests bottleneck hypotheses against real code, takes measurements, prints a severity-ranked ASCII report, then plans fixes for HIGH findings in plan mode. Use when the user types /perf.
allowed-tools: Bash, Read, Glob, Grep, Skill, EnterPlanMode, ExitPlanMode
---

Fully autonomous. No questions. Phases in order, then the report. Nothing else.

## 1 · Study
Invoke the `study` skill first (mandatory) unless the project was already studied this session.

## 2 · Hypotheses
List candidate bottlenecks for THIS stack. Cover what applies:

- **Load & bundle** — bundle size, code splitting, eager imports, server code leaking into client bundles, unoptimized assets, render-blocking third-party scripts, cache headers/CDN.
- **Frontend runtime** — allocations in render/animation loops, needless re-renders or subscriptions, DOM writes in hot paths, canvas/WebGL draw calls and texture uploads, heavy main-thread work without workers, leaked listeners/timers, layout-triggering CSS animations.
- **Backend runtime** — N+1 queries, missing indexes, blocking I/O in async code, missing caches, over-fetching, cold starts, oversized or uncompressed payloads.
- **Pipeline & build** — uncached or serial CI steps, slow test suites, needless transpilation, slow dev reload.

## 3 · Verify
Read the actual code for every hypothesis; confirm or refute with evidence. Severity:

- 🔴 **HIGH** — measurable frame drops, multi-second delays, or >50 kB wasted bundle
- 🟡 **MED** — visible jank or latency on mid-range hardware, needless CPU/GPU cost
- 🟢 **LOW** — minor waste
- ✅ **OK** — already correct; say what you checked

Each finding: file:lines, the quoted pattern, why it hurts, a concrete fix.

## 4 · Measure
Safe, non-destructive commands only: run the build and capture chunk sizes, count dependencies from the lockfile, line counts of hot files, source maps shipped to production, debug logging in production paths, sync I/O at startup.

## 5 · Report
Print exactly this, every placeholder filled, nothing truncated:

```
╔══════════════════════════════════════════════════════════════╗
║  PERFORMANCE AUDIT  ·  <project>   ·  Stack: <stack>         ║
╚══════════════════════════════════════════════════════════════╝

SUMMARY   tested N · 🔴 N · 🟡 N · 🟢 N · ✅ N

FINDINGS
[01] 🔴 HIGH · <title>
     File    : <path>:<lines>
     Pattern : <quoted code>
     Problem : <why it hurts>
     Fix     : <specific action>
[NN] ✅ OK · <title>
     File    : <path>
     Why OK  : <what was checked>

MEASUREMENTS
  <hard numbers from phase 4; if one could not be taken, say why>

TOP QUICK WINS  (highest impact · lowest effort)
  1. [NN] <action>
  2. [NN] <action>
  3. [NN] <action>
```

No 🔴 findings → stop here.

## 6 · Plan HIGH fixes
Call EnterPlanMode. One plan covering every 🔴 finding (MED/LOW are the user's call). For each: finding number and title, exact files and lines, the concrete change (not "optimize X" — "replace the per-row `execute` loop at file:line with one `executemany`"), and any risk (semantics, rebuild, other callers). End with **EXECUTION ORDER**: batch independent changes, order dependent ones.

Call ExitPlanMode. Execute only after approval, in that order; honor any changes the user makes.
