# PSI27D Navier-Stokes Research Map

Status: `HYP` / research program.

## Purpose

This record maps the proposed Psi27D topological-invariant idea onto UPI without treating the visual model or symbolic equations as established physics.

The research question is:

> Can an explicitly defined invariant on a declared manifold Sigma_1766 embedded in R^27 provide a new, reproducible bound or control relation for vorticity or velocity-gradient growth in 3D incompressible Navier-Stokes flow?

## UPI layers

### DNA: established equations and definitions

Use the existing Navier-Stokes and vorticity definitions as the reference layer:

- incompressibility: div(u) = 0
- Navier-Stokes momentum equation
- vorticity: omega = curl(u)
- velocity gradients and vortex stretching
- energy and regularity diagnostics already represented by UPI

### RNA: dynamic computation

Use the existing dynamic engine for declared frequency-series/control calculations:

- f(t)
- omega(t) = 2*pi*f(t)
- phase accumulation
- velocity field
- vorticity/curl
- Navier-Stokes residual
- particle/control trajectories

These calculations are computational checks under declared assumptions. They are not a general 3D regularity proof.

### HYP: Psi27D

The proposed invariant is a candidate research object:

Psi27D = candidate functional of the flow and an explicitly defined mapping to Sigma_1766 subset R^27.

The mapping is currently undefined and therefore cannot be treated as established mathematics.

## E8 boundary

Do not equate E8 with R^27.

If E8-derived structure is used, define an explicit map:

P: E8_data -> Sigma_1766 subset R^27

and specify:

1. domain and codomain,
2. metric/topology,
3. map properties,
4. invariant definition,
5. units/dimensions,
6. coordinate/gauge dependence,
7. relation to the Navier-Stokes field.

Until these are supplied, the E8-to-R^27 step remains HYP.

## BKM-oriented test

The central numerical target is not visual similarity.

Measure, on independently generated flows:

- ||omega(t)||_infinity
- integral_0^T ||omega(t)||_infinity dt
- ||grad u(t)||_infinity
- Psi27D(t)

Then test whether a nontrivial, reproducible bound involving Psi27D exists.

A useful result would have the form:

||grad u|| <= F(Psi27D, initial_data, nu, boundary_data)

or another rigorously specified continuation-control relation.

A numerical observation that Psi27D stays finite is not by itself a proof of regularity.

## Controls

Every claim must be compared with:

- null model without Psi27D,
- analytic smooth controls,
- resolution refinement,
- timestep refinement,
- perturbation tests,
- ablation,
- independently generated trajectories.

The existing UPI rule remains: a passed software test means the implementation is internally consistent. It does not promote a scientific hypothesis.

## TF1766 / frequency bridge

The existing TF1766 records remain separate.

1.766 Hz is a declared candidate/reference frequency.
7.834125 Hz is a declared resonance-named reference.
0.126 s gives the derived frequency 7.9365079365 Hz.
8 Hz is a declared reference/control endpoint.

These values must not be inserted into the Psi27D regularity claim unless a physical coupling and a mathematical role are independently defined.

The existing TF1766-to-fluid-coupling record remains STOP until a system-specific drive, geometry, measured transfer function and initial/boundary conditions are supplied.

## Falsification first

The hypothesis is weakened or rejected if:

- the invariant cannot be formally defined,
- dimensions do not close,
- the value is not actually invariant under the claimed transformations,
- correlations vanish under controls,
- the result is resolution/timestep dependent,
- or a counterexample breaks the proposed bound.

The goal is therefore not to make the model pass. The goal is to make it survive attempts to break it.
