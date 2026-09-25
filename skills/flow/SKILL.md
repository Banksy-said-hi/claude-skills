---
name: flow
description: Analyze the current project and draw its architecture as a box-and-arrow ASCII flow diagram with a one-line legend per component. Use when the user types /flow.
---

1. Explore source, config, and infra files (compose, Dockerfiles).
2. Identify components, services, data stores, external integrations, and what triggers the flow.
3. Trace how data moves between them.
4. Draw it:
   - Every major component as a labeled box
   - Direction on every arrow (→ ← ↔)
   - External APIs and infrastructure (databases, queues, containers)
   - The user or trigger that starts the flow

```
┌─────────────┐     ┌─────────────┐
│  Component  │────▶│  Component  │
└─────────────┘     └─────────────┘
```

Output: diagram first, then a legend with one line per component. No other prose.
