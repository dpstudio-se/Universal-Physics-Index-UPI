# UPI Equation Registry — Fluid Mechanics

| ID | Equation | Status | Domain |
|---|---|---|---|
| FM-001 | ∂ρ/∂t + ∇·(ρv)=0 | EST | Mass conservation |
| FM-002 | ∇·v=0 | EST | Incompressible flow |
| FM-003 | ṁ=ρAv | EST | Mass flow |
| FM-004 | ρ(∂v/∂t+(v·∇)v)=-∇p+μ∇²v+ρg | EST | Navier–Stokes |
| FM-005 | dp/dr=ρω²r | EST | Ideal rigid-body rotation |
| FM-006 | p(r)=p(0)+½ρω²r² | DER | Integration of FM-005 |
| FM-007 | p+½ρv²+ρgh=const. | EST | Bernoulli, stated assumptions |
| FM-008 | F=ṁv_e+A_e(P_e-P_0) | EST | Jet thrust |
| FM-009 | P_jet=½ṁv_e² | DER/EST | Jet kinetic power |
| FM-010 | Re=ρvL/μ | EST | Viscous-flow regime |
| FM-011 | Ma=v/a | EST | Compressibility regime |
| FM-012 | Ẇ_c≈ṁ c_p(T_2-T_1) | DER approximation | Compressor work |

## Control examples

### Example A: 1 kg/s at 3000 m/s
- Thrust from momentum term: 3.0 kN.
- Jet kinetic power: 4.5 MW.

These values are arithmetic consequences of the stated parameters, not experimental measurements.

### Example B: rotating water pressure scale
For density ρ and angular speed ω:
Δp = ½ρω²R².
Use actual fluid properties and measured boundary pressure before making cavitation claims.

## Required metadata
Each equation record should contain:
- symbol definitions
- SI units
- assumptions
- applicability range
- provenance
- uncertainty
- relation graph
- verification state

## Audit rule
No equation is promoted to an anomalous propulsion claim merely because it appears inside a toroidal geometry. Geometry changes boundary conditions; it does not by itself change conservation laws.
