# Ω1766 / UPI rotating self-debug workflow

Automatic repair is now modeled as a bounded rotating loop:

`OBSERVE → DEBUG → PATCH → TEST → VALIDATE → UPDATE → ROTATE → OBSERVE`

The UPI control layer governs sequencing, retry bounds, rollback on failed tests or validation, and an immutable DNA boundary. The host supplies the real debugger, patch executor, test runner, rollback implementation and update sink.

A successful cycle produces an auditable update **proposal**, never a direct DNA write. Every proposal remains `verification_type=software_test`.

Recommended live adapter:

`Odysseus/agent → debug → SelfPatchLoop → patch in isolated branch → tests/CI → validation → proposal → GitHub review → merge → next observation`

STOP conditions include rejected patch, failed tests without rollback, failed validation without rollback, direct DNA-write request, or exhausted repair cycles.

This is software governance, not an assertion that an autonomous system is scientifically self-validating.