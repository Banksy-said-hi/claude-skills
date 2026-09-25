---
name: yo
description: Quick "where are we" re-orientation after the user has been away. One line on what we're building, 3-5 terse status fragments, and a small ASCII diagram only if a model, architecture, or bug is under discussion. Use when the user types /yo.
---

The user stepped away. Be ruthlessly short — a third of your normal length. No preamble.

Output exactly:

```
## **Building first**
<one short line — the immediate goal in flight>

## **Status**
- <fragment, ~6 words>

- <fragment>

- <fragment>
```

- 3–5 bullets, blank line between them, fragments not sentences, real file/component names.
- Only if a data model, architecture, or specific bug is on the table: add `## **Picture**` with one small ASCII diagram.
- Pull from actual session state; never invent progress. Nothing in flight → say so in one line and stop.
