# T€@X model laboratory v1.0

The local UPI app serves a Swedish, responsive laboratory at `/lab`. Start with
`upi serve --host 127.0.0.1 --port 8080` and open http://127.0.0.1:8080/lab.
In a Windows checkout with an existing virtual environment, use
`.venv/Scripts/python.exe -m upi.cli serve --host 127.0.0.1 --port 8080`.
This is the local package UI; deploying the external RNA explorer is separate.

![Desktop view of the model laboratory](ui/teax-lab-v1.png)

## Included in v1

- Frequency presets and editable frequency with energy, energy-equivalent mass,
  inverse frequency and relative round-trip error. The positive supported range
  is 1e-100 through 1e100 Hz; zero is discussed as a limit.
- Conditional 27D to 4D compactification calculator. In natural units and a common
  length unit L, G27 has units L^25, V23 L^23, G4 L^2, and both curvature and
  cosmological constants L^-2. No conversion to observed SI G4 is implied.
- Golay [24,12,8] correction-radius explorer. It visualizes a guarantee; it does
  not encode or decode codewords or simulate a physical correction mechanism.
- Local JSON download containing inputs, units, constants, results, assumptions,
  STOP reasons, next observations and falsification conditions. Input is not sent
  to the server. The settings panel can save parameters in this browser or import
  an export. Reset restores the example; Clear saved parameters removes persistence.
- Keyboard-accessible controls, labeled outputs, inline input errors, responsive
  layout, and no remote fonts, scripts or runtime dependencies.

Static web-host deployment and the one-command updater are documented in
[One.com UI publishing](ONE_COM_UI.md).

## Mathematical scope

DER: E = hf, m_E = E/c^2 and f = m_E c^2/h close for a specified quantum energy.
The mass is energy-equivalent mass, not photon rest mass. The inverse is a
consistency check, not independent physical evidence.

HYP: The 27D Einstein–Hilbert plus scalar-field action is a proposed ansatz.
For a fixed, unwarped product M4 x K23 with no additional vacuum contributions,
integration gives G4 = G27/V23 and Lambda4 = Lambda27 - <R_K>/2 (DER).
STOP: internal geometry, stabilization and vacuum potential are unspecified.
Next observation: specify K23, its metric and stabilizing potential.

DER: Minimum code distance 8 guarantees correction of at most 3 bit errors.
STOP: a field-to-code map, correction dynamics and energy budget are missing.
Next observation: define encoding and transition rates with energy exchange.
Neither this code bound nor the frequency round trip establishes dS/dt <= 0.

ERR: This ansatz alone does not guarantee singularity freedom. Schwarzschild
x a flat T23 remains a counterexample when potentials and Lambda27 vanish.
E8 roots, lattice dimensions and spacetime coordinates are distinct quantities;
the proposed 27 dimensions are not selected by the mass bridge or the code.

References: [Tong, general relativity](https://davidtong.org/teaching/general-relativity/),
[Tong, compactification](https://www.damtp.cam.ac.uk/user/tong/string/string.pdf),
[Brown, coding theory notes](https://www.math.brown.edu/~res/MathNotes/notes11.pdf).

## Reproduction and failure conditions

`verification_type: software_test` throughout. Run:

```text
node --test tests/test_lab_math.cjs
pytest tests/test_lab_ui.py
ruff check src tests
mypy src/upi --ignore-missing-imports
```

Expected: at 377 Hz, E = 2.49802844655e-31 J and m_E approximately
2.779431491077391e-48 kg; inverse error below 1e-12. G27=12, V23=3,
Lambda27=2, <R_K>=6 gives G4=4 and Lambda4=-1. Three bit errors remain inside
the correction guarantee; four are outside. Blank/non-finite/out-of-range
inputs must clear numerical results and disable export.

Browser control: open `/lab`, change all controls, export JSON, reset, check
keyboard navigation, and inspect desktop and 390px mobile layouts. HTTP tests
establish delivery only; they do not establish rendering or connector behavior.
Any mismatch against these controls falsifies the relevant software result.

On restricted Windows environments use a fresh workspace `--basetemp` path and
`-p no:cacheprovider` if the default pytest temporary directory is inaccessible.

## Observed verification, 2026-09-08

EST, working tree based on `b2663cb0d9296cb616865d93d549a44159867601`:
154 main-package Python tests and 4 Node calculation tests pass. Ruff and mypy
pass. Python 3.14.7 and Node 26.7.0 were used. The wheel builds offline and
contains all four laboratory assets; this does not establish the CI version matrix.

EST, Edge browser control via DevTools: the 1440px desktop and 390px mobile
layouts render without horizontal overflow. Frequency presets, invalid-input
clearing/export disabling, reset, the 3/4-bit boundary, and JSON Blob contents
pass. No JavaScript exceptions were observed. Screenshots were visually inspected.
Export content was inspected by intercepting the Blob; operating-system download
completion was not tested. The browser required an isolated headless profile with
its sandbox disabled in this restricted environment; this is not an application
runtime requirement. External RNA deployment and physical experiments were not run.
