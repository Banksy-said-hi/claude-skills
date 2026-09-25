---
name: unify
description: Autonomous last-gate-before-push drift audit. Checks UI consistency against the project's canonical tokens and components, checks that architecture diagrams in the code still match the running system, and checks that every model or external call goes through the project's canonical, observable wrapper. Prints an ASCII report, then plans HIGH and MED fixes in plan mode. Use when the user types /unify.
allowed-tools: Bash, Read, Glob, Grep, Skill, EnterPlanMode, ExitPlanMode
---

Fully autonomous. No questions. Phases in order, then the report. Nothing else.

Purpose: catch drift away from the project's most recent decisions before a push. Run the sections that apply: skip UI if there is no frontend, skip topology if nothing in the repo draws the architecture, skip calls if there is no canonical wrapper.

## 1 · Study
Invoke the `study` skill first (mandatory) unless the project was already studied this session. You need every page route, every service (compose, Procfile, workers), any component or doc that draws the system, and recent git activity.

## 2 · Baseline (the ruler)
Recent decisions come from:
- `git log --since="2 weeks ago" --oneline`: read the diffs of commits touching UI, design, components, or architecture, and note the canonical patterns they introduced.
- `lessons/`: drift bugs already paid for once. Their patterns are non-negotiable.
- CLAUDE.md / AGENTS.md: stated conventions ("all model calls go through X").

Compile:
- **Tokens**: color, font, and spacing variables; status colors; light/dark parity.
- **Components**: buttons by role, status badges, cards, loading, empty, and error states, date formatting.
- **Topology**: every service that does work, every queue or channel between them, and the component or doc that renders them.
- **Call wrapper**: the canonical path for model or external calls (client, registry of call types, context/tracing helper) and where its telemetry surfaces (table, dashboard, filter list).

## 3 · Sweep
**UI drift**, across every route and shared component:
- hardcoded colors, font sizes, or spacing where a variable exists; colors missing a dark-theme equivalent
- the same role rendered differently (buttons, badge vs plain text, section headers)
- inconsistent loading, error, or empty states and copy; inconsistent date formats
- the same action labeled differently; a confirmation on one destructive action but not another
- header, nav active state, or card padding/radius/shadow drifting between pages
- a list page and its detail page showing different status text for the same state

**Topology drift**: diff ground truth (services, queue kinds, event channels, enqueue edges, found by grep) against what the diagram component declares.
- a service or queue in reality but missing from the diagram → 🔴
- a node or edge that no longer exists, or a stale label → 🟡
- an emitted event with no documented consumer → 🟢

**Call drift**: diff every model or external call site against the canonical wrapper.
- a call that bypasses the wrapper (a direct client call, or a raw HTTP call to the model endpoint) → 🔴 invisible to telemetry and to rate limits
- a call-type enum value with no registry entry → 🔴
- a call made outside the context/tracing helper, so telemetry rows can't be traced to the workflow → 🔴
- a hand-off dict built for a dispatcher that lacks a key the dispatcher reads (the call gets silently misrouted; tests rarely catch it) → 🔴
- a call type or metric that is recorded but missing from the dashboard, filter list, or rollup → 🟡
- a registry entry nothing references → 🟢
- if the telemetry store is reachable read-only: a registered call type with zero rows in the last 14 days → 🟢 (a cold path, or broken recording)

## 4 · Verify
Read the code for every item. A finding needs: file:lines, the quoted drift, the quoted canonical version with its path, and a concrete fix. Not "use the variable" but "replace `#4ade80` with `var(--green)` per `app/globals.css:42`".

- 🔴 **HIGH**: a primary user flow looks inconsistent, the topology is materially wrong, or a call is invisible
- 🟡 **MED**: a secondary surface, stale labels, or telemetry recorded but not shown
- 🟢 **LOW**: a hardcoded value that currently equals the variable, or cosmetic 1px drift
- ✅ **OK**: already aligned; say what you checked and across how many files

## 5 · Report
Print exactly this, sections that were skipped marked `skipped (<reason>)`:

```
╔══════════════════════════════════════════════════════════════╗
║  UNIFICATION AUDIT  ·  <project>   ·  Stack: <stack>         ║
╚══════════════════════════════════════════════════════════════╝

SUMMARY   UI N · topology N · calls N · 🔴 N · 🟡 N · 🟢 N · ✅ N

UI FINDINGS
[U01] 🔴 HIGH · <title>
      File      : <path>:<lines>
      Drift     : <quoted>
      Canonical : <quoted, with path>
      Fix       : <action>

TOPOLOGY FINDINGS
[T01] 🔴 HIGH · <missing-node | missing-edge | stale-label | extra-node>
      Reality : <what runs, file:line>
      Diagram : <what is drawn, file:line>
      Fix     : <add / remove / rename>

CALL FINDINGS
[C01] 🔴 HIGH · <bypass | unregistered | no-context | dict-missing-key | not-surfaced | vestigial | cold>
      Call site : <file:line>
      Surfaces  : <where it should show up, file:line>
      Canonical : <a sibling call site that does it right, file:line>
      Fix       : <the wiring to add>

ALIGNED
[OK01] ✅ <title> — <what was verified, across which files>

TOP FIXES BEFORE PUSH  (most visible · lowest effort)
  1. [ID] <action>
  2. [ID] <action>
  3. [ID] <action>
```

No 🔴 or 🟡 findings → stop: aligned, safe to push.

## 6 · Plan HIGH + MED fixes
Call EnterPlanMode. One plan, grouped as UI, TOPOLOGY, and CALLS. For each finding: ID and title, files and lines, drift → canonical (quoted), and the reality source for topology. A global swap is written as "replace across N files" plus the file list.

Separate **RISKY** list, so the user can decline items one by one: pages under active redesign, swaps touching more than 10 files, user-visible copy changes, changes to tuned call config, cross-language ports.

**EXECUTION ORDER**: call-site wiring first, so telemetry is correct during manual testing; then global token swaps; then per-page fixes; then additive telemetry surfacing (filters, columns, rollups); then diagram updates.

Call ExitPlanMode. Execute only after approval; honor any "skip [ID]" requests.
