---
name: scout
description: Objective deep research before or during building - how others (competitors, open source, papers, platform docs) solve the problem at hand, what our code does differently, what is obsolete, and what to replace it with - written to docs/research/ with dated, graded references. Use when the owner types /scout, asks for deep research, competitor analysis, "state of the art" or "are we reinventing the wheel".
---

# /scout: find what others already know

Goal: decisions about the system rest on current, verified knowledge, not on habit or on the first idea. Output is
a report in the repo that says, with sources: how others handle it, what we do, where we are behind or wrong, and
what to replace it with. Objectivity beats enthusiasm: "no evidence found" and "we are already ahead here" are
valid findings.

## 1. Intake: what do we need to know, for which part?

If the request does not already say, ask with **AskUserQuestion** (one round, up to 4 questions):
- **Area**: which part of the system or which decision (e.g. "how the bot reads group messages", "payment UX").
- **Decisions pending**: what will change depending on the answer (so research stays aimed).
- **Competitor set**: named products to compare, or "find them".
- **Horizon and depth**: how recent (default: prefer the last 18 months; older only as background) and how deep
  (quick scan, or deep with 3–4 parallel researchers).

When the request already covers these, state the scope in two lines and go on.

## 2. Inventory: what do we do today?

Before searching, read our own code, specs (`docs/specs/`), earlier reports (`docs/research/`) and open issues for
the area. Write down our current approach per topic in a sentence each, with `file:line`. Every finding later is
compared against this, never against nothing.

## 3. Research plan

Split the area into 3–6 **questions**, each tied to a decision. For each: which source types answer it best.

Source ranking (best first):
1. Primary: official platform docs and changelogs, standards, regulators, the product itself (pricing pages, help
   centres), source code and issue trackers of open-source projects.
2. Measured: peer-reviewed or arXiv papers with evaluations, benchmarks, engineering blogs with numbers, postmortems.
3. Secondary: reputable press, analyst write-ups, conference talks.
4. Anecdotal: forums, Reddit, HN, Stack Overflow; useful for failure stories, never alone for a decision.
Vendor marketing is a claim to check, not evidence.

## 4. Research (parallel when deep)

For a deep run, launch up to 4 research agents in parallel, each with one cluster of questions, our current
approach for it, the source ranking, and this return format; ask for under 1,200 words each:

```
CLAIM: <one sentence>
SOURCE: <title> — <URL> — <published or updated date> — grade A/B/C/D
RELEVANCE: <which of our decisions it bears on>
```
plus "competitors found" (name, what they do in this area, still alive?), "obsolete or risky practices seen", and
"evidence against" (things that contradict the obvious answer). Agents use WebSearch and WebFetch; they must open
the source, not quote search snippets.

For a quick run, do the same yourself with fewer questions.

## 5. Verify

- Re-open the source of every claim that drives a recommendation; drop or downgrade what does not hold.
- Where sources conflict, say so and say which you trust and why.
- Date-check: platform features and prices change; a claim older than the horizon is marked as possibly stale.
- Separate **fact** (sourced) from **inference** (ours), visibly.

## 6. Report

Write `docs/research/YYYY-MM-DD-<slug>.md` and add a line to `docs/research/README.md` (create it if missing:
one line per report, newest first). If an earlier report on the same slug exists, start with **Changed since
<date>**.

```markdown
# <Area>: research
Date · scope · horizon · how deep · who asked

## Bottom line
<5–8 bullets: the decisions this report supports, each with confidence high/medium/low>

## Changed since <last report>          (only on a re-run)

## Today in our code
<topic → our approach, file:line>

## Competitors and prior art
| Product / project | What it does here | Status (alive, dead, pivoted) | What we can learn |

## Findings
### <Topic>
- **Others:** how they handle it [n]
- **Us:** what we do (file:line)
- **Gap:** behind / wrong / equal / ahead
- **Better:** the replacement, effort S/M/L, confidence
### …

## Avoid
- <obsolete or failed practice>: why, who learned it the hard way [n]

## Open questions
- <what the evidence could not settle, and how to settle it (experiment, measurement, ask an expert)>

## Proposed changes
| # | Change | Why (refs) | Effort | Goes to |      ← "Goes to": a spec decision, a new /spec, or an issue

## Sources
[n] <title>. <publisher>. <date>. <URL> (grade, accessed <date>)
```

## 7. Hand-off

Show the owner the bottom line and the proposed changes. For the ones they adopt: feed them into `/spec`
(a decision in an existing spec, or a new spec) or open issues. Offer to commit the report; pushing follows the
project's rules.

## Rules

- Every claim that drives a recommendation has a source with a date; no source, no recommendation.
- Look for the case against: failures, shutdowns, lawsuits, negative benchmarks.
- Say plainly where we are ahead or where nothing better exists.
- Keep our own bias visible: if we built it, we like it; the report must survive that.
- No secrets, keys or personal data in the report.
