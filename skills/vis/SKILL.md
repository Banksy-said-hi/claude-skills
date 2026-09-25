---
name: vis
description: Explain a freshly cloned repo visually in a landscape PDF on the Desktop (overview, dictionary, technologies, data models, abstract architecture map, components and responsibilities, layers, inputs and outputs by component, load, one map plus one sequence per main feature, two chosen views, where to look next). Use when the user types /vis or asks to understand a codebase visually.
allowed-tools: Bash, Read, Glob, Grep, Write, Skill
---

You are producing a document that gets an engineer ready to add features to this repo after one read.
No questions to the user. Work through every phase in order. Nothing else.

The deliverable: `~/Desktop/<repo>-vis.pdf`, A4 landscape, 12 pages plus 2 per main feature, built from Markdown with
Mermaid diagrams by `$VIS/build.mjs`, where `$VIS` is the directory holding this SKILL.md
(normally `~/.claude/skills/vis`). The information lives on the diagrams: box names,
role lines, paths, and labelled arrows. Prose is short and in simple words.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 1 — SETUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Repo root: `git rev-parse --show-toplevel` (fall back to the current directory).
   Repo name: basename of that path.
2. Work dir: `WORK=$(mktemp -d -t vis)`. All intermediate files go there.
   Output: `OUT=~/Desktop/<repo>-vis.pdf`. If it exists, overwrite it.
3. Read `$VIS/cookbook.md` now. Every diagram you write must follow a shape from it.
   Do not invent Mermaid syntax. Do not write classDef lines; the build injects the vocabulary.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 2 — STUDY, THEN EXTRACT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Invoke the `study` skill first. This is mandatory.

Then get the facts a diagram needs. Use deterministic tools for edges; use your own reading only
to name and group things. Never install anything (no brew, pip, npm -g, cargo install, go install).
`npx --yes` is allowed because it installs nothing permanently. Record what ran and what was missing.

Size and language:
  - `scc --format json .` if `scc` exists, else `find` + `wc -l` per top-level folder.
  - The language with the most lines decides which extractor to try.

Edges (imports, calls), first one that applies and is available:
  - JS/TS:     `npx --yes dependency-cruiser --no-config --output-type json src > $WORK/deps.json`
  - Python:    `pydeps <pkg> --show-deps --no-output > $WORK/deps.json`; `pyreverse -o mmd -p <name> <pkg>` if pylint exists
  - Go:        `goda graph "./...:all" > $WORK/deps.dot`
  - Rust:      `cargo modules dependencies --lib > $WORK/deps.dot`
  - Java:      `jdeps -verbose:class -dotoutput $WORK/jdeps <jar or classes dir>`
  - Any:       if nothing above exists, read entry points, config, and imports by hand with grep.

Always by hand:
  - Technologies: every manifest and build file (package.json, Cargo.toml, pyproject, go.mod,
    depends/, Dockerfile, CI workflows). For each: what it does for THIS project.
  - Entry points: main files, CLI commands, HTTP routes, cron or job definitions, message consumers.
  - Inputs: what comes in from outside (requests, files, peers, queues, APIs, env or config).
  - Outputs and artifacts: what goes out or is produced (responses, files written, emails, DB rows,
    build outputs, logs). Name the real folder, file, or table.
  - Load facts, only from evidence: rates or intervals in constants and docs, data sizes in docs,
    thread and worker counts in code, what each request reads versus writes. Where the repo says
    nothing, the answer is "not stated in repo". Never invent a number.
  - External systems: databases, queues, third-party APIs, other services. Black boxes only.
  - Stateful things: any entity with 4 or more named states (enum, status column, state machine).
  - Threads, workers, processes, queues: how work is split at runtime.
  - `lessons/` folder if present: read it; it tells you where things went wrong before.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 3 — BUILD THE CAST (ONE MODEL, MANY VIEWS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write `$WORK/cast.md`: one table that every diagram is drawn from. Columns:

  | Name (plain words) | Kind | Tier | Path | Lines | Role (3 to 5 words) | Takes in | Gives out | Talks to |

Kind is one of: person, external, entry, core, worker, store, queue, artifact.
Tier is major, normal, or minor: major = on the critical path or the biggest part; minor = small
helper or rarely touched. Stores get their tier from how central they are to the main flow.
Rules:
  - Every row with kind entry/core/worker/store/queue/artifact has a real path that exists. Check it.
  - Names are everyday words. "Scorer", not "ScoringServiceImpl". Keep the same name everywhere.
  - At most 14 rows inside the repo. Group small folders into the part they serve. Diagrams never
    introduce a box that is not in the cast.
  - Pick the ONE critical path: the thing the system exists to do. It becomes the sequence page and
    the thick arrows on the architecture page.
  - Pick 3 to 5 columns for the layers page: self-contained vertical slices (for example Network,
    Validation, Storage, Wallet, API), each owning 2 to 4 cast rows.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 4 — THE VISUAL VOCABULARY (fixed, every page)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

One shape and one colour per kind, on every page. The build injects the colours; you assign classes.

  person      stadium        `you([You<br/><small>role</small>])`                          class person
  external    hexagon        `x{{Name<br/><small>what it is</small>}}`                    class external
  entry       parallelogram  `r[/Name<br/>role<br/><small>path</small>/]`                 class entry
  core        rectangle      `c[Name<br/>role<br/><small>path</small>]`                    class core
  worker      procs          `w@{ shape: procs, label: "Name<br/>role<br/><small>path</small>" }`   class worker
  store       disk           `s@{ shape: lin-cyl, label: "Name<br/>role<br/><small>path</small>" }` class store
  queue       das            `q@{ shape: das, label: "Name<br/><small>path</small>" }`     class queue
  artifact    doc            `f@{ shape: doc, label: "name" }`                             class artifact
  tier        second class   `class a,b major` · `class c minor` (normal is the default)

Box text: line 1 the name, line 2 the role in three to five words, line 3 the path in `<small>`.
People and outside systems have no path.

Every arrow is labelled: verb plus object, then format or protocol when known. Direction is the
direction the data moves. `-->|sends blocks, TCP|` data or call · `-.->|announces new block|`
event or async · `==>|hands the block to|` the one critical path. Unlabelled arrows are a defect.
On the architecture page keep labels to two or three words, and never draw an arrow from deep
inside the system back to a person or outside system: it closes a cycle and the diagram turns
tall and narrow. Say that fact in the box's role line instead. People and outside systems only
send arrows in, or receive them from a way-in or an event feed.
A flow longer than seven boxes in a line becomes a thin strip: split it into two `short` fences
on the same page.

SPACING RULE, no overlaps anywhere: no text may touch or cross a box border, another label, or
an arrow. The build already spaces nodes and ranks generously; what you control is the amount of
text. Box text: at most three lines, each at most five words, plus the small path line. Arrow
labels: at most four words on flowcharts, two or three on block grids. Grid cells (layers,
inputs and outputs): at most two short lines plus the path, no `major` class. Sequence messages:
at most eight words, they wrap automatically. Sequence participants: the name, then on the
second line the file BASENAME only (invite.ts, not the full path), or the participant boxes
overlap each other. If a label still collides, shorten it, move the
fact into the box's role line, add a `space` cell, or split the diagram in two `short` fences.

The legend strip with these shapes, the three arrow styles, and the zoom breadcrumb is added by
the build to every diagram page. Declare the zoom level on the fence: `level=1` system,
`level=2` parts, `level=3` inside.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 5 — THE PAGES, IN THIS ORDER (12 fixed + 2 per main feature, up to 3 features)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Each H1 is one page. Each page is self-contained. No page has a "What you are looking at" or
"In plain words" section. If a page needs prose, it is at most two sentences under the title,
except the prose pages (1, 2, 3, 4) and the last page.

Main features (the USPs): the one to three capabilities the README and docs lead with that set
this repo apart from its alternatives. If the docs are unclear, the largest user-facing
capabilities on the critical paths. Fewer than three is fine. Each gets two pages.

  1. What this repo is         No diagram. Five short blocks with bold lead-ins, at most 200
                               words on the whole page, so it reads in under a minute:
                               What it does (two sentences). One journey (one real trip through
                               the system, start to finish, four sentences). Primary goals
                               (three bullets, one line each). Primary features (four bullets,
                               one line each). The jungle (an analogy: each main part is an
                               animal chosen for its role, the flows are jungle dynamics such as
                               the river, the hunt, the watering hole; four sentences, and only
                               the four or five most important parts get an animal).
  2. Dictionary                No diagram. Every word a reader might not know, one plain line
                               each, in three groups: Words of the domain (the problem space),
                               Names used in this document (each cast name, what it is, its
                               crate or folder), Technology words. 15 to 25 entries, wrapped in
                               `<div class="cols">` so it flows in two columns. Every term used
                               later in the document must be here.
  3. Technologies              See page details below.
  4. Data models               classDiagram, fence `short level=3` so the bullets fit under it,
                               then one bullet per type: bold name, what it is, which part
                               creates it, which part checks or reads it, where it is stored
                               (file, table, or column family). Then one sentence on how the
                               types nest.
  5. The whole architecture    ABSTRACT MAP. `flowchart TB`, fence `full level=1`. At most 8
                               boxes inside the repo, each a GROUP of cast rows (for example
                               Network, Node tasks, Verifier, State, Finalized store,
                               Interfaces), plus people and outside systems. Labelled arrows,
                               critical path thick. These 8 box ids are reused on every feature
                               map page.
  6. Components and            No diagram. One table, one row per map box and per important
     responsibilities          sub-part, at most 12 rows. Columns: Component · Responsibility
                               (one sentence, what it is accountable for) · Owns (the data,
                               files, or connections only it touches) · Must not do (the
                               boundary, one phrase) · Path. Names are the cast names.
  7. Layers as columns         `block-beta`, fence `level=2`. 3 to 5 NARROW columns with a
                               `space` cell between neighbours, so the arrows between columns
                               have room and can be read. Column title is the first cell. 2 to 4
                               boxes per column, each box: name plus the file basename only in
                               small text. Three to six cross-column arrows, each labelled verb
                               plus object ("hands blocks", "writes coins").
  8. Inputs and outputs        `block-beta` with `columns 4`, middle cell spanning two (`:2`),
                               fence `full level=2`. NO central
     by component              box. One row per major component (at most 7 rows): left cell
                               its inputs (source, what, rate), middle cell the component with
                               its load parameters (workers, queue depth, batch size, cache
                               time, limits), right cell its outputs (what, to whom, rate).
                               Arrows in to component and component to out, labelled with what
                               moves. Rates and numbers only from evidence in the repo, else
                               "not stated in repo".
  9. Load                      `flowchart LR`, fence `short level=2`: the hot path only, rates
                               on the arrows, worker counts, queue depths, and batch sizes in the
                               boxes. Under it the fact table: How much comes in, How much is
                               stored, Read heavy or write heavy, Concurrency, What limits it.
                               Columns: Question, Answer, Evidence in repo. "Not stated in repo"
                               is a valid answer. Invented numbers are forbidden.
 10. Feature N, the map        Title: "Feature: <name>". One sentence on why it is a USP.
                               `flowchart TB`, fence `full level=2`. The SAME 8 map boxes with
                               the same ids. Boxes this feature does not touch get
                               `class x faded`. Boxes it touches may be EXPANDED into a subgraph
                               holding their sub-parts (real paths, at most 6 sub-parts each).
                               Only this feature's arrows are drawn, labelled, critical path
                               thick.
 11. Feature N, the trip       sequenceDiagram of this feature's main trip, fence `level=2`.
                               At most 8 participants, each with its file basename on a second
                               line, steps in words, no function names.
      ... pages 10 and 11 repeat for feature 2 and feature 3 ...
 12. Chosen view 1             Pick from the menu below. Subtitle states the reason in one
 13. Chosen view 2             sentence. Rule: the two views that most change what you would do
                               when adding a feature to this repo. Not a duplicate of a
                               feature page.
 14. Where to look next        mindmap fence `short level=3`, then "To change X, open Y", 6 to
                               10 rows. Last page.

Page details:
  - Technologies: bullets, one per technology, from the manifests: name in bold, then what it
    does for this project in one line. Groups: Language, Libraries, Storage, Build and test,
    Runtime. Wrapped in `<div class="cols">` (blank line after the opening tag and before the
    closing tag) so it flows in two columns.
  - Data models: classDiagram of the 3 to 7 core types, fields only, no methods, field names in
    plain words, relationship lines labelled with a verb, fence `level=3`. erDiagram instead if
    the repo owns a relational schema.

The menu for the chosen views (cookbook has each):
  - Stages of a thing          stateDiagram-v2 of the stages one entity passes through, for the
                               most important stateful entity (4+ states). Title it
                               "Stages of a <thing>: from <first> to <last>".
  - Where the weight is        treemap-beta of lines per area, labels of two or three words
  - Threads and processes      flowchart of workers (procs) and queues (das) and what feeds what
  - Deployment view            architecture-beta when two or more things run on their own
  - Dependency map             flowchart of which parts import or call which, labelled arrows
  - Inside one part            flowchart LR of the biggest part, its files as boxes, in and out

Never: a history page, fenced code, inline code in prose, function names, unlabelled arrows,
a box without a path (people and outside systems excepted), a page with only a heading.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 6 — WRITE `$WORK/vis.md`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Writing rules, checked line by line before building:
  - Sentences of at most 15 words. One idea per sentence.
  - No acronym without its expansion the first time. No jargon without a plain explanation in
    the same sentence ("a queue, a waiting line for work").
  - Say what a thing does, then what it is called.
  - The same name for the same thing on every page. Names come from the cast table.
  - No marketing words. "You" is the user of the system, "this repo" is the system.
  - No backticks anywhere in prose. Paths appear only as the small third line inside boxes and
    on the Where to look next page.
  - Mermaid labels: short. Avoid parentheses, quotes, semicolons, and `#` inside labels; wrap a
    label in double quotes when it has spaces plus special characters.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 7 — BUILD AND CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  node $VIS/build.mjs $WORK/vis.md "$OUT" --html $WORK/vis.html

Exit code 2 means a diagram failed to render; stderr names it and shows the source. Fix the
Mermaid against the cookbook and rebuild. Never delete a diagram to make the build pass.

Text checks (mandatory):
  grep -c '`' $WORK/vis.md                  must be 0 outside mermaid fences
  grep -n 'What you are looking at\|In plain words' $WORK/vis.md   must be empty
  grep -nE '[A-Za-z_]+\(\)' $WORK/vis.md    must be empty (no function names)
  page count in the build output must be 12 + 2 x (number of features), so 14, 16, or 18
  the H1 count in vis.md must equal that page count (one H1 per page, nothing overflowed)

Visual check (mandatory, at most 3 rounds):
  pdftoppm -r 45 -png "$OUT" $WORK/pg     (if pdftoppm exists; else build with --screenshot)
Read the page images. Look for: a page that overflowed into a second sheet, a diagram that is a
thin strip, an unlabelled arrow, a box without a path, a shape used for the wrong kind, a legend
missing on a diagram page, a treemap label that vanished, and ANY text that overlaps a box,
another label, or an arrow (rasterize the suspect page alone at 90 dpi to be sure). An overlap
is a defect: shorten the text, move it into the role line, add a `space` cell, or split the
diagram. Fix in vis.md, rebuild, re-check.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 8 — REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Print only this:

  vis: <path to PDF>  (<N> pages)
  pages: <all page titles, comma separated>
  critical path: <name>
  columns: <the layer names>
  chosen views: <view 1> because <reason> · <view 2> because <reason>
  extractors: used <list> · missing <list>
  assumptions: <anything you had to guess; "none" if none>
  sources: $WORK/vis.md, $WORK/cast.md
