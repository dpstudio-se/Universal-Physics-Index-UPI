"""Lossy spectral observability profiles kept separate from exact file identity."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROFILE_ALGORITHM = "byte-dft-histogram-v1"
HISTOGRAM_BUCKETS = 16


@dataclass(frozen=True)
class SpectralProfile:
    algorithm: str
    source_size: int
    sample_count: int
    bins: int
    max_samples: int
    amplitudes: tuple[float, ...]
    phases: tuple[float, ...]
    histogram: tuple[float, ...]
    spectral_entropy: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> SpectralProfile:
        return cls(
            algorithm=str(value["algorithm"]),
            source_size=int(value["source_size"]),
            sample_count=int(value["sample_count"]),
            bins=int(value["bins"]),
            max_samples=int(value["max_samples"]),
            amplitudes=tuple(float(item) for item in value["amplitudes"]),
            phases=tuple(float(item) for item in value["phases"]),
            histogram=tuple(float(item) for item in value["histogram"]),
            spectral_entropy=float(value["spectral_entropy"]),
        )


def _even_sample(data: bytes, max_samples: int) -> bytes:
    if len(data) <= max_samples:
        return data
    if max_samples == 1:
        return data[:1]
    return bytes(
        data[round(index * (len(data) - 1) / (max_samples - 1))]
        for index in range(max_samples)
    )


def _profile(sample: bytes, *, source_size: int, bins: int, max_samples: int) -> SpectralProfile:
    if bins < 1:
        raise ValueError("bins must be positive")
    if max_samples < 1:
        raise ValueError("max_samples must be positive")

    histogram_counts = [0] * HISTOGRAM_BUCKETS
    for byte_value in sample:
        histogram_counts[min(byte_value // 16, HISTOGRAM_BUCKETS - 1)] += 1
    histogram = tuple(
        count / len(sample) if sample else 0.0 for count in histogram_counts
    )

    if not sample:
        return SpectralProfile(
            algorithm=PROFILE_ALGORITHM,
            source_size=source_size,
            sample_count=0,
            bins=bins,
            max_samples=max_samples,
            amplitudes=(0.0,) * bins,
            phases=(0.0,) * bins,
            histogram=histogram,
            spectral_entropy=0.0,
        )

    normalized = [(value - 127.5) / 127.5 for value in sample]
    sample_count = len(normalized)
    amplitudes: list[float] = []
    phases: list[float] = []
    for frequency_bin in range(1, bins + 1):
        real = 0.0
        imaginary = 0.0
        for index, normalized_value in enumerate(normalized):
            angle = -2.0 * math.pi * frequency_bin * index / sample_count
            real += normalized_value * math.cos(angle)
            imaginary += normalized_value * math.sin(angle)
        real /= sample_count
        imaginary /= sample_count
        amplitude = math.hypot(real, imaginary)
        amplitudes.append(amplitude)
        phases.append(math.atan2(imaginary, real) if amplitude > 1e-15 else 0.0)

    power = [amplitude * amplitude for amplitude in amplitudes]
    total_power = sum(power)
    if total_power <= 0 or bins == 1:
        entropy = 0.0
    else:
        probabilities = [value / total_power for value in power if value > 0]
        entropy = -sum(value * math.log(value) for value in probabilities) / math.log(bins)

    return SpectralProfile(
        algorithm=PROFILE_ALGORITHM,
        source_size=source_size,
        sample_count=sample_count,
        bins=bins,
        max_samples=max_samples,
        amplitudes=tuple(amplitudes),
        phases=tuple(phases),
        histogram=histogram,
        spectral_entropy=entropy,
    )


def profile_bytes(data: bytes, *, bins: int = 24, max_samples: int = 4096) -> SpectralProfile:
    """Create a bounded, lossy profile without changing the original bytes."""
    return _profile(
        _even_sample(data, max_samples),
        source_size=len(data),
        bins=bins,
        max_samples=max_samples,
    )


def profile_file(path: Path, *, bins: int = 24, max_samples: int = 4096) -> SpectralProfile:
    """Profile a file with deterministic evenly spaced byte samples."""
    size = path.stat().st_size
    if size <= max_samples:
        sample = path.read_bytes()
    elif max_samples == 1:
        with path.open("rb") as handle:
            sample = handle.read(1)
    else:
        selected = bytearray()
        with path.open("rb") as handle:
            for index in range(max_samples):
                position = round(index * (size - 1) / (max_samples - 1))
                handle.seek(position)
                selected.extend(handle.read(1))
        sample = bytes(selected)
    return _profile(sample, source_size=size, bins=bins, max_samples=max_samples)


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("profile vectors have different lengths")
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 and right_norm == 0:
        return 1.0
    if left_norm == 0 or right_norm == 0:
        return 0.0
    score = sum(a * b for a, b in zip(left, right, strict=True)) / (
        left_norm * right_norm
    )
    return min(1.0, max(0.0, score))


def coherence(
    left: SpectralProfile,
    right: SpectralProfile,
    *,
    amplitude_weight: float = 0.50,
    histogram_weight: float = 0.30,
    phase_weight: float = 0.20,
) -> float:
    """Compare two lossy profiles; never use this score as exact identity."""
    if left.algorithm != right.algorithm or left.bins != right.bins:
        raise ValueError("spectral profiles use incompatible algorithms")
    weights = (amplitude_weight, histogram_weight, phase_weight)
    if any(weight < 0 for weight in weights) or abs(sum(weights) - 1.0) > 1e-12:
        raise ValueError("coherence weights must be nonnegative and sum to 1")

    amplitude_score = _cosine(left.amplitudes, right.amplitudes)
    histogram_score = _cosine(left.histogram, right.histogram)
    phase_weights = [
        min(left.amplitudes[index], right.amplitudes[index])
        for index in range(left.bins)
    ]
    phase_total = sum(phase_weights)
    if phase_total <= 1e-15:
        phase_score = 1.0 if amplitude_score == 1.0 else 0.0
    else:
        phase_score = sum(
            weight * (1.0 + math.cos(left.phases[index] - right.phases[index])) / 2.0
            for index, weight in enumerate(phase_weights)
        ) / phase_total

    score = (
        amplitude_weight * amplitude_score
        + histogram_weight * histogram_score
        + phase_weight * phase_score
    )
    return min(1.0, max(0.0, score))
