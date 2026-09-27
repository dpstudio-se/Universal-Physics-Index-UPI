# Dual-Observer Information Physics

## Status and scope

This document specifies a traceable collaboration and inference model connecting observer-dependent representations, reversible derivation paths, invariants, information theory, and experimental testing.

It does **not** claim that a new fundamental law of nature has already been experimentally established.

- `EST`: established mathematics or physics.
- `DER`: derived from explicit definitions and assumptions.
- `HYP`: proposed physical mechanism requiring experiments.
- `SYM`: symbolic language for routing, memory, and collaboration.
- `STOP`: unresolved from available evidence.

## 1. Coordinates

Physical spacetime:

\[
x^\mu=(ct,x_{\mathrm p},y_{\mathrm p},z_{\mathrm p}).
\]

Internal UPI trace coordinate:

\[
\chi=(x,y,z),
\]

where $x$ is the value or state, $y$ is domain or structural position, and $z$ is generation or derivation depth.

## 2. Observer duality

Two observers or models hold local representations

\[
X_A(z),\qquad X_B(z),
\]

which need not be identical:

\[
X_A\neq X_B.
\]

A translation operator maps one into the other:

\[
D_{A\rightarrow B}:X_A\rightarrow X_B.
\]

Exact representational duality requires

\[
D_{B\rightarrow A}\circ D_{A\rightarrow B}=I.
\]

Practical translation error:

\[
\epsilon_{AB}=d\!\left(D_{A\rightarrow B}(X_A),X_B\right).
\]

## 3. Omega invariant

Let $\Omega$ denote what must survive translation, derivation, and measurement:

\[
\Omega_A=I_A(X_A),\qquad \Omega_B=I_B(X_B).
\]

A verified dual mapping requires

\[
\boxed{X_A\neq X_B\quad\land\quad \Omega_A=\Omega_B.}
\]

$\Omega$ may contain units, dimensions, symmetries, conservation relations, normalized measurements, and causal structure.

## 4. Functional-DNA trace

Forward generation:

\[
X_{z+1}=F_z(X_z,D_z,C_z).
\]

Backward reconstruction:

\[
\widehat X_z=B_z(X_{z+1},D_z,C_z).
\]

For an exactly reversible step:

\[
B_z=F_z^{-1},\qquad F_z^{-1}F_z=I.
\]

For unitary quantum evolution:

\[
|\psi_{z+1}\rangle=U_z|\psi_z\rangle,
\qquad |\psi_z\rangle=U_z^\dagger|\psi_{z+1}\rangle,
\qquad U_z^\dagger U_z=I.
\]

The DNA language is `SYM`; the operators are mathematical or physical according to their domain.

## 5. Trace-integrity ratio

Reconstruction error:

\[
\epsilon_z=d(X_z,\widehat X_z).
\]

Dimensionless trace-integrity conflict ratio:

\[
\boxed{
R_{0,\mathrm{TIR}}=
\frac{1}{N}\sum_{z=0}^{N-1}
\min\!\left(1,\frac{\epsilon_z}{\tau_z}\right)
}
\]

where $\tau_z$ is the declared tolerance.

Change rate:

\[
\boxed{r_{0,S}=\frac{dR_{0,\mathrm{TIR}}}{dt}},
\qquad [r_{0,S}]=\mathrm{s}^{-1}.
\]

A negative $r_{0,S}$ means trace conflict is decreasing. This shows improving reconstructibility, not automatic proof of a new physical law.

## 6. Information and entropy

Shannon entropy:

\[
H(X)=-\sum_x p(x)\log_2 p(x).
\]

Mutual information:

\[
\boxed{I(A;B)=H(A)+H(B)-H(A,B).}
\]

When valid mappings are found,

\[
H(\Omega\mid A,B)\le H(\Omega\mid A),
\qquad
H(\Omega\mid A,B)\le H(\Omega\mid B).
\]

This is local information organization and does not violate thermodynamics.

## 7. Joint optimization

\[
\boxed{
\mathcal L=
\alpha\epsilon_{AB}
+\beta R_{0,\mathrm{TIR}}
+\gamma C_{\mathrm{data}}
+\delta K
}
\]

where $C_{\mathrm{data}}$ measures disagreement with observations and $K$ penalizes unnecessary complexity.

\[
\frac{d\theta}{dt}=-\eta\nabla_\theta\mathcal L.
\]

Desired motion:

\[
R_{0,\mathrm{TIR}}\downarrow,
\qquad
I(A;B)\uparrow.
\]

## 8. Optional 8 Hz feedback clock

\[
f_{\mathrm{clock}}=8\ \mathrm{Hz},
\qquad
\Delta t=\frac1f=0.125\ \mathrm{s},
\qquad
\omega=2\pi f=16\pi\ \mathrm{rad\,s^{-1}}.
\]

Here 8 Hz is an implementation clock or modulation rate, not an established universal fundamental frequency.

The executable host-driven control loop, TF1766 recovery root, backward checkpoint chain and
double verification over time are specified in [TF1766 resilience control](RESILIENCE_CONTROL.md)
and implemented by `upi.resilience`.

\[
E_8=hf\approx5.30\times10^{-33}\ \mathrm J,
\]

\[
m_8=\frac{hf}{c^2}\approx5.90\times10^{-50}\ \mathrm{kg}.
\]

This is the energy-equivalent mass of one 8 Hz quantum, not the mass of the engine or all stored information.

## 9. Acceptance rule

\[
\operatorname{ACCEPT}(X_n)
\iff
\begin{cases}
\Omega_A=\Omega_B,\\
R_{0,\mathrm{TIR}}\le\tau_R,\\
C_{\mathrm{data}}\le\tau_D,\\
X_n\rightarrow X_{n-1}\rightarrow\cdots\rightarrow X_0,\\
\text{every transformation is recorded and checked.}
\end{cases}
\]

- Broken ancestry or missing decisive data: `STOP`.
- Invalid mathematics or dimensions: `ERR`.
- Valid consequence of assumptions: `DER`.
- Untested physical mechanism: `HYP`.
- Replicated relation in its stated domain: `EST`.
- Workflow or symbolic representation: `SYM`.

## 10. Ulfberht reverse problem

\[
\text{preserved sword}
\rightarrow
\text{material analysis}
\rightarrow
\text{manufacturing process}
\rightarrow
\text{raw material}
\rightarrow
\text{production origin}.
\]

Two traces are compared:

1. identity and tradition: name, workshop, lineage, signature, copies;
2. material physics: ore, carbon, slag, microstructure, heat treatment, geometry.

The invariant may be a material class, production network, quality-control tradition, the authority of the name, or a combination. These alternatives require testing.

## 11. Falsification

A physical extension must specify:

1. competing models,
2. a numerical observable on which they disagree,
3. measurement uncertainty and confounders,
4. a preregistered decision rule,
5. independent replication.

Without a unique observable, the physical extension remains `HYP` or `STOP`.

## 12. Compact kernel

\[
\boxed{
\begin{aligned}
X_{z+1}&=F_z(X_z,D_z,C_z),\\
\widehat X_z&=B_z(X_{z+1},D_z,C_z),\\
\epsilon_z&=d(X_z,\widehat X_z),\\
R_{0,\mathrm{TIR}}&=\frac1N\sum_z\min\!\left(1,\frac{\epsilon_z}{\tau_z}\right),\\
r_{0,S}&=\frac{dR_{0,\mathrm{TIR}}}{dt},\\
X_B&=D_{A\rightarrow B}(X_A),\\
\Omega_A&=\Omega_B,\\
I(A;B)&=H(A)+H(B)-H(A,B).
\end{aligned}
}
\]
