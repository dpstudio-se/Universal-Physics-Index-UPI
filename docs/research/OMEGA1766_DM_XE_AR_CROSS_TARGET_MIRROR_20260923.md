# Ω1766 Dark-Matter Cross-Target Mirror — 2026-09-23

Status: DER / TEST / HYP / STOP-GATED
Parent workflow: docs/research/OMEGA1766_0D_11D_27D_UNIFIED_WORKFLOW_20260923.md

## Purpose

Record the complete locked-parameter cross-target test developed from the Ω1766 7.834125 Hz → 84-octave → 626.694334 GeV branch. The test is an auditable model comparison, not a claim of dark-matter discovery.

## 1. Locked frequency-to-mass branch

f0 = 7.834125 Hz
N = 84
f84 = f0 * 2^84
   = 1.5153401578541531e26 Hz

E84 = h*f84
   = 1.0040750187053692e-7 J
   = 626.6943340688922 GeV

mχ = E84/c²
   = 1.1171841258445671e-24 kg
   = 626.6943340688922 GeV/c²

Classification: DER, conditional on declared 84-octave scaling.

## 2. Elastic recoil mirror

For target nucleus A:

μ = mχ*mA/(mχ+mA)
ER = (μ² v²/mA)(1-cosθ)

Using the locked mχ:

At v = 361 km/s:
Xe: 248.302279 keV
Ge: 159.829 keV
Ar: 96.156 keV
Si: 69.910 keV

At v = 600 km/s:
Xe: 685.913 keV
Ge: 441.513 keV
Ar: 265.623 keV
Si: 193.121 keV

For ER = 248 keV, the required speeds are approximately:
Xe 360.8 km/s
Ge 449.7 km/s
Ar 579.8 km/s
Si 679.9 km/s

These are kinematic consequences of the locked mass, not event-rate predictions.

## 3. Exothermic mirror branch

For the simplified zero-velocity line:
ER^(0) = |δ| mχ/(mχ + mA)

Lock Xe to ER = 248.000 keV and mχ = 626.694334 GeV.

Solving gives:
δ = -296.3969 keV

Mirroring the same mχ and δ to argon gives:
ER,Ar^(0) = 279.7841 keV

Important correction:
Earlier working notes used δ ≈ -299.96 keV and ER,Ar ≈ 281.98 keV. Those values are ERR and are superseded by the full-precision mirror calculation above.

## 4. Exothermic velocity relation

vmin(ER) =
|mA*ER/μ + δ| / sqrt(2*mA*ER)

The central exothermic line has vmin = 0 in the idealized zero-width relation. The halo velocity distribution broadens the observable spectrum.

A complete event-rate prediction still requires:
- interaction operator/cross section
- halo model
- nuclear response/form factor
- detector exposure
- detector efficiency/acceptance
- resolution and analysis window

Do not fit independent normalizations for Xe and Ar.

## 5. UPI falsification rule

The following parameters are locked across targets:
mχ
δ (for exothermic branch)
declared halo parameters
declared interaction operator
declared normalization

Allowed target dependence:
mA
nuclear response/form factor
detector response

Forbidden:
retuning mχ or δ separately for each detector merely to recover a feature.

## 6. Evidence classification

EST:
- LZ reports a 248 ± 23_stat ± 23_sys keV nuclear-recoil candidate in its 2.84 tonne-year result.
- LZ reports global significance 2.6σ after look-elsewhere treatment; this is not a confirmed dark-matter discovery.

DER:
- 7.834125 Hz × 2^84 → 626.694334 GeV.
- Fixed-mass elastic recoil kinematics.
- Fixed-mass/fixed-splitting exothermic target mapping.

HYP:
- 626.694334 GeV represents the microscopic dark-matter sector.
- The Ω1766 frequency scaling has physical rather than model-defined significance.

TEST:
- Cross-target recoil locations and spectra under one locked parameter set.

STOP:
- Absolute event rate without an explicit interaction operator, normalization, detector response, and uncertainty model.
- Claiming physical 27D/11D interpretation without an explicit action/metric/field construction.

ERR:
- Superseded exothermic values δ≈-299.96 keV and Ar≈281.98 keV.

## 7. Forward / mirror chain

FORWARD:
7.834125 Hz
→ 2^84
→ 626.694334 GeV
→ locked mχ
→ Xe 248 keV constraint
→ δ = -296.3969 keV
→ Ar 279.7841 keV line
→ full recoil spectrum
→ independent target data

REVERSE:
target recoil
→ infer allowed mχ, δ under declared operator
→ compare with 626.694334 GeV
→ infer f84 = mc²/h
→ divide by 2^84
→ recover 7.834125 Hz

## 8. Required next UPI gate

Build a reproducible dR/dER engine with:
1. explicit interaction operator;
2. normalized halo integral η(vmin);
3. target-specific nuclear response;
4. detector response;
5. one shared normalization;
6. Xe calibration/constraint;
7. blind Ar prediction;
8. independent-data comparison;
9. residual calculation;
10. FL-M mirror verification.

Promotion to physical support requires agreement with independent data within declared uncertainties and without target-specific parameter retuning.

