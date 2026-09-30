# JKAI Grundlag-vakt

## Purpose and authority boundary

`upi.jkai_grundlag_vakt.JKAIGrundlagVakt` is a fail-closed software gate for
proposed changes to a governance/root policy. It checks version lineage, supplied
legal-source metadata, declared rights-impact scope, and a human-review receipt.
It does **not** interpret Swedish law, determine constitutionality, authenticate
users, approve policy, or apply a change.

`Ω7834` (root owner) → `Ω7934` (reviewer) are symbolic role labels only. They grant
no account, credential, or permission. Authentication and authorization must be
implemented by a separate, explicitly reviewed identity system before these labels
can be bound to real users.

## Conceptual constitutional review flow

The proposed “root / chambers / feedback loop” is an architectural metaphor for
traceable review, not a claim that law is a closed mathematical system:

1. **Constitutional reference layer:** use the currently applicable constitutional
   text as the highest-level legal reference for the review. TF 1766 is historical
   context, not the operative text. This software can pin reference identifiers
   and provenance, but cannot make legal rules immutable or derive every result
   from them mechanically.
2. **Ordinary-law and case layer:** record statutes, decisions, administrative
   actions, facts, and the authority's stated legal basis as a separate,
   time-specific chain. They are review inputs, not edits to the constitutional
   reference layer. Whether a particular rule is subordinate, applicable, or
   valid is a legal question, not inferred from its position in a software tree.
3. **Review chambers:** when a possible restriction is raised, record who acted,
   what measure and right are involved, the asserted legal basis and reasons,
   relevant sources, and materially different perspectives. A missing basis or
   explanation is an open review question; this gate does not decide the formal
   burden of proof, which depends on the legal rule and proceeding.
4. **Bidirectional trace:** trace backward from the measure to its stated
   authority, provisions, sources, and facts; then trace forward to the claimed
   purpose, impact, and countervailing rights. Preserve conflicting or incomplete
   branches with provenance instead of silently deleting them. Return a trace
   report for human review, not a legal ruling.

An unresolved constitutional concern may hold a **policy/configuration
deployment** for human review. It must not make this monitor pause, suppress,
rewrite, or delay the underlying press/publication. That boundary is enforced as
a project design requirement in `PublicationInterferenceGuard`; it does not
claim to enforce an external system that is not integrated with the guard.

The contribution server now calls the monitor when it emits a live contribution
event and includes the audit result in that event. This integration observes only
the server's event metadata and its own publication action; it cannot tell whether
an upstream AI refused a request or altered content before submission. A `CLEAR`
result is therefore not proof of end-to-end absence of censorship. The actual AI
response/publishing pipeline still needs to emit explicit refusal, withholding,
redaction, delay, or access-restriction events to the guard, with a durable,
authorized audit trail.

An adapter can submit such a report to `POST /api/publication-audit` as JSON:

```json
{
  "event_id": "model-output-42",
  "action": "redaction",
  "press_or_publication_context": true
}
```

Allowed actions are the `PublicationAction` values. Set the context to `null`
when uncertain; an intervention in an uncertain context is flagged. The endpoint
returns the audit disposition and broadcasts a `publication-audit` SSE event.
It does not receive article text, reject or rewrite a publication, or verify the
reporter's identity. It is an adapter hook, not automatic model monitoring:
the external AI client must call it when it observes a relevant event.

Symbolic identifiers such as `Ω1766` and values such as `7.83125 Hz` are labels
only. They are not credentials, legal authority, or mechanisms that change
authorization or computation. Access control requires a separate identity
provider and ordinary security review.

## Analysis of the supplied four-panel illustration

The user-supplied image is a pedagogical systems diagram titled “Hur geopolitik
& byråkrati mätbart drabbar folket.” Its four panels retain a shared flow:
external geopolitical pressures feed into an infrastructure or service
chokepoint; valves, friction, secrecy, or oversight affect the flow; a
“tryckfallsreaktion” / “tryckförlust i periferin” is connected to consequences
for people and groups. The pictured variants label different intermediary
systems, including a data hub, Norway/VVS, Finland/building construction, and
shield/spare parts. Fine print and causal details in the image are not treated
as verified facts.

For JKAI, this can be used as a **candidate causal map**, not as a finding:

- **Observation (EST, limited to the artifact):** the illustration repeats a
  common infrastructure-to-people pathway across four scenario variants and
  labels intermediate bottlenecks and a press/flow-loss stage.
- **Interpretation (HYP):** dependency concentration or administrative
  intervention could mediate an external shock into reduced access to
  information or services, with downstream effects on people. The graphic
  supplies no measured time series, operational definitions, source citations,
  or comparison group to establish that causal claim or that the effect is
  “measurable.”
- **Competing explanations:** the depicted effect could instead arise from
  direct infrastructure damage, ordinary capacity limits, independent policy
  decisions, or an inaccurate/nonrepresentative scenario. These branches must
  remain open until evidence discriminates among them.

To turn one panel into an auditable case, record the exact scenario and
jurisdiction; identify each physical or administrative link and its source;
define the measured outcome and time window; compare against a baseline or
null model; trace both forward to the claimed impact and backward from the
impact to the alleged cause; and preserve contradictions and missing links.
The four illustrated variants are not four independent replications merely
because they appear in separate panels. Use current TF/YGL/RF text when making
present-law claims; the image's “TF 1766” label is historical context, not a
current-text citation. Do not treat the illustration as evidence that a legal
violation or censorship occurred.

## Review contract

Every proposal declares:

- the parent generation and exact parent-state SHA-256;
- the proposed state, which the guard hashes using canonical JSON; the parent
  checkpoint stores a canonical snapshot so later mutation of the caller's
  original mapping cannot silently change the root digest;
- its rights-impact classification and exact provisions asserted to be relevant;
- primary-source citations, official HTTPS URLs, retrieval dates, and source hashes;
- a review receipt confirming that the source text was checked and disagreement
  was considered, and listing the exact source hashes reviewed.

The software checks URL host against the configured-in-code official source domains
(`riksdagen.se` and `regeringen.se`), metadata presence, and whether the cited
provisions cover the provisions supplied by the proposer. It does not fetch or
cryptographically verify the remote source bytes. A source hash is provenance
metadata supplied by the caller, not proof that the source is current or authentic.
The reviewer must verify the actual official text and exact provisions.

Statuses are workflow dispositions, not legal conclusions:

- `STOP`: required metadata is missing, malformed, based on a stale root lineage,
  or does not cover the declared provisions.
- `REVIEW_REQUIRED`: structural/source metadata passes but there is no complete
  human review receipt.
- `REVIEW_RECORDED`: the symbolic reviewer receipt is complete. This still does
  not authorize or apply the change.

Every result has `legal_conclusion="NOT_DETERMINED"` and
`canonical_apply_allowed=False`. The caller must retain the proposed and current
states separately until a distinct human authorization and persistence workflow
exists. Software test results are `verification_type: software_test`.

## AI publication-interference monitor

`PublicationInterferenceGuard` separately audits runtime event metadata for
possible AI interference with press or publication. Refusal, withholding,
redaction, delay, access restriction, another intervention, or uncertain
publication context is flagged for human review. Incomplete event metadata also
requires review. The event record contains action/context metadata, not article
text; the caller should retain the original publication and link the event to
its own authorized audit record.

This monitor does not semantically inspect model responses, observe a runtime
pipeline by itself, determine whether an act is legally censorship, or enforce a
publication system's behavior. It returns a project-policy signal:
`automated_publication_block_allowed=False` and
`publication_must_remain_available=True`, including for a flagged event. An
adapter must call the monitor for every relevant output/publication event and
honor those fields; durable logging, alert delivery, and integration tests for
the real publishing path remain deployment responsibilities. This is a
conservative UPI governance rule, not a claim that Swedish law has no exceptions
or that the monitor can apply legal remedies.

## Legal source anchors

The following are starting points for source collection, not timeless or
self-executing interpretations:

- Current Tryckfrihetsförordning, SFS 1949:105:
  <https://www.riksdagen.se/sv/dokument-och-lagar/dokument/svensk-forfattningssamling/tryckfrihetsforordning-1949105_sfs-1949-105/>
- Current Yttrandefrihetsgrundlag, SFS 1991:1469:
  <https://www.riksdagen.se/sv/dokument-och-lagar/dokument/svensk-forfattningssamling/yttrandefrihetsgrundlag-19911469_sfs-1991-1469/>
- Current Successionsordning, SFS 1810:0926:
  <https://www.riksdagen.se/sv/dokument-och-lagar/dokument/svensk-forfattningssamling/successionsordning-18100926_sfs-1810-0926/>
- Regeringsform, SFS 1974:152:
  <https://www.riksdagen.se/sv/dokument-och-lagar/dokument/svensk-forfattningssamling/kungorelse-1974152-om-beslutad-ny-regeringsform_sfs-1974-152/>

The retrieved Riksdag pages reported amendments through 2022 when checked on
2026-09-30 for TF, YGL and RF; the Successionsordning page identifies its 1979
reprint and must also be checked for later changes. Therefore, the guard
intentionally requires reviewers to confirm the current text during each review
instead of claiming those snapshots are current. TF 1766 is historical context,
not the present text of TF. Legal conclusions, including voting thresholds or
whether a change is ultra vires, require provision-specific primary-source
analysis and qualified human review.

## Three-step mathematical mirror (separate symbolic branch)

The vortex language is a `SYM` analogy and does not establish a legal invariant.
Allow an axisymmetric, z-dependent pure-swirl field
`u = v(r,z,t) e_theta`, with `u_r = u_z = 0`. Here `v` denotes the azimuthal
speed `u_theta`. The following are kinematic identities; a chosen field must
still satisfy the momentum equations and its boundary conditions to be a
Navier-Stokes solution.

1. Incompressibility holds because the field has no radial or axial component
   and no azimuthal dependence. Its vorticity is
   `omega = -d_z(v) e_r + (1/r) d_r(r v) e_z`; thus z-variation adds radial
   vorticity `omega_r = -d_z(v)` as well as the axial component.
2. The vortex-stretching term is now
   `(omega . grad)u = (v/r) d_z(v) e_theta`, which need not vanish. For example,
   with `v = U(r,t) [1 + epsilon cos(k z)]`, it is
   `-(epsilon k/r) U^2 [1 + epsilon cos(k z)] sin(k z) e_theta`.
   This term changes vorticity locally; it does not by itself imply radial
   expansion, since `u_r` is still zero.
3. To model radial transport or a changing outer radius, specify a meridional
   flow (`u_r` and possibly `u_z`), forcing, viscosity, and wall/end conditions,
   then solve the incompressible momentum and continuity equations together.
   Between infinitely long concentric cylinders (or with periodic axial
   boundary conditions), the z-independent Couette solution remains the special
   stationary case `v = A r + B/r`, with
   `A = (Omega_R R^2 - Omega_0 r_0^2)/(R^2-r_0^2)` and
   `B = r_0^2 R^2 (Omega_0-Omega_R)/(R^2-r_0^2)`; its axial vorticity is
   `omega_z = 2A`. Neither this special solution nor a nonzero stretching term
   establishes stability for arbitrary Reynolds number, disturbances, or
   boundary conditions.

No radial return-energy law or stability bound follows from the user's prompt
alone. Those require fluid properties, geometry, forcing, wall conditions, and a
specified turbulence/feedback model. The legal guard and this mathematical mirror
remain separate branches.
