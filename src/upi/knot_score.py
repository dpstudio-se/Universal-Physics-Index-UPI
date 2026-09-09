"""Transparent engineering ranking, never a probability of new physics."""

from .knot_model import Observation, bounded


def score_components(a: Observation, b: Observation, strength: float,
                     cross_domain_support: float, persistence: float) -> dict[str, float]:
    for name, value in (("strength", strength), ("cross_domain_support", cross_domain_support),
                        ("persistence", persistence)):
        bounded(value, name)
    independent = bool(a.source_group and b.source_group and
                       a.source_group != b.source_group and a.source != b.source and
                       not set(a.provenance) & set(b.provenance))
    components = {
        "independence": float(independent),
        "contradiction_strength": strength,
        "source_quality": min(a.source_quality, b.source_quality)
        if a.provenance and b.provenance else 0.0,
        "cross_domain_support": cross_domain_support,
        "persistence": persistence,
    }
    score = 1.0
    for value in components.values():
        score *= value
    return {**components, "score": score}
