# FL terminology

**FL = Feedback Loop**

UPI uses FL as the default shorthand for the general mathematical feedback-loop structure:

\[
x_n \rightarrow F(x_n) \rightarrow x_{n+1}
\]

Extensions:
- **FL-M** = Feedback Loop + independent Mirror verification.
- **FL-V** = Feedback Loop Verification, emphasizing the verification gate.

Mirror comparison:

\[
y_n=A(x_n),\qquad \hat y_n=M(x_n)
\]

\[
\Delta_n=y_n-\hat y_n
\]

Use FL in ordinary UPI discussion. Use FL-M or FL-V only when the additional layer matters. This naming convention does not claim novelty for feedback loops themselves.
