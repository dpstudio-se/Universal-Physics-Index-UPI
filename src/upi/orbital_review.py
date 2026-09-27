"""Bounded audit of the signed-a periapsis relation, not an ephemeris validator."""

from __future__ import annotations

import math
from typing import Any

from .feedback import CheckResult


def check_signed_periapsis_equation(
    node: dict[str, Any], *, eccentricity: float, periapsis: float
) -> CheckResult:
    """Compare a recognized formula with energy conservation in dimensionless units.

    q and a must share a length unit. Compare v_p^2 q / mu, so no solar mass,
    AU conversion or observation is invented. Unsupported notation returns UNKNOWN.
    """
    if not all(type(x) in (int, float) and math.isfinite(x) for x in (eccentricity, periapsis)):
        return CheckResult("UNKNOWN", "Non-finite orbital inputs.", "Supply finite e and q.")
    if eccentricity <= 1 or periapsis <= 0:
        return CheckResult(
            "UNKNOWN",
            "Outside the declared hyperbolic domain e > 1, q > 0.",
            "Choose a valid hyperbolic case or a separate boundary model.",
        )
    equations = node.get("equations", [])
    if not isinstance(equations, list) or not all(isinstance(x, str) for x in equations):
        return CheckResult(
            "UNKNOWN", "Equations are unavailable.", "Supply the signed-a equations."
        )
    compact = {"".join(equation.split()) for equation in equations}
    if not {"epsilon=v^2/2-mu/r", "epsilon=-mu/(2a)"} <= compact:
        return CheckResult(
            "UNKNOWN",
            "Energy premises for the signed-a audit are missing.",
            "Declare both specific-energy relations and their convention.",
        )
    plus = "v_p=sqrt(mu(2/q+1/a))" in compact
    minus = "v_p=sqrt(mu(2/q-1/a))" in compact
    if not plus and not minus:
        return CheckResult(
            "UNKNOWN",
            "Periapsis notation is outside this bounded adapter.",
            "Review the formula and extend the adapter with a tested interpretation.",
        )
    # q/a = 1-e. Energy gives v_p^2 q/mu = 2-q/a = 1+e.
    expected = 1 + eccentricity
    if plus:
        proposed = 3 - eccentricity
        return CheckResult(
            "FAIL",
            f"ERR: signed-a plus formula gives v_p^2 q/mu={proposed:g}; "
            f"DER from the declared energy relations gives {expected:g}. "
            "CONTRADICTS energy conservation for e > 1.",
            "Replace +1/a with -1/a wherever the signed-a periapsis formula is asserted, then rerun.",
        )
    return CheckResult(
        "PASS",
        "DER: recognized minus formula preserves the declared energy identity; "
        "scope is this equation only, not the entire node or an observed orbit.",
    )
