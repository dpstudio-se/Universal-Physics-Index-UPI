# UPI Agent Contract — VS Code · Grok xAI · 500k

You are coding the Universal Physics Index (UPI). The owner runs the repo. You write software and ledger JSON. You do not invent physics. You do not break the DNA/RNA loop.

Read this whole contract before the first edit. If a later chat message conflicts with this contract, the contract wins unless the owner explicitly overrides a named rule.

---

## 0. Three surfaces (do not mix them)

| Surface | Role | URL |
|---|---|---|
| GitHub `main` | DNA-memory. Canonical typed JSON under `data/`. | https://github.com/dpstudio-se/Universal-Physics-Index-UPI |
| This VS Code clone | Coding worktree. Source of the RNA engine. | local |
| Live RNA | Transcribes DNA, runs labs, writes back. | https://upi-built-by-agi-teax.grok.me |

Rules:
- DNA is GitHub `main`. A branch, a PR, a chat, or a local file is **not** DNA until it is on `main`.
- RNA is the TanStack explorer (Grok App Builder + grok.me). It **reads** DNA and **writes** proposals/nodes. It is not a second ledger.
- grok.me is a **deployed RNA snapshot**. It can lag VS Code. Never “fix” grok.me by editing DNA to match a stale UI. Fix source, then deploy.
- Two different projects named UPI exist. **This** one is Universal Physics Index. Mason 2026 (arXiv:2602.20507) is Unified Personal Index — a cited corpus, not infrastructure. Do not fork the name, do not ingest the files, do not add ArangoDB.

Owner runs the repo: **direct writes to `main` are allowed** after merge-check and mirrors pass. A PR is optional documentation, not a gate, unless CI is red.

---

## 1. Do not sabotage (hard stops)

Never:
- Delete or rewrite `startup.sh`, `src/router.tsx` `getRouter`, `<PreviewHostBridge />`, Grok PWA injector, `public/__grok/`, or `server/middleware/grok-pwa.ts`.
- Hide “Created with Grok” / Remix branding in code. That is a project setting, not a patch.
- Bind the preview off `0.0.0.0:8080` or start Vite without `npm run dev` / `scripts/with-app-env.mjs`.
- Add auth, `@/lib/db`, or migrations unless the owner names accounts. Auth stays OFF.
- Promote status (HYP→DER→EST) without named evidence and a person.
- Close a STOP by arithmetic, vibe, or a matching number. STOP closes only when the **identity** is named (what the quantity counts).
- Treat `verification_type: software_test` as `experimental_observation`.
- Ingest 160 TB / 31M files / Drive / Spotify / personal FS. Cite them. Map them. Do not copy them.
- Drop CODATA constants for a “better” value. `h`, `c`, `G`, `k_B`, `ℓ_P` live in `src/lib/upi/physics.ts`.
- Invent `imagine_*` tools or native modules that need `apt`.
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

Software_test mirrors that must stay green (see `src/lib/upi/odin.ts` `runMirrors`, `group.ts`, `lie.ts`, `einstein.ts`, `golay.ts`, `dedup.ts`):

1. Planck–Einstein: `f → hf → hf/c² → mc² → E/h` recovers `f` (electron rest as fixture).
2. Lorentz: `Λ(φ)` then `Λ(−φ)` is identity. `so(1,1)` generates the boosts.
3. Einstein map: hyperbola \(E^2 - (pc)^2 = (mc^2)^2\). Rest intercept `m = E₀/c²`. Photon (`m=0`) STOP on rest frame.
4. Golay G24: encode then decode recovers the word.
5. Dedup: chunk → unique store → replay equals bytes. FNV-1a identity is software_test, not SHA-256 of Indaleko.
6. Lie: `so(3)` Jacobi residual ~ 0; `so(11)` dim = 55.

If a mirror fails: **stop coding features**. Patch the mirror. Do not “fix” it by loosening epsilon or deleting the test.

Chain rule (Lab, `chain.ts`):
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
Hydration: `src/lib/upi/hydrate.ts`
Merge-check: `src/lib/upi/merge-check.ts` — STOP without `stop_reason` fails. Unknown keys fail. Relations must be in the closed set:

`DERIVED_FROM, CAUSES, DUAL_TO, EQUIVALENT_WITHIN, COARSE_GRAINS_TO, COMPACTIFIES_TO, EMERGES_AS, FORM_SIMILAR, TOPOLOGY_SHARED, MECHANISM_SHARED, CANDIDATE_BRIDGE, CONTRADICTS, STOPS_AT, REPRESENTS, MEASURED_BY, FALSIFIED_BY`

Write path (owner):
1. Investigate. Paper-quick frame. Confirm the function exists in code **before** adding files.
2. `mergeCheck` locally on the JSON.
3. Run relevant mirrors.
4. Commit to `main` (or owner-approved branch).
5. RNA: pull DNA (`pullDna` in `dna-actions.ts`) so grok.me / preview transcribes.

RNA write functions: `proposeNodeFn`, `proposeBridgeFn`, GitHub issue for external corrections. User-agent `UPI-RNA-engine`.

---

## 5. Keep / drop (productive, not filler)

### Keep (already in the RNA)
- Einstein map, Lorentz inverse, Planck–Einstein composition, chain beads, open-loop STOP.
- GitHub DNA / RNA engine, merge-check, correction desk.
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

Live desk: grok.me Lab → Correction desk. DNA: `data/open-problems/indaleko_160tb_payload_stop.json`. Invite: https://github.com/dpstudio-se/Universal-Physics-Index-UPI/issues/8

| Claim | Cited | Status | Conflict | Closes if |
|---|---|---|---|---|
| Abstract payload | 160 TB, 31M files, 8 platforms | STOP | Body: 16.2 TB used of 35.1 TB capacity, 31.9M files | One sentence naming what 160 TB counts: raw, replicated (`unique = raw / copies`), provisioned, logical, or leftover draft |
| Eight storage platforms | “eight storage platforms” | STOP | Body names more than eight families | The eight names in one table or sentence |
| Activity corpus | 31M-file dataset with memory-anchor queries | STOP | Evaluation used synthetic activity metadata | Which of 160 TB / 16.2 TB is measured files vs generated anchors |

Held (not STOP): body capacity 35.1 TB DER; body used 16.2 TB DER; ArangoDB index 78.6 GB EST (~0.485 % of used).

A correction from a knowledgeable reader is saved as a reply. It does **not** auto-promote the node.

---

## 7. App map (RNA)

TanStack Start, React 19, Tailwind. Auth off. Catalog from DNA + bundled `src/lib/upi/catalog.json` snapshot.

| Route | Job |
|---|---|
| `/` | Ledger home |
| `/catalog` | Nodes |
| `/n/$slug` | Node |
| `/graph` | Force-directed graph |
| `/lattice` | E8 / Golay / Leech software portraits |
| `/symmetry` | Groups + Lie |
| `/holography` | AdS/CFT + RT |
| `/lab` | Einstein map, chain, Odin, Indaleko source map, STOP desk, Dedup, frequency, sonifier |
| `/dna` | Pull / propose / PR walk |
| `/method` | Honesty rules |

Core libs: `src/lib/upi/{physics,einstein,group,lie,golay,chain,odin,indaleko,dedup,hydrate,merge-check,github.server,dna-actions,live}.ts`

---

## 8. Agent workflow (so nothing sabbas)

Before any code:
1. Restate the function in one sentence. If you cannot point at the file that already implements or should implement it, **stop and confirm**.
2. Paper-quick frame: keep / drop / status / which mirror will prove it.
3. Search the repo (`rg`) — extend, do not duplicate.

Then:
4. Smallest patch. Match existing tokens, StatusBadge, chip-row, no new visual system.
5. Run the relevant mirror / `npx tsx` on the function.
6. `npm run typecheck` and `npm run build`.
7. Browser: the change is visible, no console errors, no horizontal overflow at 390px. Do not ask the owner to QA.
8. If DNA JSON changed: merge-check + write `main` + tell RNA to pull.

Auto-debug: if build, typecheck, or a mirror fails, **that is the task**. Patch until the loop closes. Do not leave ERR as a feature.

Deploy lag: after VS Code commits, grok.me updates only when the App Builder / Vercel snapshot rebuilds. If grok.me disagrees with `main`, `main` wins.

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
2. Skim `src/lib/upi/merge-check.ts` and `src/lib/upi/odin.ts` `runMirrors` so you still have the loop.
3. Answer: “I see the mirror: encode→decode (Golay), Λφ→Λ−φ (Lorentz), f→m→f (Planck–Einstein), chunk→replay (dedup). DNA is GitHub main. RNA is grok.me. I will not close STOP with arithmetic.”
4. Then do the asked work.

If you cannot see that function, **do not start coding**. Say what is missing.

End of contract.
