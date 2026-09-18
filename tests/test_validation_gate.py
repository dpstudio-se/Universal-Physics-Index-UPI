from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from upi.validation_gate import dna_update_proposal, validate

def test_all_gates_pass_without_dna_mutation():
    result=validate(reproducible=True,dimensional_consistency=True,no_escape=True,falsification_survived=True)
    assert result.passed
    assert result.decision=="PROPOSAL"
    assert dna_update_proposal(result,"candidate")["writes_dna"] is False

def test_failed_gate_stops_promotion():
    result=validate(reproducible=True,dimensional_consistency=True,no_escape=False,falsification_survived=True)
    assert not result.passed
    assert result.decision=="STOP"
    assert dna_update_proposal(result,"candidate")["writes_dna"] is False
