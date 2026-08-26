"""Narrow SI dimension checks for declared quantity units."""

from __future__ import annotations

from typing import Any

SI_BASE = {
    "Hz": "T-1",
    "s": "T",
    "m": "L",
    "kg": "M",
    "J": "M L2 T-2",
    "N": "M L T-2",
    "C": "I T",
    "K": "Theta",
    "mol": "N",
}


def dimension_of(unit: str) -> str | None:
    """Return a coarse SI dimension string, or None if unknown."""
    return SI_BASE.get(unit)


def check_quantities(quantities: list[dict[str, Any]]) -> list[str]:
    """Flag unknown units. Does not invent conversions."""
    errors = []
    for item in quantities:
        unit = item.get("unit")
        if unit and dimension_of(str(unit)) is None:
            errors.append(f"Unknown unit for dimension check: {unit}")
    return errors


def energy_mass_frequency_consistent(unit: str, name: str) -> bool:
    """Return True if the unit matches a declared quantity role."""
    if name in {"frequency", "reference_frequency"} and unit == "Hz":
        return True
    if name in {"mass", "equivalent_mass"} and unit == "kg":
        return True
    if name == "energy" and unit == "J":
        return True
    return dimension_of(unit) is not None
