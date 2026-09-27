# UPI Chamber Integrity Protocol v1

The intended mechanism is to contain candidate edits in a work chamber and compare
them with a protected, version-bound expectation before human review. The executable
core is `src/upi/chamber.py`. It reads supplied byte snapshots and never writes files,
updates anchors, restores canonical content or performs promotion.

## Implemented boundary

`draft_manifest` prepares an **untrusted proposal** containing chamber identity,
candidate version/status, schema version/hash, exact content hash, normalized JSON
hash, invariant specification hash, predecessor manifest hash and dependency hashes.
It does not approve that proposal. A separately configured `TrustAnchor` pins the exact
manifest hash, chamber, schema version and deployed validator identity.

`verify_chamber` compares expected/current hashes, checks the predecessor chain to
genesis, requires the exact dependency inventory, validates the protected schema and
runs a trusted domain callback. Missing inputs, changed artifacts, malformed JSON,
unknown/failed domain results and callback failures retain STOP. Remote schema
references are disallowed. Duplicate JSON keys and nonfinite numbers are rejected.

Byte integrity and normalized JSON identity are separate results. Formatting-only
changes retain normalized identity but fail an exact byte expectation until reviewed.
The normalization is the versioned Python JSON serialization profile in this module,
not RFC 8785, semantic equivalence of equations, or physical evidence. Invariant hashes
identify specifications; the callback actually checks the declared domain. The existing
signed-a adapter is bounded to its recognized energy/periapsis equations and does not
validate arbitrary physics or long-term trajectories.

A successful local CIP result means AWAITING_HUMAN_REVIEW **for this component only**.
It preserves HYP/DER/etc. and does not override the case gate. Dependency identity is
not claim evidence. The existing promotion service now requires `chamber_integrity`
alongside physics, canonical, software_tests and status_promotion. Missing policy
blocks. Configure it with `promotion_check(load_review)` in server-owned policy code;
the loader must obtain fresh trusted snapshots on every invocation. The adapter
binds reviewed normalized content to the exact promotion target, including status.
The existing server reruns policy checks before its atomic database update and
requires its human-decision receipt. No production CIP trust anchor is installed here.

## Trust deployment remains STOP

EST: the checker and its tests execute inside this repository. DER: these checks can
detect accidental drift against an unchanged anchor. They cannot protect against a
writer who can replace the anchor, deployed validator and checks together. A validator
version string is a trusted deployment assertion, not proof of independent execution.

STOP reason: no separate verifier identity, protected anchor store, agent-denied
canonical permissions or independent human authentication has been deployed by this
change. Smallest next action: select the verifier service account and canonical/anchor
storage location, then enforce and test an access matrix: agent writes candidates
only; verifier reads candidates and protected policy; authorized human/promotion
service controls anchor acceptance and canonical writes. Pin the deployed code digest
outside the agent's workspace. A shared bearer token with a human-decision field is
not proof that a human, rather than an agent holding that token, made the decision.

Hash-linked history is tamper-evident only relative to the protected head. This version
checks manifest ancestry, not signatures or historical scientific validity. Supplied
dependency hashes identify content, not their canonical acceptance. The separate
canonical and claim gates must still run. Cross-resource dependency changes require
immutable content-addressed snapshots or transactionally enforced version checks in
the deployed promotion service; an in-process callback alone provides no distributed
transaction or OS containment guarantee.

Recovery design: select a previously protected, accepted manifest, verify its complete
content/dependency snapshot, restore into a NEW candidate chamber and rerun all gates.
Automatic destructive rollback and a protected snapshot service are not implemented.
No claim is made that an agent can currently damage only its own directory.

## Reproduction and falsification

Run `.venv\Scripts\python.exe examples/feedback/run_validation.py` from the repository
root. Its receipt binds the current source, candidate, tests and documentation; every
test outcome is `verification_type: software_test`. Tests exercise content+manifest
rewrites against an unchanged anchor, wrong vis-viva despite matching hashes, altered
dependencies/history, cross-chamber history, ambiguous JSON, callback failures and
promotion target substitution/revalidation. Accepting any of those negative controls
would falsify the claimed software boundary. These are not independent physics proofs.

The 3I/ATLAS case retains its separate STOP/BLOCKED result. This change does not alter
the canonical baseline, resolve its 21 mixed review items, or deploy a propagation model.
