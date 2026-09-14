# Dynamic Spiral Flow

UPI now has a small, deterministic dynamic layer for the spiral-flow test.

## Core relations

For a declared frequency f:

- T = 1/f
- omega = 2*pi*f
- E = h*f
- m_eq = E/c^2

For a time-varying frequency, phase is accumulated:

phi[n] = phi[n-1] + omega[n] * dt

The implementation deliberately keeps the 0.126 s pulse reference separate from
7.834125 Hz:

- 1 / 0.126 s = 7.9365079365 Hz
- 1 / 7.834125 Hz = 0.1276469 s (approximately)

## Three shared-state modes

NavierMode.VELOCITY exposes the rigid-vortex control field.

NavierMode.VORTICITY exposes its exact curl.

NavierMode.NAVIER_STOKES_RESIDUAL evaluates the residual of the declared
Navier-Stokes equation for supplied derivatives/gradients.

The mode switch cycles without resetting the underlying state.

This is a computational verification layer, not a claim of a new physical law,
and the residual helper is not a full Navier-Stokes solver.
