import json
from pathlib import Path

from upi.workflow import (
    validate_handoff,
    validate_ledger_entry,
    validate_routine,
    validate_skill,
    validate_workflow,
)

ROOT = Path(__file__).parents[1]


def _load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_index_triage_contracts_validate() -> None:
    assert validate_workflow(_load("examples/workflows/canonical-merge.workflow.json")) == []
    assert validate_workflow(_load("examples/workflows/index-triage.workflow.json")) == []
    assert validate_skill(_load("examples/skills/index-triage.skill.json")) == []
    assert validate_skill(_load("examples/skills/schema-validator.skill.json")) == []
    assert validate_routine(_load("examples/routines/index-triage.routine.json")) == []
    assert validate_ledger_entry(_load("examples/ledger/index-triage.ledger.json")) == []
    assert validate_handoff(_load("examples/handoffs/index-triage.handoff.json")) == []
    assert validate_handoff(_load("examples/handoffs/schema-validator.handoff.json")) == []


def test_circulation_workflow_declares_governance() -> None:
    assert validate_workflow(_load("examples/workflows/agent-circulation.workflow.json")) == []


def test_governance_owner_must_be_a_declared_role() -> None:
    workflow = _load("examples/workflows/index-triage.workflow.json")
    workflow["governance"]["owner"] = "missing-role"
    errors = validate_workflow(workflow)
    assert any("governance.owner" in error for error in errors)


def test_manager_must_not_share_specialist_capabilities() -> None:
    workflow = _load("examples/workflows/index-triage.workflow.json")
    for role in workflow["roles"]:
        if role["agent_class"] == "manager":
            role["capabilities"].append("cli:debug-index")
    errors = validate_workflow(workflow)
    assert any("share specialist" in error for error in errors)


def test_handoff_rejects_same_owner() -> None:
    handoff = _load("examples/handoffs/index-triage.handoff.json")
    handoff["next_owner"] = handoff["from_owner"]
    errors = validate_handoff(handoff)
    assert any("must differ" in error for error in errors)
