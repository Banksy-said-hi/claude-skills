---
name: spec
description: Turn a feature, idea or behaviour change into a written spec by finding the gaps and asking about them instead of guessing. Use when the owner describes something new to build or change (before planning or editing code), when the spec gate denies an edit, or when the user types /spec.
---

# /spec: find the gaps, ask, write it down

The rule: **nothing the owner did not say and the code does not show goes into the build silently.** Each gap
ends up in one of three places: answered by the code, asked as a question, or listed as an assumption the owner sees
before the spec is ready. Specs live in the repo at `docs/specs/<slug>.md`. A hook (`hooks/gate.py`) denies code
edits and leaving plan mode in a git repo until the current branch has a spec with `status: ready` and no open markers.

## 0. Triage (one line to the owner)

| Kind | Signs | Path |
|---|---|---|
| **Small** | typo, copy, one-line fix, rename, dependency bump, a change the owner fully specified | Write a small spec (§6), continue at once. No questions. |
| **Bug** | something worked and broke | Small spec naming the symptom and how it will be verified; ask only if the expected behaviour is unclear. |
| **Feature** | new behaviour, new screen, new flow, a change to rules, money, data or permissions | §1–§5 in full. |
| **Idea** | "should we…", "what if…", unclear whether it is worth building | §1–§5, and the spec ends with a verdict: **go / clarify / stop**, with the reason. Stopping is a good outcome. |

When unsure between small and feature, treat it as a feature.

## 1. Read before asking

Answer from the repo everything it can answer: what exists, what is half-built, what the code assumes, open issues
and milestones (`gh issue list`), the project's CLAUDE.md and decision records. Never ask the owner what `grep` can
tell. Record findings in the spec's **Today** section with `file:line` references.

## 2. Scan for gaps

Mark each category **Clear / Partial / Missing** (internally; show the table only in the final report):

- **Outcome**: who it is for, the problem, what "done" looks like, how it is measured, what is out of scope
- **Actors and roles**: who can do what; who owns the result when something goes wrong
- **Flow**: the main path step by step; empty, loading, error and cancel states
- **Data and life cycle**: entities, identity, states and transitions, retention and deletion
- **Money** (if any): who pays, how much, fees, rounding, currency, refunds, failed and partial payments
- **Identity and access**: sign-in or not, how a person is recognised, abuse and spam
- **Outside services**: each one's failure modes, cost per use, limits, test vs live
- **Privacy and law**: personal data, consent, retention, regulated activity, terms
- **Platforms**: devices, browsers, in-app browsers, channels (web, Telegram, WhatsApp…)
- **Edge cases**: concurrency, duplicates, timeouts, retries, people who never respond
- **Fit**: current milestone or focus rule, what it depends on, what it blocks, what gets slower or riskier
- **Terms**: words used two ways; vague adjectives ("fast", "simple") with no number

Then read `docs/specs/CHECKS.md` in the repo if it exists: the project's own questions (its money rules, laws,
platforms). They count as categories too.

## 3. Ask

- Only ask what **changes the build, the tests, the cost or the risk**. Rank by impact × uncertainty.
- Use **AskUserQuestion**: up to 4 questions per round, **at most 2 rounds**. Each question is a full sentence ending
  in `?`; 2–4 options; the **recommended option first, labelled "(Recommended)"**, its description saying why;
  every option's description says what it means for the build.
- Before the round, give the owner a few lines: what the code already answers, and blockers found (things that stop
  the feature whatever is chosen, e.g. a missing legal opinion or a dependency not done).
- Anything not asked becomes an **assumption** with a reason, never a silent choice.
- The owner may say "skip", "your call" or pick Other: record exactly that.

## 4. Write the spec

`docs/specs/<slug>.md`, kebab-case slug. Plain words, the project's own style.

```markdown
---
status: draft            # draft → ready → done
kind: feature            # feature | idea | bug | small
branch: <git branch the work happens on>
issue: <#number or empty>
created: <YYYY-MM-DD>
---
# <Title>

## Why
<the problem, for whom, in two to four sentences>

## Today
<what the code already has and what it lacks, with file:line>

## Success criteria (done means)
1. <observable, testable, numbered; Given / When / Then where it helps>

## Out of scope
- <what this does not do>

## Flow
<the main path step by step; then the error, empty and cancel paths>

## Rules
- R1 <a rule the code must follow>

## Blockers and risks
- <thing>: <why it matters> → <what unblocks it>

## Decisions
- <date> Q: <question> → A: <answer>

## Assumptions
- A1 <assumed>: <why this default>     ← the owner confirms these before ready

## Open
- [NEEDS CLARIFICATION: <question>]   ← none may remain at ready

## Verdict (ideas only)
go | clarify | stop: <reason>
```

Write the draft with a `[NEEDS CLARIFICATION: …]` marker for every open question **before** asking, so the file
always shows what is unknown. After each answer, update the affected sections, add a **Decisions** line, and delete
the marker. Leave no contradicting old text.

## 5. Ready

1. Show the owner the **Assumptions** list and the blockers (short). Ask: "These are my assumptions; correct any?"
2. When the owner agrees and no `[NEEDS CLARIFICATION` remains, set `status: ready`. **Only the owner's agreement
   makes a spec ready**; never set it to get past the gate.
3. Then plan (plan mode, issues on the project board) from the spec, not from memory of the conversation.
4. Offer to commit the spec with the work. Pushing follows the project's own rules.

## 6. Small spec

```markdown
---
status: ready
kind: small
branch: <branch>
created: <YYYY-MM-DD>
---
# <What changes>
<One sentence: what changes and why it needs no questions.>
Verify: <how it will be checked>
```

Tell the owner in one line that you used the small path, so every exception is visible.

## 7. Converge (when the work is done)

Check each success criterion against the code and tests: met / partly / not met, with evidence. Unmet ones become
tasks or issues. When all are met, set `status: done`. A `done` spec no longer opens the gate: new work on the
branch needs its own spec.

## The gate (what the hook checks)

In a git repo, `Edit`, `Write`, `MultiEdit`, `NotebookEdit`, file-writing `Bash` commands and `ExitPlanMode` are denied unless
`docs/specs/` has a file with `branch:` equal to the current branch, `status: ready` and no `[NEEDS CLARIFICATION`.
Always allowed: files under `docs/specs/`, `*.md` and `*.txt` files, and paths outside the repo.
A repo opts out with an empty file `docs/specs/.off` (the owner's decision, never Claude's).
When the gate denies, run `/spec` for the work at hand; do not try other ways to write the file.
