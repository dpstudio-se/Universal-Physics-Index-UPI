"""Universal Physics Index (UPI) - machine-readable scientific knowledge graph."""

__version__ = "1.0.0"
__author__ = "UPI Contributors"
__license__ = "MIT"

from .constants import (
    AMPLITUDE_TOLERANCE_DEFAULT,
    EPSILON_Z_DEFAULT,
    K_B,
    N8_REFERENCE_HZ,
    N_A,
    PHASE_TOLERANCE_DEFAULT,
    C,
    E,
    H,
)
from .debug import generate_debug_report, render_debug_markdown
from .dual_observer import (
    DualObserverTraceResult,
    Event1D,
    dual_observer_trace,
    inverse_lorentz_transform_event,
    lorentz_factor,
    lorentz_transform_event,
    minkowski_interval_m2,
    trace_integrity_rate,
    trace_integrity_ratio,
)
from .graph import UPIGraph
from .models import (
    Address,
    Bridge,
    EdgeType,
    EvidenceRecord,
    InformationLayer,
    PhysicsNode,
    Quantity,
    RuntimeMatchResult,
    ScientificStatus,
    TheoryNode,
    VerificationType,
)
from .physics import (
    complex_signal_match,
    energy_from_frequency,
    frequency_from_mass,
    index8_from_frequency,
    index8_from_mass,
    mass_from_frequency,
    normalize_signal,
    relativistic_total_frequency,
    signal_match,
)
from .resilience import (
    CONTROL_CLOCK_HZ,
    TF1766_ANCHOR_ID,
    RecoveryChain,
    RecoveryCheckpoint,
    ResilienceController,
    ResilienceDecision,
    ResilienceMode,
    TemporalMirrorGate,
    TemporalMirrorState,
    VerificationReceipt,
)
from .runtime import (
    RuntimeProfile,
    RuntimeProfileLoader,
    activate_profile,
    deactivate_profile,
    get_active_profiles,
    get_runtime_loader,
    register_profile,
)
from .triage import compare_report, finding_key
from .validation import (
    validate_bridge_consistency,
    validate_bridge_json,
    validate_json_schema,
    validate_node_json,
    validate_node_status,
    validate_record_boundaries,
    validate_scientific_boundaries,
    validate_status_enum,
)
from .workflow import (
    WorkflowState,
    validate_handoff,
    validate_ledger_entry,
    validate_recovery_chain,
    validate_result,
    validate_routine,
    validate_skill,
    validate_task,
    validate_task_result_pair,
    validate_transition,
    validate_workflow,
)

__all__ = [
    # Version
    "__version__",
    # Constants
    "H", "C", "K_B", "E", "N_A",
    "N8_REFERENCE_HZ",
    "EPSILON_Z_DEFAULT",
    "AMPLITUDE_TOLERANCE_DEFAULT",
    "PHASE_TOLERANCE_DEFAULT",
    # Models
    "Address",
    "Quantity",
    "EvidenceRecord",
    "ScientificStatus",
    "EdgeType",
    "PhysicsNode",
    "Bridge",
    "TheoryNode",
    "RuntimeMatchResult",
    "InformationLayer",
    "VerificationType",
    # Physics
    "energy_from_frequency",
    "mass_from_frequency",
    "frequency_from_mass",
    "index8_from_frequency",
    "index8_from_mass",
    "relativistic_total_frequency",
    "normalize_signal",
    "signal_match",
    "complex_signal_match",
    # Dual-observer trace physics
    "Event1D",
    "DualObserverTraceResult",
    "lorentz_factor",
    "lorentz_transform_event",
    "inverse_lorentz_transform_event",
    "minkowski_interval_m2",
    "trace_integrity_ratio",
    "trace_integrity_rate",
    "dual_observer_trace",
    # Runtime
    "RuntimeProfile",
    "RuntimeProfileLoader",
    "get_runtime_loader",
    "register_profile",
    "activate_profile",
    "deactivate_profile",
    "get_active_profiles",
    # Resilience and temporal mirror control
    "TF1766_ANCHOR_ID",
    "CONTROL_CLOCK_HZ",
    "RecoveryCheckpoint",
    "RecoveryChain",
    "VerificationReceipt",
    "TemporalMirrorState",
    "TemporalMirrorGate",
    "ResilienceMode",
    "ResilienceDecision",
    "ResilienceController",
    # Graph
    "UPIGraph",
    "generate_debug_report",
    "render_debug_markdown",
    "compare_report",
    "finding_key",
    # Declarative workflows
    "WorkflowState",
    "validate_task",
    "validate_result",
    "validate_recovery_chain",
    "validate_workflow",
    "validate_transition",
    "validate_task_result_pair",
    "validate_ledger_entry",
    "validate_handoff",
    "validate_skill",
    "validate_routine",
    # Validation
    "validate_json_schema",
    "validate_node_status",
    "validate_bridge_consistency",
    "validate_status_enum",
    "validate_node_json",
    "validate_bridge_json",
    "validate_scientific_boundaries",
    "validate_record_boundaries",
]
