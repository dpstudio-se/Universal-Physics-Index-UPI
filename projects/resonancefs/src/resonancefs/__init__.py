"""ResonanceFS: exact content storage plus a non-authoritative spectral index."""

from .errors import IntegrityError, PolicyError, ResonanceFSError
from .policy import Phi1766Policy
from .repository import ResonanceRepository, SnapshotResult
from .spectral import SpectralProfile, coherence, profile_bytes, profile_file

__all__ = [
    "IntegrityError",
    "Phi1766Policy",
    "PolicyError",
    "ResonanceFSError",
    "ResonanceRepository",
    "SnapshotResult",
    "SpectralProfile",
    "coherence",
    "profile_bytes",
    "profile_file",
]

__version__ = "0.1.0"
