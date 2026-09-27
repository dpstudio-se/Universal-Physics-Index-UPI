# Typed DNA execution

The reader inventories every JSON file under the selected root, including malformed,
legacy, symbolic and unsupported records. It executes registered, reviewed relations
only. Unknown mathematics remains OPEN in the inventory. This is an extensible typed
adapter engine, not a universal symbolic solver or autonomous PDE discovery system.
Adding a law means registering its input/output roles, exact equation, forward function,
inverse and assumptions. The non-frequency force regression exercises that extension.
An unsupported equation needs an adapter and independent tests before execution.

`main` was inspected at `2aa811bf9594a8b4aae06287fa800e65c7f4aa57` and PR #24 at
`490ad173cef3bfa4798ecd7ebd98be5a9d9a3b00`. This PR builds on PR #22's gates and
reuses the existing `feature/research-mode-shadow-open` implementation. These branches
are proposed changes, not a new canonical baseline. No 3I/ATLAS promotion is performed.

```powershell
python -m upi.cli dna-derive 1.766 --time 0.25 --phase0 0
python -m upi.cli research examples/research/session-8200.json
python examples/feedback/run_validation.py
python -m upi.cli triage data --inspect --known examples/ledger/baselines/known-findings.json
```

The DNA command emits an inventory, source byte hashes/versions, input values,
per-link verification and schema-valid candidate nodes. It does not insert them.
Use a new file per run. The bound suite receipt additionally records the complete
code/source/candidate snapshot and exact collected tests. `PASS` is software behavior;
the CLI can pass a conditional calculation while scientific promotion remains blocked.

## The actual graph

These quantities share an input; they are not a chain of physical causes:

| Relation | Typed input → output | Domain/status | Check |
| --- | --- | --- | --- |
| T=1/f | ordinary f [Hz] → T [s] | f>0, DER | dimensions; f=1/T |
| omega=2 pi f | f [Hz] → omega [rad/s] | f>0, DER | dimensions; f=omega/(2 pi) |
| E=h f | f [Hz] → quantum E [J] | radiation quantum interpretation, conditional DER | dimensions; f=E/h |
| m_eq=h f/c² | f [Hz] → m_eq [kg] | energy equivalent, conditional DER | dimensions; f=m_eq c²/h |
| t_model=t_ref f_ref/f | f,f_ref [Hz], t_ref [Gyr] → t_model [Gyr] | declared model, conditional DER | dimensions; inverse with fixed references |
| phase=2 pi f t+phase0 | f [Hz], physical t [s], phase0 [rad] → phase [rad] | constant f, declared origin, DER | dimensions; recover t |
| phi_n=n×72° | chamber index n → label [degrees] | n=0..4, SYM | partition endpoints, 5×72=360 |
| v=(-Omega y,Omega x,0) | prescribed Omega [s^-1], position [m] → v [m/s] | REDUCED MODEL, conditional DER | spatial derivative and pressure balance |
| curl(v)=(0,0,2Omega) | specified vector field → vorticity [s^-1] | same reduced model, DER | finite-difference curl |
| TF1766 → fluid forcing | hypothesis → measured boundary/coupling | HYP / STOP | missing physical mechanism and measured drive |
| reduced field → general flow | model → boundary/initial-value solution | STOP | geometry, initial/boundary data, constitutive model and solver validation |

`phase` takes physical seconds, never `t_model` implicitly. Chamber labels are not
oscillator phase. m_eq does not determine geometry, density or velocity; a photon's
rest mass is not m_eq. Matching units alone cannot supply those missing identities.
HYP or SYM inputs retain that status in derived values; numerical agreement cannot
promote them to EST. Conflicting supplied outputs are retained and marked STOP.

## TF1766 numerical control

With exact SI h=6.62607015e-34 J s and c=299792458 m/s, f=1.766 Hz gives:

| Output | Value |
| --- | --- |
| T | 0.5662514156285391 s |
| omega | 11.09610525247915 rad/s |
| E | 1.17016398849e-33 J |
| m_eq | 1.3019830273853243e-50 kg |
| t_model | 0.6115515288788222 Gyr = 611.5515288788222 Myr |
| phase at t=0.25 s, phase0=0 | 2.7740263131197875 rad |

The original PR's precise stored values were correct. Regression tests now compute
and compare them; the example record is a snapshot, not a hardcoded implementation.
The tests also use 0.1, 0.5, 2, 5, 7, 7.834125, 8 and 13.12345 Hz. t_model is
strictly decreasing for positive f, with t_model(0.1)=10.8 Gyr and t_model(8)=0.135 Gyr.
Unrepresentable floating-point outputs fail closed rather than emit infinity or zero.

The existing 8 Hz node is reused. The existing memory node is **7.834**, not 7.834125 Hz;
these remain distinct. The new symbolic partition records 7.834125 explicitly.
8−7.834125=0.165875 Hz; no universal constant or resonant coupling follows.

## Reduced flow domain

`reduced_rotation(f,x,y,rho)` assumes a cylinder in established steady rigid rotation,
uniform positive density, no axial flow and a wall prescribed to rotate at Omega=2 pi f.
The local field requires a separately chosen radius R with x²+y²≤R². The wall velocity
is Omega R; p−p0=rho Omega²(x²+y²)/2. Viscous Laplacian and divergence vanish; the
pressure gradient balances convective centripetal acceleration. No body force is needed
for this steady solution. Spin-up, stability, dissipation at other boundaries and generic
Navier–Stokes evolution are not computed. All momentum terms have dimensions m/s²:
partial_t v, (v·grad)v, grad(p)/rho, nu laplacian(v), and body acceleration F.

STOP: no measured TF1766 coupling or physical universal resonance has been supplied.
Next observation: name the driven system, geometry, drive observable, transfer function,
boundary conditions and a preregistered control-spectrum comparison. A source/sink or
spiral radial-flow model needs its own field and conservation checks.

## Review layers

Source binding and schema checks establish repository/adapter consistency. The test
suite establishes software behavior within its inputs. Neither proves Windows isolation,
physical resonance, long-term 3I propagation, or correctness of every catalog claim.
Windows production isolation remains STOP as recorded in WINDOWS_PRODUCTION_ISOLATION.md.
3I/ATLAS remains STOP/BLOCKED with its separate canonical and scientific dependencies.
