"""Narrow SI dimension checks for declared quantity units."""

from __future__ import annotations

import ast
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
    "rad": "1",
    "rad/s": "T-1",
    "Gyr": "T",
    "Myr": "T",
    "m/s": "L T-1",
    "s^-1": "T-1",
    "Pa": "M L-1 T-2",
}


def equation_dimensions_match(expression: str, units: dict[str, str], output_unit: str) -> bool:
    """Check a bounded arithmetic expression in (mass, length, time) dimensions.

    No evaluation, imports, functions or attribute access. Units are exact port
    contracts; equal dimensions alone do not establish semantic compatibility.
    """
    dimensions = {
        "Hz": (0, 0, -1),
        "s": (0, 0, 1),
        "Gyr": (0, 0, 1),
        "rad": (0, 0, 0),
        "rad/s": (0, 0, -1),
        "kg": (1, 0, 0),
        "m": (0, 1, 0),
        "m/s": (0, 1, -1),
        "J": (1, 2, -2),
        "N": (1, 1, -2),
    }
    if len(expression) > 512:
        return False
    try:
        names = {name: dimensions[unit] for name, unit in units.items()}
        names.update(h=(1, 2, -1), c=(0, 1, -1), pi=(0, 0, 0))
        tree = ast.parse(expression, mode="eval")

        def dimension(node: ast.AST) -> tuple[int, ...]:
            if isinstance(node, ast.Name):
                return names[node.id]
            if isinstance(node, ast.Constant) and type(node.value) in {int, float}:
                return (0, 0, 0)
            if isinstance(node, ast.BinOp):
                left, right = dimension(node.left), dimension(node.right)
                if isinstance(node.op, (ast.Add, ast.Sub)) and left == right:
                    return left
                if isinstance(node.op, ast.Mult):
                    return tuple(a + b for a, b in zip(left, right, strict=True))
                if isinstance(node.op, ast.Div):
                    return tuple(a - b for a, b in zip(left, right, strict=True))
                if (
                    isinstance(node.op, ast.Pow)
                    and isinstance(node.right, ast.Constant)
                    and type(node.right.value) is int
                    and abs(node.right.value) <= 8
                ):
                    return tuple(a * node.right.value for a in left)
            raise ValueError("Unsupported or dimensionally incompatible expression")

        return dimension(tree.body) == dimensions[output_unit]
    except (KeyError, ValueError, SyntaxError, RecursionError):
        return False


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
