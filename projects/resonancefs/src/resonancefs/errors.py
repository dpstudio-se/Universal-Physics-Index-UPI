"""Project-specific exceptions."""


class ResonanceFSError(Exception):
    """Base error for expected repository failures."""


class IntegrityError(ResonanceFSError):
    """Stored bytes, hashes, manifests or links do not agree."""


class PolicyError(ResonanceFSError):
    """A Phi1766 policy is malformed or incompatible."""
