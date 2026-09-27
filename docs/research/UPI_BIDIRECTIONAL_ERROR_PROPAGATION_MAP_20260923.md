# UPI Bidirectional Error Propagation Map

**Date:** 2026-09-23  
**Status:** DER / architecture verification  
**Scope:** UPI calculation, Ω1766 transformation, mirror reconstruction and FL verification.

## Principle

Small input errors should not require a new theory layer. UPI should make the existing chain safer by checking the right quantity at the right location.

\[
INPUT \rightarrow CALC \rightarrow CHECK \rightarrow \Omega_{1766}:T\rightarrow B\rightarrow R
\rightarrow MIRROR \rightarrow FL
\]

The same calculation rule is used in both directions where an inverse is mathematically defined.

## Bidirectional test

\[
f \rightarrow T=1/f \rightarrow E=hf \rightarrow m=E/c^2
\]

\[
m \rightarrow E=mc^2 \rightarrow f=E/h
\]

A perturbation is introduced at an input or intermediate node:

\[
X' = X(1+\delta)
\]

The forward path propagates the perturbation. The reverse path reconstructs the original state where the transformation is invertible.

Residual:

\[
\epsilon = X_{\rm rec}-X
\]

Relative residual:

\[
r = \frac{|X_{\rm rec}-X|}{\max(|X|,X_{\min})}
\]

A declared tolerance determines PASS/STOP. The tolerance belongs to the measurement/calculation being tested and must not be silently changed to rescue a result.

## Error direction

For \(T=1/f\), a positive frequency perturbation produces a negative period perturbation:

\[
\frac{\delta T}{T}\approx-\frac{\delta f}{f}
\]

For \(E=hf,\;m=hf/c^2\):

\[
\frac{\delta E}{E}=\frac{\delta f}{f},
\qquad
\frac{\delta m}{m}=\frac{\delta f}{f}.
\]

This gives UPI an immediate sanity check: the sign and scale of propagated error must agree with the declared transformation.

## Ω1766 placement

\[
\Omega_{1766}=T\circ B\circ R
\]

The error-control rule does not replace T, B or R. It checks each transformation at the location where that transformation is applied.

\[
X\xrightarrow{T}X_T\xrightarrow{B}X_B\xrightarrow{R}X'
\xrightarrow{M_\Omega}X_{\rm rec}
\]

Each node can expose its local residual before the next node is trusted.

## FL rule

FL remains the verification loop, not an additional physical law:

\[
INPUT\rightarrow CALC\rightarrow CHECK\rightarrow
\begin{cases}
CONTINUE,&\text{within tolerance}\\
STOP,&\text{outside tolerance}
\end{cases}
\]

This prevents error propagation without adding an unnecessary evidence layer.

## Evidence classification

- **EST:** ordinary mathematical operations and declared error propagation.
- **DER:** numerical consequences of declared transformations.
- **HYP:** claim that the same architecture is a universal physical law.
- **TEST:** independent measurement or benchmark testing a prediction.
- **STOP:** missing information, failed check, undefined inverse, or unsupported physical identification.

A successful forward/reverse calculation is mathematical/architectural verification. It is not, by itself, experimental proof of a physical interpretation.

## Small-error simulation

Representative perturbations:

| Input perturbation | \(T=1/f\) relative change | \(E,m\) relative change |
|---:|---:|---:|
| +0.0001% | approximately -0.0001% | +0.0001% |
| +0.01% | approximately -0.009999% | +0.01% |
| -0.01% | approximately +0.010001% | -0.01% |

For small perturbations the first-order relation is a diagnostic; exact recalculation remains the final check.

## Design rule

**Do not change the UPI architecture merely because an input contains a small error.**

1. calculate;
2. check locally;
3. propagate only a checked result;
4. mirror/invert where mathematically valid;
5. compare reconstruction;
6. let FL stop the chain at the first failed check.

\[
\boxed{\text{same UPI}+\text{better local control}}
\]

not more layers for the sake of more layers.

## Boundary

The method detects mathematical inconsistency and declared tolerance violations. It cannot establish that an input represents a real physical quantity. That requires the appropriate measurement, calibration, uncertainty model and independent test.
