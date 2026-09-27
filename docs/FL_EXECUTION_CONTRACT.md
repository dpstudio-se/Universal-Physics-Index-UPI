# UPI FL Execution Contract

Canonical path:

SOURCE -> A || M -> DELTA -> CLASSIFY -> BRIDGE -> NEXT -> FL

A is primary analysis. M is an independent mirror. M receives source evidence and declared assumptions, but not A's expected answer.

For y=A(x) and yhat=M(x):

Delta = y-yhat

epsilon = ||Delta|| / max(||y||,||yhat||,epsilon0)

AGREE: epsilon <= tau.
CONFLICT: epsilon > tau.
UNKNOWN: required evidence, units, domain, provenance, or checks are missing.

Agreement is not proof of truth. Experimental validation remains separate.

False-convergence guard: shared hidden assumptions or expected answers invalidate independence even when A and M agree.

A successful iteration must emit a durable next_pointer. The loop is incomplete if it only reports PASS without defining the next observation.

Shadow retains conflicts, unknowns, alternate reconstructions, discarded candidates, missing information, and provenance uncertainty.

If used with Omega1766, the transformation may be represented as x_(n+1)=Omega1766(x_n), while FL verification remains external to the transformation.

This contract specifies operational verification architecture, not physical proof of Omega1766 or any processed hypothesis.
