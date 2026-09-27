# UPI Mathematical Foundation Library: Awesome Math Books

Source repository: https://github.com/valeman/Awesome_Math_Books

Use in UPI: mathematical reference map, not evidence for any physical hypothesis.

## Purpose

UPI uses this catalog as a discovery layer for established mathematical methods that can be applied to derivations, verification, numerical analysis and hypothesis testing. The catalog is a source map. Individual books must still be checked directly before a specific theorem, definition or derivation is cited as support.

## UPI mapping

| UPI area | Mathematical foundation | Example sources in catalog | UPI role |
|---|---|---|---|
| Analysis | limits, continuity, differentiation, integration, rigorous real analysis | Rudin; Kolmogorov & Fomin; Apostol; Piskunov | EST input / DER |
| Linear algebra | matrices, vector spaces, eigenvalues, multidimensional geometry | Bellman; Shilov; Gantmacher; Efimov | EST input / DER |
| Differential equations | ODEs, PDEs, boundary-value problems, variational methods | Pontryagin; Elsgolts; Vladimirov | EST input / DER |
| Fourier / harmonic analysis | Fourier series, transforms, generalized functions | Tolstov; Vladimirov; Gelfand–Shilov | EST input / DER |
| Probability | probability spaces, random variables, stochastic processes | Kolmogorov; Gnedenko; Feller; Markov | EST input / TEST |
| Information theory | entropy, information measures, coding/inference foundations | Yeung; MacKay | EST input / DER / TEST |
| Optimization | convex optimization and numerical optimization | Nemirovski; Kochenderfer & Wheeler | EST input / DER |
| Mathematical physics | mechanics, mathematical-physics equations, generalized functions | Gantmacher; Zeldovich; Vladimirov | EST input / DER |
| Machine learning | statistical learning, probabilistic ML, inference | Bishop; Murphy; Shalev-Shwartz & Ben-David; MacKay | EST input / TEST |
| Geometry/topology | analytic geometry, differential geometry and topology | Pogorelov; Mishchenko & Fomenko | EST input / DER |
| Number theory / discrete mathematics | number systems, combinatorics, induction, number theory | Hardy & Wright; Fomin; Vilenkin | EST input / DER |

## Ω1766 / FL use

The catalog is useful for the existing Ω1766 workflow:

claim → mathematical formulation → derivation → dimensional/unit check → mirror/inverse check → numerical test → independent test

For an Ω1766 claim, the book catalog can supply the mathematical machinery without automatically promoting the physical interpretation.

Example:

- Fourier transform theorem: EST mathematical input.
- Applying Fourier analysis to a declared Ω1766 state representation: DER, if the mapping is explicitly defined.
- Claim that the resulting spectral structure is a new physical law: HYP/TEST.
- Self-inversion alone: mathematical consistency, not experimental validation.

## Priority foundation stack

For current UPI work, prioritize:

1. Kolmogorov & Fomin / Rudin / Apostol for analysis and rigorous derivation.
2. Gantmacher / Shilov / Bellman for matrix, operator and spectral structures.
3. Tolstov / Vladimirov / Gelfand–Shilov for Fourier and generalized-function machinery.
4. Kolmogorov / Gnedenko / Feller / Markov for probability and stochastic processes.
5. Gelfand–Fomin / Elsgolts for variational methods and differential equations.
6. Nemirovski / Kochenderfer–Wheeler for optimization and quantitative bounds.
7. Yeung / MacKay for information-theoretic quantities.
8. Gantmacher / Zeldovich / Vladimirov for mathematical-physics connections relevant to Ω1766 and Navier–Stokes research.

## Evidence rule

A reference in this catalog does not establish an Ω1766 physical claim.

UPI keeps the evidence classes separate:

- EST: established mathematics or experimentally established input.
- DER: valid mathematical consequence of declared assumptions.
- TEST: prediction or quantitative relation submitted to independent data.
- HYP: new physical interpretation or mechanism.
- STOP: derivation reaches an unsupported assumption or missing proof obligation.
- SYM: symbolic/architectural notation.

The same evidentiary standard is applied to Ω1766 and established models for the same type of claim.

## Provenance

This document records the catalog as an external mathematical reference index. It does not copy the catalog wholesale and does not treat the repository's ratings or descriptions as UPI evidence.

Last mapped: 2026-09-23.
