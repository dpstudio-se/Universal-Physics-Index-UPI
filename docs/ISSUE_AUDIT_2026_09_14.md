# Open-issue audit and publication corrections

This change repairs repository behavior and records bounded mathematical progress. It
does not close an open conjecture or independently certify an external proof. Historical
3I evidence and the selected baseline remain immutable snapshots. The published 3I case
is replaced by its schema-valid, scoped STOP candidate; the original is archived under
`examples/feedback/sources/`. The signed-a vis-viva correction is included.

## #12: triad routing

EST (source inspection): main at `2aa811bf9594a8b4aae06287fa800e65c7f4aa57` contains all
three requested STOP nodes and STOPS_AT bridges. The existing `classify_rna_surface`
function routes those exact records to Catalog + STOP desk and Graph/Catalog. Added
regression controls load the real files, check each bridge target and preserve STOP.
Repository routing is covered; live grok.me hydration is not verified or deployed.
Next observation: read the deployed RNA revision and confirm it has consumed this DNA
revision. Keep the issue open if it includes deployed UI acceptance.

## #8: Indaleko counting identity

EST (source-report domain): [arXiv v1 abstract](https://arxiv.org/abs/2602.20507v1) still
reports 160 TB; [v1 body, Resource Utilization](https://arxiv.org/html/2602.20507v1) reports
35.1 TB capacity, 16.2 TB used and 78.6 GB index. The available submission history lists
v1, not a correcting v2. DER under decimal units: 160/16.2 = 800/81 and
78.6 GB / 16.2 TB = 131/27000, approximately 0.485185%. Those identities are tested.
ERR: interpreting the first ratio as a measured replication factor. STOP: no source
counting identity reconciles the quantities, names the exact eight-platform set and
separates measured files from synthetic activity anchors. Next action: obtain a cited
author correction or inventory/table giving those definitions. No personal corpus ingested.

## #16: Navier–Stokes external claim

EST (publication domain): the [OpenAI release](https://openai.com/index/navier-stokes-solution/)
links a paper and [Lean repository](https://github.com/openai/NavierStokesAndEuler).
Pin for follow-up: `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`; the README specifies
Lean 4.34.0-rc2, Lake and Mathlib. Its stated results concern positive viscosity and
smooth forcing in whole space and the periodic torus, mapped to Clay alternatives C/D.
Do not conflate this with an unforced result. Compare with
[Fefferman's official specification, pp. 1–2](https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf):
divergence-free smooth data, declared forcing decay/periodicity, smooth solution class,
and the whole-space uniform energy requirement must all match.

HYP: the submitted proof meets every formal and mathematical obligation. STOP: no clean
Lean rebuild, axiom/dependency audit, Comparator run or independent theorem-to-Clay
mapping has been completed here. Next action: build the pinned revision in an isolated
Lean environment, record hashes and theorem axioms, then check every hypothesis in the
exported C/D statements. Lack of this audit is not evidence that the external proof fails.

## #17: Riemann Hypothesis

Target: [Clay RH](https://www.claymath.org/millennium/riemann-hypothesis/).
ERR: the existing issue comment says symmetry itself localizes zeros to the critical
strip. DER counterexample: P(s)=(s-1/2)^2-9/4 satisfies P(s)=P(1-s) and has real
coefficients, yet P(-1)=P(2)=0. An exact Fraction regression test checks this; P is not
zeta/xi and is not a counterexample to RH. Thus neither the strip nor the critical line
follows from these symmetries alone. Zeta-specific zero-free arguments are separate
premises. HYP: a suitable positivity or spectral route could exclude off-line zeros.
STOP: no such global exclusion theorem is proved here. Next action: state the exact
positivity functional/operator domain and prove the property without assuming RH.

## #18: P versus NP

Target: [Clay P versus NP](https://www.claymath.org/millennium/p-vs-np/).
DER: checking a supplied n-bit SAT assignment takes time proportional to formula size;
enumerating all assignments introduces a 2^n factor. ERR: equating the verifier's runtime
with a deterministic search bound, or turning a bounded timing benchmark into a lower
bound over all algorithms. HYP: a proposed reduction or circuit argument can close the
gap. STOP: no algorithm/proof candidate establishing a uniform polynomial bound or a
general superpolynomial lower bound is supplied. Next action: specify the machine model,
encoding, quantifiers and candidate lemma, then test reductions for hidden size blowups.

## #19: Yang–Mills

Target: [Clay Yang–Mills](https://www.claymath.org/millennium/yang-mills-the-maths-gap/).
DER: a dimensionless lattice gap g(a)>0 at each spacing does not alone bound a physical
gap g(a)/a away from zero as a tends to zero: the abstract sequence g(a)=a^2 is a
counterexample to that implication. It is not a Yang–Mills construction. HYP: uniform
estimates may survive the continuum limit. STOP: the required continuum QFT construction
and uniform spectral bound are absent. Next action: specify axioms, observables,
renormalization and limits, then prove uniform bounds and reconstruction.

## #20: Hodge

Target: [Clay Hodge conjecture](https://www.claymath.org/millennium/hodge-conjecture/).
DER: an algebraic cycle gives a class through the cycle-class map; existence of this
forward map does not imply it is surjective onto every rational Hodge class. ERR:
silently replacing rational coefficients by integral ones, or reversing a map without
a surjectivity argument. HYP: a selected smooth projective family admits an explicit
cycle construction. STOP: no general construction/surjectivity proof supplied. Next
action: name a variety, codimension and rational class and construct the representing
cycle before generalizing; a symbolic analogy is SYM and does not supply the cycle.

## #21: Birch–Swinnerton-Dyer

Target: [Clay BSD](https://www.claymath.org/millennium/birch-and-swinnerton-dyer-conjecture/).
DER bounded calculation for E: y²=x³-x (discriminant 64): at good primes 3,5,7,
point counts including infinity are 4,8,8, hence a_p is 0,-2,0. Exact enumeration is
tested. These local coefficients do not establish either Mordell–Weil rank or analytic
order of vanishing at s=1. HYP: an explicit theorem chain can certify both for a selected
curve. STOP: certified rank bounds and a rigorous analytic-rank certificate are missing.
Next action: provide descent/generator certificates and a validated analytic calculation,
then state the precise hypotheses of the theorem connecting them. Finite prime counts
and floating-point zeros cannot close the general conjecture.

## Validation and closure boundary

`tests/test_issue_regressions.py` contains software controls for triad routing, the RH
symmetry error, local elliptic-curve counts, decimal corpus ratios and published 3I STOP.
Run the full bound runner after all changes; results are `verification_type: software_test`.
These controls are self-review, not independent scientific verification. Issues #8 and
#16–21 retain their named unresolved obligations; #12 retains external UI verification.
Do not use automatic closing keywords for these issues in the publication PR.
