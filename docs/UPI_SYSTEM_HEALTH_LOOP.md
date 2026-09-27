# UPI System Health Loop

The health loop keeps the UPI toolchain, workflows, skills and governance paths
observable and testable.

## Control loop

SOURCE -> AUDIT -> TEST -> REPORT -> REPAIR QUEUE -> HUMAN REVIEW -> MERGE -> AUDIT

The loop is fail-closed: a missing expected component or failed verification
produces STOP rather than silently promoting a repair.

## Scope

- Python tooling under `src/` and `tools/`
- GitHub workflows under `.github/workflows/`
- UPI governance and research documentation
- OCR / image-decode research entry points
- tests and linting

## Evidence boundary

The health loop verifies system integrity. It does not turn a hypothesis,
reconstruction, AI-transformed image, or symbolic model into established
physics.

## Repair rule

Automated findings create a concrete repair target. Changes remain subject to
the repository's existing review and merge controls.

## Manual run

```bash
python tools/upi_system_audit.py
python -m pytest tests -q
ruff check src tests
```
