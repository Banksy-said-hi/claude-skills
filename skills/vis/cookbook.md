# vis cookbook

Every snippet here rendered through `build.mjs` with the vendored Mermaid 11.17. Copy the shape,
change the words. Pages are A4 landscape. Fence options: `full` (whole-page diagram), `short`
(diagram with a table under it), `level=1|2|3` (highlights the zoom breadcrumb in the legend).

## The vocabulary (injected automatically, never write classDef yourself)

`build.mjs` appends `vocab.mmd` to every `flowchart` and `block-beta` fence. You only assign classes.

| Kind | Node syntax | Class |
|---|---|---|
| Person | `you([You<br/><small>role</small>])` | `person` |
| Outside system | `x{{Other nodes<br/><small>what it is</small>}}` | `external` |
| Way in | `r[/RPC door<br/>role<br/><small>path</small>/]` | `entry` |
| Core part | `c[Rule checker<br/>role<br/><small>path</small>]` | `core` |
| Background worker | `w@{ shape: procs, label: "Workers<br/>role<br/><small>path</small>" }` | `worker` |
| Data store | `s@{ shape: lin-cyl, label: "Chain store<br/>role<br/><small>path</small>" }` (in block-beta: `s[("...")]`) | `store` |
| Queue or stream | `q@{ shape: das, label: "Job queue<br/><small>path</small>" }` | `queue` |
| File produced | `f@{ shape: doc, label: "debug.log" }` | `artifact` |
| Importance | add a second class | `major`, `normal`, `minor` |
| The repo box | the one subgraph on the architecture page | `repo` |

Box text: line 1 the name, line 2 the role in three to five words, line 3 the path in `<small>`.
Edge text: verb plus object, then format or protocol when known. Direction = where the data goes.
`-->|sends blocks, TCP|` data or call · `-.->|announces new block|` event or async · `==>|hands the block to|` the critical path.

## Layout lesson: a top-to-bottom flowchart fills a landscape page (older, detailed example)

```mermaid full level=1
flowchart TB
  nodes{{Other nodes<br/><small>same program elsewhere</small>}}
  you([You<br/><small>runs the node</small>])
  subgraph repo [zcashd · this repo]
    direction TB
    net[/Peer network<br/>talks to other nodes<br/><small>src/net.cpp</small>/]
    rpc[/RPC door<br/>takes your commands<br/><small>src/rpc/</small>/]
    rules[Rule checker<br/>validates blocks<br/><small>src/main.cpp</small>]
    proofs[Proof engine<br/>privacy math<br/><small>src/rust/</small>]
    wallet[Wallet<br/>your keys and money<br/><small>src/wallet/</small>]
    queue@{ shape: das, label: "Job queue<br/><small>src/asyncrpcqueue.cpp</small>" }
    workers@{ shape: procs, label: "Send workers<br/>build transactions<br/><small>src/wallet/asyncrpcoperation_sendmany.cpp</small>" }
    chain@{ shape: lin-cyl, label: "Chain store<br/>blocks and coins<br/><small>src/txdb.cpp</small>" }
    wfile@{ shape: lin-cyl, label: "Wallet file<br/><small>wallet.dat</small>" }
    log@{ shape: doc, label: "debug.log" }
  end
  apps{{Apps listening}}
  nodes -->|sends blocks and transactions, TCP| net
  net -->|relays blocks, TCP| nodes
  net ==>|hands each message to| rules
  rules ==>|writes accepted blocks and coin state| chain
  rules -->|asks to verify proofs, batch| proofs
  rules -.->|announces new block| wallet
  rules -.->|announces new block, ZeroMQ| apps
  you -->|JSON commands, HTTP| rpc
  rpc -->|reads facts from| rules
  rpc -->|puts send jobs on| queue
  queue -->|feeds| workers
  workers -->|builds transactions with| wallet
  wallet -->|saves keys and transactions| wfile
  rules -->|appends lines| log
  class you person
  class nodes,apps external
  class net,rpc entry
  class rules,proofs,wallet core
  class workers worker
  class chain,wfile store
  class queue queue
  class log artifact
  class rules,chain major
  class wfile,log minor
  class repo repo
```

## Page 5: the whole architecture, the abstract map (at most 8 boxes inside the repo, ids reused by every feature page)

```mermaid full level=1
flowchart TB
  nodes{{Other nodes}}
  you([You])
  wallets{{Wallet servers}}
  subgraph repo [zebrad · this repo]
    direction TB
    net[/Network<br/>talks to peers<br/><small>zebra-network/</small>/]
    tasks[Node tasks<br/>syncer, inbound, mempool, gossip<br/><small>zebrad/src/components/</small>]
    verifier[Verifier<br/>checks blocks and transactions<br/><small>zebra-consensus/</small>]
    state[State<br/>recent chain, best chain<br/><small>zebra-state/</small>]
    store@{ shape: lin-cyl, label: "Finalized store<br/>RocksDB<br/><small>zebra-state/src/service/finalized_state/</small>" }
    rpc[/Interfaces<br/>JSON-RPC, gRPC, metrics<br/><small>zebra-rpc/</small>/]
    types[Chain types<br/>shared types and rules<br/><small>zebra-chain/</small>]
  end
  nodes -->|blocks, transactions| net
  net ==>|downloaded blocks| tasks
  tasks ==>|blocks to check| verifier
  verifier ==>|verified blocks| state
  state ==>|blocks 1000 deep| store
  you -->|JSON-RPC| rpc
  wallets -->|gRPC| rpc
  rpc -->|reads| state
  types -.->|used by all| verifier
  class you person
  class nodes,wallets external
  class net,rpc entry
  class tasks,verifier,state,types core
  class store store
  class net,verifier,state major
  class types minor
  class repo repo
```

## Feature page: the same map, this feature lit, the rest faded, touched boxes expanded

Same ids as the abstract map. Untouched boxes get `class x faded` and no arrows. A touched box may
become a subgraph with its sub-parts (real paths). Only this feature's arrows are drawn.

```mermaid full level=2
flowchart TB
  nodes{{Other nodes}}
  you([You])
  wallets{{Wallet servers}}
  subgraph repo [zebrad · this repo]
    direction TB
    net[/Network<br/>talks to peers<br/><small>zebra-network/</small>/]
    tasks[Node tasks<br/>syncer<br/><small>zebrad/src/components/sync.rs</small>]
    subgraph verifier [Verifier · zebra-consensus/]
      router[Router<br/>checkpoint or full<br/><small>src/router.rs</small>]
      ckpt[Checkpoint verifier<br/><small>src/checkpoint.rs</small>]
      blockv[Block verifier<br/><small>src/block.rs</small>]
      batch@{ shape: procs, label: "Batch proof checks<br/><small>tower-batch-control/</small>" }
    end
    state[State<br/>recent chain, best chain<br/><small>zebra-state/</small>]
    store@{ shape: lin-cyl, label: "Finalized store<br/>RocksDB<br/><small>zebra-state/src/service/finalized_state/</small>" }
    rpc[/Interfaces<br/>JSON-RPC, gRPC, metrics<br/><small>zebra-rpc/</small>/]
    types[Chain types<br/><small>zebra-chain/</small>]
  end
  nodes -->|blocks| net
  net ==>|downloaded blocks| tasks
  tasks ==>|block to check| router
  router -->|old block| ckpt
  router -->|new block| blockv
  blockv -->|proofs, in batches| batch
  ckpt ==>|verified| state
  blockv ==>|verified| state
  state ==>|1000 deep| store
  class nodes external
  class net entry
  class tasks,router,ckpt,blockv,state core
  class batch worker
  class store store
  class you,wallets,rpc,types faded
  class net,router,state major
  class repo repo
```

## Page 9: load, the hot path with rates in the arrows and sizes in the boxes

```mermaid short level=2
flowchart LR
  nodes{{Other nodes<br/>25 outbound, up to 125 inbound}}
  net[/Network<br/>one block per 75 s at the tip, thousands per minute while syncing<br/><small>zebra-network/</small>/]
  syncer[Syncer<br/>up to 1000 blocks in flight<br/><small>zebrad/src/components/sync.rs</small>]
  verifier@{ shape: procs, label: "Verifier<br/>proofs batched, one batch per core<br/><small>zebra-consensus/</small>" }
  state[State<br/>one commit per block<br/><small>zebra-state/</small>]
  store@{ shape: lin-cyl, label: "RocksDB<br/>grows every block" }
  nodes -->|blocks| net -->|blocks| syncer ==>|blocks| verifier ==>|verified| state ==>|writes| store
  class nodes external
  class net entry
  class syncer,state core
  class verifier worker
  class store store
```

## Page 2: dictionary, and page 4: data model bullets (formats)

```
<div class="cols">

**Words of the domain.**
- **Block** — a batch of transactions with a header. Blocks form a chain.

**Names used in this document.**
- **Verifier** — the part that checks blocks and transactions. Crate zebra-consensus.

**Technology words.**
- **RocksDB** — a key-value database with named tables called column families.

</div>
```

Data model bullet: `- **Block** — a header plus transactions. Made by miners, checked by the Verifier, stored by the Finalized store in the block_header_by_height column family.`

## Page 7: layers as columns (block-beta, narrow columns with a space between them)

Narrow columns: name plus file basename only. A `space` cell between neighbours gives the
arrows room. `columns` at the top = column blocks + spaces (5 columns → 9). Labels are verb
plus object.

```mermaid level=2
block-beta
  columns 9
  block:c1
    columns 1
    l1["Network"] a1["Peer connections<br/><small>net.cpp</small>"] a2["Message reader<br/><small>main.cpp</small>"] a3["Address book<br/><small>addrdb.cpp</small>"]
  end
  space
  block:c2
    columns 1
    l2["Validation"] b1["Block rules<br/><small>main.cpp</small>"] b2["Memory pool<br/><small>txmempool.cpp</small>"] b3["Proof engine<br/><small>rust/</small>"]
  end
  space
  block:c3
    columns 1
    l3["Storage"] s1[("Chain store<br/><small>txdb.cpp</small>")] s2[("Block files<br/><small>blocks/</small>")]
  end
  space
  block:c4
    columns 1
    l4["Wallet"] w1["Keys, balances<br/><small>wallet.cpp</small>"] w2["Tx builder<br/><small>transaction_builder.cpp</small>"] w3[("Wallet file<br/><small>wallet.dat</small>")]
  end
  space
  block:c5
    columns 1
    l5["API"] r1["HTTP server<br/><small>httpserver.cpp</small>"] r2["Command table<br/><small>rpc/</small>"]
  end
  a2 -- "hands blocks" --> b1
  b1 -- "writes coins" --> s1
  b1 -- "announces tip" --> w1
  r2 -- "reads balance" --> w1
  r2 -- "reads chain" --> b1
  class l1,l2,l3,l4,l5 collabel
  class a1,a2,a3,b1,b2,b3,w1,w2,r2 core
  class s1,s2,w3 store
  class r1 entry
  classDef collabel fill:#e9e9e9,stroke:none,font-weight:600
```

## Page 8: inputs and outputs by component (block-beta grid, no central box)

One row per component: inputs on the left, the component with its load parameters in the
middle, outputs on the right. `columns 4` with the middle cell spanning two (`:2`) so its
text fits. Shapes in block-beta: `{{ }}` outside system, `([ ])` person, `[( )]` store,
`[/ /]` way in. At most 7 rows, short text per cell, no `major` class in grid cells (the
bigger font overflows the cell).

```mermaid full level=2
block-beta
  columns 4
  i1{{"Other nodes<br/>blocks every 75 s, transactions all day"}} c1[/"Network<br/>25 outbound peers, up to 125 inbound<br/><small>zebra-network/</small>"/]:2 o1{{"Other nodes<br/>relayed blocks, replies to requests"}}
  i2["Network<br/>hashes, then blocks"] c2["Syncer<br/>up to 1000 blocks in flight<br/><small>zebrad/src/components/sync.rs</small>"]:2 o2["Verifier<br/>one block at a time, in order"]
  i3["Syncer, Inbound<br/>blocks and transactions"] c3["Verifier<br/>proofs in batches of 64 or every 100 ms<br/><small>zebra-consensus/</small>"]:2 o3["State<br/>verified blocks, or a rejection"]
  i4["Verifier<br/>verified blocks"] c4["State<br/>last 1000 blocks in memory, one commit per block<br/><small>zebra-state/</small>"]:2 o4[("RocksDB<br/>one write per block")]
  i5(["You, wallet servers<br/>a few calls per minute"]) c5[/"Interfaces<br/>40 JSON-RPC methods, gRPC streams<br/><small>zebra-rpc/</small>"/]:2 o5(["You, wallet servers<br/>JSON and gRPC replies"])
  i1 -- "blocks, TCP" --> c1
  c1 -- "relay, TCP" --> o1
  i2 -- "downloads" --> c2
  c2 -- "block to check" --> o2
  i3 -- "to check" --> c3
  c3 -- "verified" --> o3
  i4 -- "commit" --> c4
  c4 -- "finalize" --> o4
  i5 -- "requests" --> c5
  c5 -- "replies" --> o5
  class i1,o1 external
  class i5,o5 person
  class c1,c5 entry
  class c2,c3,c4 core
  class i2,i3,i4,o2,o3 minor
  class o4 store
```

## Page 6: components and responsibilities (table format)

```
| Component | Responsibility | Owns | Must not do | Path |
|---|---|---|---|---|
| Network | Keep connections to peers and move messages in and out | the peer set and address book | check or store blocks | zebra-network/ |
```

## Feature trip page: one trip (sequence, file basename per participant, steps in words, no function names)

```mermaid level=2
sequenceDiagram
  autonumber
  participant O as Other node
  participant N as Peer network<br/>net.cpp
  participant R as Rule checker<br/>main.cpp
  participant P as Proof engine<br/>rust
  participant S as Chain store<br/>txdb.cpp
  participant W as Wallet<br/>wallet.cpp
  O->>N: a new block
  N->>R: hands the block over
  R->>R: checks shape and mining puzzle
  R->>S: saves the raw block
  R->>P: verifies all privacy proofs in one batch
  P-->>R: all valid
  R->>S: updates the unspent coins
  R-->>W: new chain tip
  R->>N: tell the peers
  N->>O: block announcement
```

## Page 3: data models (class diagram, fields only)

```mermaid level=3
classDiagram
  class CBlockHeader { +version +previousBlockHash +merkleRoot +time +difficulty +nonce +solution }
  class CBlock { +transactions }
  class CTransaction { +version +inputs +outputs +lockTime +expiryHeight +saplingBundle +orchardBundle }
  class CTxIn { +previousOutput +unlockScript }
  class CTxOut { +value +lockScript }
  class OrchardBundle { +actions +proof +bindingSignature }
  CBlockHeader <|-- CBlock
  CBlock "1" --> "*" CTransaction : holds
  CTransaction "1" --> "*" CTxIn : spends
  CTransaction "1" --> "*" CTxOut : creates
  CTransaction "1" --> "0..1" OrchardBundle : hides
```

## Menu: stages of a thing (state diagram of the stages one entity passes through)

```mermaid level=3
stateDiagram-v2
  [*] --> READY : send command creates the job
  READY --> EXECUTING : a worker picks it up
  EXECUTING --> SUCCESS : built, proved, broadcast
  EXECUTING --> FAILED : not enough funds or a rule broken
  READY --> CANCELLED : you cancel it
  SUCCESS --> [*]
  FAILED --> [*]
  CANCELLED --> [*]
```

## Menu: where the weight is (treemap, short labels or they vanish)

```mermaid level=2
treemap-beta
"zcash source"
  "Tests": 73000
  "Borrowed libraries": 66000
  "Rule checker": 51500
  "Wallet": 33000
  "Rules and helpers": 19800
  "Proof engine": 13700
  "RPC door": 7500
```

## Menu: threads and processes (flowchart, workers as procs, queues as das)

```mermaid level=2
flowchart LR
  t1@{ shape: procs, label: "net thread<br/>reads sockets<br/><small>src/net.cpp</small>" }
  t2@{ shape: procs, label: "message handler<br/>runs the rules<br/><small>src/main.cpp</small>" }
  t3@{ shape: procs, label: "script check pool<br/>signatures in parallel<br/><small>src/main.cpp</small>" }
  t4@{ shape: procs, label: "async RPC workers<br/>build transactions<br/><small>src/asyncrpcqueue.cpp</small>" }
  q1@{ shape: das, label: "per-peer receive buffer" }
  q2@{ shape: das, label: "job queue" }
  t1 -->|fills| q1 -->|drained by| t2
  t2 -->|fans out signature checks to| t3
  q2 -->|feeds| t4
  class t1,t2,t3,t4 worker
  class q1,q2 queue
```

## Menu: deployment view (architecture-beta, only when two or more things run on their own)

```mermaid level=1
architecture-beta
  group docker(cloud)[Runs in Docker]
  service web(server)[Web] in docker
  service worker(server)[Worker] in docker
  service db(database)[Postgres] in docker
  service queue(disk)[Redis queue] in docker
  service gmail(internet)[Gmail]
  web:R -- L:queue
  queue:R -- L:worker
  worker:B -- T:db
  web:B -- T:db
  worker:R -- L:gmail
```

## Last page: where to look next (mindmap, two levels, at most 15 leaves)

```mermaid level=3
mindmap
  root((zcash))
    src
      main.cpp
      net.cpp
      init.cpp
      txdb.cpp
      wallet
      rpc
      rust
    qa
      rpc-tests
    zcutil
      build.sh
```

## Page 2: technologies in two flowing columns

Wrap the bullets in a div with class `cols`, with blank lines around the tags, or the page overflows.

```
<div class="cols">

**Language.**
- **C++ 17** — most of the node.

**Storage.**
- **LevelDB** — a simple key-value database for the chain store.

</div>
```

## Menu: threads and processes, as two short strips on one page

When a flow has more than seven steps in a line, split it into two `short` fences on the same page
(for example the network side and the command side). One legend is added for the page.

## Known Mermaid limits, learned the hard way

- `direction TB` inside a subgraph is ignored as soon as any edge touches a subgraph. Invisible links do not fix it. Use block-beta for columns.
- A left-to-right flowchart with many nodes becomes a thin strip. For the full-page architecture use `flowchart TB`.
- Never draw an arrow from deep inside the system back to a person or an outside system (for example "dashboard draws for You"). It closes a cycle, dagre breaks it by moving that person to the middle, and the whole diagram becomes tall and narrow. Put that fact in the box's role line instead.
- Long edge labels stretch the gaps between ranks. Two or three words per arrow on the architecture page.
- Treemap hides the label of any box that is too narrow. Keep labels to two or three words.
- `block-beta` cannot use `@{ shape: ... }`. Use `[( )]` for stores there.
- Do not use Mermaid's C4 syntax. Still beta, poor layout.
