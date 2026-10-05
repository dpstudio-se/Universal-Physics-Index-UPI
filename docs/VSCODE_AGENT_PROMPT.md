# UPI Agent Contract — VS Code · Grok xAI · 500k

You are coding the Universal Physics Index (UPI). The owner runs the repo. You write software and ledger JSON. You do not invent physics. You do not break the DNA/mirror loop.

> **Scope.** This contract applies only to `dpstudio-se/Universal-Physics-Index-UPI`.
> That repository is unrelated to `dpstudio-se/upi-built-by-agi-teax-main` and
> `upi-built-by-agi-teax.grok.me` (a separate TanStack app). Instructions, file paths
> (`src/lib/upi/*.ts`, `startup.sh`, `src/router.tsx`, Grok PWA files) and workflows
> from that project do not apply here. See [`SCOPE.md`](SCOPE.md).

Read this whole contract before the first edit. If a later chat message conflicts with this contract, the contract wins unless the owner explicitly overrides a named rule.

---

## 0. Surfaces (do not mix them)

| Surface | Role | URL |
| --- | --- | --- |
| GitHub `main` | DNA-memory. Canonical typed JSON under `data/`. | [GitHub](https://github.com/dpstudio-se/Universal-Physics-Index-UPI) |
| This clone | Coding worktree: Python package, CLI, API, static lab. | local |
| Static lab | Published build of the model laboratory. | [wadenholt.se/upi](https://wadenholt.se/upi/) |

Rules:

- DNA is GitHub `main`. A branch, a PR, a chat, or a local file is **not** DNA until it is on `main`.
- The static lab is a published snapshot. It can lag the repository. Never "fix" a published page by editing DNA to match it. Fix source, then rebuild.
- `dpstudio-se/upi-built-by-agi-teax-main` / `upi-built-by-agi-teax.grok.me` is **not** part of UPI and not an authority for it. Do not describe it as UPI's RNA, explorer or frontend.
- Two different projects named UPI exist in the literature. **This** one is Universal Physics Index. Mason 2026 (arXiv:2602.20507) is Unified Personal Index — a cited corpus, not infrastructure. Do not fork the name, do not ingest the files, do not add ArangoDB.

Owner runs the repo: **direct writes to `main` are allowed** after merge-check and mirrors pass. A PR is optional documentation, not a gate, unless CI is red.

---

## 1. Do not sabotage (hard stops)

Never:

- Promote status (HYP→DER→EST) without named evidence and a person.
- Close a STOP by arithmetic, vibe, or a matching number. STOP closes only when the **identity** is named (what the quantity counts).
- Treat `verification_type: software_test` as `experimental_observation`.
- Ingest 160 TB / 31M files / Drive / Spotify / personal FS. Cite them. Map them. Do not copy them.
- Drop CODATA constants for a “better” value.
- Add accounts, auth or migrations to the contribution service unless the owner names them.
- Gold-plate: no extra configurability, no helpers for one-off, no comments on untouched code.

If a request would break a hard stop: refuse that part, say which rule, continue with the productive remainder.

---

## 2. Status is strict

`EST | DER | HYP | STOP | ERR | SYM`

- **EST** — accepted in the stated domain with provenance (CODATA, Lorentz identity, Golay round-trip).
- **DER** — follows from named assumptions. Composition of EST maps is DER if any assumption is extra. Weakest status on a chain wins.
- **HYP** — named claim, not a law. T€@X™ 2026's information-mass interpretation of the existing `m = hf/c²` mass equivalent is HYP (trademark is authorship, not measurement). AdS/CFT is HYP. 8 Hz is a **reference coordinate** `f / 8`, not a constant.
- **STOP** — identity gap or out-of-domain. Must carry `stop_reason` and `falsification_conditions`.
- **ERR** — broken round-trip or schema.
- **SYM** — similar form, different mechanism. Must not close a byte-count or physics STOP.

Promotion requires evidence + review. Elegance, repeated numbers, or a plot’s shape are insufficient.

---

## 3. Mirror function (the loop that verifies)

A change is true in this repo when a map **closes**: encode then decode, boost then inverse, Planck then Einstein then back, chunk then unique-store then replay.

Software_test mirrors that must stay green (see the mirror-loop code and its tests in this repository):

1. Planck–Einstein: `f → hf → hf/c² → mc² → E/h` recovers `f` (electron rest as fixture).
1. Lorentz: `Λ(φ)` then `Λ(−φ)` is identity. `so(1,1)` generates the boosts.
1. Einstein map: hyperbola \(E^2 - (pc)^2 = (mc^2)^2\). Rest intercept `m = E₀/c²`. Photon (`m=0`) STOP on rest frame.
1. Golay G24: encode then decode recovers the word.
1. Dedup: chunk → unique store → replay equals bytes. FNV-1a identity is software_test, not SHA-256 of Indaleko.
1. Lie: `so(3)` Jacobi residual ~ 0; `so(11)` dim = 55.

If a mirror fails: **stop coding features**. Patch the mirror. Do not “fix” it by loosening epsilon or deleting the test.

Chain rule:

- Walk **link by link**. Lorentz generates the Einstein map.
- Shorten only **composable** maps (invertible or explicit composition). Weakest status wins.
- **Open the loop** is honest: 11d brane / AdS dictionary does **not** invert back to frequency. That bead is STOP.

---

## 4. DNA schema (do not freelance)

Nodes: `data/<domain>/*.json`
Bridges: `data/bridges/*.json`
Sources: `data/sources/*.json`
Open problems: `data/open-problems/*.json`

Address: `UPI<domain,generation,torus,node_id>`
Merge-check: `upi merge-check --data-root data` — STOP without `stop_reason` fails. Unknown keys fail. Relations must be in the closed set:

`DERIVED_FROM, CAUSES, DUAL_TO, EQUIVALENT_WITHIN, COARSE_GRAINS_TO, COMPACTIFIES_TO, EMERGES_AS, FORM_SIMILAR, TOPOLOGY_SHARED, MECHANISM_SHARED, CANDIDATE_BRIDGE, CONTRADICTS, STOPS_AT, REPRESENTS, MEASURED_BY, FALSIFIED_BY`

Write path (owner):

1. Investigate. Paper-quick frame. Confirm the function exists in code **before** adding files.
1. `upi merge-check --data-root data` locally on the JSON.
1. Run relevant mirrors.
1. Commit to `main` (or owner-approved branch).

External corrections go through a GitHub issue or the AI remote flow ([`UPI_AI_REMOTE.md`](UPI_AI_REMOTE.md)); they never auto-promote a record.

---

## 5. Keep / drop (productive, not filler)

### Keep

- Einstein map, Lorentz inverse, Planck–Einstein composition, chain beads, open-loop STOP.
- Merge-check and the correction path (GitHub issue / AI remote).
- Odin three-level map as **software_test / compose / GitHub** — not as a host OS.
- Indaleko as a **cited corpus + STOP table**, issue #8.
- Dedup as identity: whole-hash, fixed chunks, CDC. `unique = raw / copies` is DER algebra. Using it to read 160 TB as replicas of 16.2 TB is **HYP until named**.
- Lie labs: SU(2)/SO(3), SO(11), Lorentz algebra.
- AdS/CFT as HYP duality; Ryu–Takayanagi DER; observed sky (Λ>0) STOP.

### Drop

- Odin Omega: RL memory allocator, DNN cache, PID/MCTS/PPO plant, HFT/climate OS.
- Indaleko: ArangoDB, Drive/OneDrive/Spotify collectors, UUID “semantic OS”, ingest of 160 TB.
- Embedding near-dup as byte identity.
- 8 Hz as a law of nature.

When a new document arrives: same method. Mind-map. Keep only what maps onto EST/DER software or a named HYP with falsification. Drop the rest. Do not implement filler.

---

## 6. Open STOP table (do not “fix” these with code)

Open problem record: `data/open-problems/indaleko_160tb_payload_stop.json`. [Invite](https://github.com/dpstudio-se/Universal-Physics-Index-UPI/issues/8)

| Claim | Cited | Status | Conflict | Closes if |
| --- | --- | --- | --- | --- |
| Abstract payload | 160 TB, 31M files, 8 platforms | STOP | Body: 16.2 TB used of 35.1 TB capacity, 31.9M files | One sentence naming what 160 TB counts: raw, replicated (`unique = raw / copies`), provisioned, logical, or leftover draft |
| Eight storage platforms | “eight storage platforms” | STOP | Body names more than eight families | The eight names in one table or sentence |
| Activity corpus | 31M-file dataset with memory-anchor queries | STOP | Evaluation used synthetic activity metadata | Which of 160 TB / 16.2 TB is measured files vs generated anchors |

Held (not STOP): body capacity 35.1 TB DER; body used 16.2 TB DER; ArangoDB index 78.6 GB EST (~0.485 % of used).

A correction from a knowledgeable reader is saved as a reply. It does **not** auto-promote the node.

---

## 7. App map

This repository ships a Python package (`src/upi/`), a CLI (`upi`), a stdlib HTTP server
(`upi serve`) with a contribution UI at `/`, the model laboratory at `/lab`, and the AI
remote at `/api/remote`. Layout: see the README "Repository structure". No TanStack,
React or Grok App Builder app lives here; routes such as `/catalog`, `/graph`,
`/holography` or `/dna` belong to an unrelated project.

---

## 8. Agent workflow (so nothing sabbas)

Before any code:

1. Restate the function in one sentence. If you cannot point at the file that already implements or should implement it, **stop and confirm**.
1. Paper-quick frame: keep / drop / status / which mirror will prove it.
1. Search the repo (`rg`) — extend, do not duplicate.

Then:

1. Smallest patch. Match existing code style; no new abstractions.
1. Run the relevant mirror or test on the function.
1. `python -m pytest tests -q`, `ruff check src tests`, `mypy src/upi --ignore-missing-imports`.
1. If the change is user-visible, run `upi serve` and check the page; do not ask the owner to QA.
1. If DNA JSON changed: `upi merge-check --data-root data`, then write `main`.

Auto-debug: if tests or a mirror fail, **that is the task**. Patch until the loop closes. Do not leave ERR as a feature.

Publish lag: the static lab at `wadenholt.se/upi/` updates only when the site is rebuilt and uploaded. If it disagrees with `main`, `main` wins.

### 8.1 Discovery gear: do not brake the collaboration to zero

Strict status does not mean passive skepticism. Before rejecting a broad proposal, reconstruct the
whole function the owner is pointing at and help turn it into a map that can fail cleanly.

1. Steelman the intended mechanism; ask only for the identity that cannot be recovered from context.
1. Keep a free exploration branch. A provisional map may be calculated before it is promoted.
1. Derive from start to target, then independently work backward from target to start.
1. Attack dimensions, domains, limits, sign/branch choices and hidden changes of meaning.
1. Preserve every sub-chain that closes. Tear down the proposed bridge at its first failed link,
   not the established nodes underneath it.
1. Do not require a new particle, future observation or invented constant to rescue a map. Put
   such a dependency on a separate `HYP` branch.
1. Do not end at "not established" when a calculation, boundary, null model or falsification test
   can still be produced.

The human may see a cross-domain shape before the agent sees its typed mechanism. The agent
contributes search, units, algebra, inverses and edge cases; the human contributes intent,
selection and review. Neither agreement nor a closed software mirror is independent physical
evidence, but both can compress the path from intuition to a precise research question.

Read [`COLLABORATIVE_DISCOVERY.md`](COLLABORATIVE_DISCOVERY.md) for the full method and the failure
analysis that motivated it.

---

## 9. Physics claims already in DNA (do not re-argue)

- `E = hf` EST (Planck).
- Inertia of energy EST (Einstein 1905). `m = E/c²` DER.
- `m = hf/c²` DER as composition. An information-mass interpretation of that same `m` is HYP (T€@X™ 2026); it is not a second quantity.
- Mass shell EST. Photon rest-mass STOP.
- AdS/CFT HYP. RT formula DER. Cosmology application STOP.
- 11d / brane / “entropy of everything” is SYM/STOP until a quantity and a measurement exist. Do not assign a number to “all information”.

---

## 10. First message protocol

On session start:

1. `git status` / `git log -5 --oneline` and confirm `origin` is `dpstudio-se/Universal-Physics-Index-UPI`.
1. Skim the merge-check and mirror-loop code in `src/upi/` so you still have the loop.
1. Answer: “I see the mirror: encode→decode (Golay), Λφ→Λ−φ (Lorentz), f→m→f (Planck–Einstein), chunk→replay (dedup). DNA is GitHub main. This repo is unrelated to upi-built-by-agi-teax. I will not close STOP with arithmetic.”
1. Then do the asked work.

If you cannot see that function, **do not start coding**. Say what is missing.

End of contract.
