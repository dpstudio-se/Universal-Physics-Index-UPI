# ResonanceFS

ResonanceFS is a standalone prototype that turns the useful part of the
"filesystem as resonance architecture" idea into an auditable storage tool.
It combines exact, content-addressed snapshots with a separate lossy spectral
profile for anomaly detection.

The separation is intentional:

- SHA-256 chunk hashes, file hashes, and ordered Merkle roots establish exact
  byte identity.
- Spectral profiles describe similarity and change. They never replace exact
  hashes, permissions, encryption, or malware analysis.
- `Phi1766` is a versioned policy document containing thresholds and weights;
  it is not treated as a physical constant.

## Architecture

```text
source directory
      |
      +-- bytes --> fixed chunks --> SHA-256 object store
      |                                |
      |                                +--> ordered Merkle root
      |
      +-- sampled bytes --> DFT amplitudes/phases + byte histogram
                                             |
                                             +--> coherence score

exact objects + spectral metadata + embedded policy --> immutable snapshot
                                                        |
                                                        +--> inspect/restore
```

Every snapshot stores the policy that produced its classifications. A later
policy change therefore cannot silently reinterpret an older decision.

## Quick start

Python 3.10 or newer is required.

```powershell
cd projects/resonancefs
python -m pip install -e .

resonancefs init demo-store --policy phi1766.example.json
resonancefs commit demo-store path\to\source --message "first snapshot"
resonancefs list demo-store
resonancefs inspect demo-store HEAD
resonancefs restore demo-store HEAD demo-restore
```

Commands emit JSON so another agent or program can consume the evidence
without parsing prose. `inspect` verifies the manifest hash, all chunk hashes,
the reconstructed file hash and the stored spectral profile before reporting a
clean snapshot.

By default, restore refuses to overwrite existing files and skips files whose
comparison classification is `QUARANTINE`. Use `--overwrite` or
`--include-quarantined` only after reviewing the snapshot.

Run the verification suite with:

```powershell
python -m pip install pytest ruff mypy
pytest tests -q
ruff check src tests
mypy src
```

## Phi1766 policy

[`phi1766.example.json`](phi1766.example.json) defines:

- chunk size and spectral sample size;
- number of DFT bins;
- amplitude, histogram, and phase weights;
- `INSPECT` and `QUARANTINE` coherence thresholds.

Coherence is a bounded score in `[0, 1]`. It compares profiles of the same
relative path in adjacent snapshots. This is a triage signal, not a statement
about the meaning or safety of the file.

## Security and integrity boundary

The prototype currently provides:

- immutable content-addressed objects;
- deterministic snapshot manifests and IDs;
- ordered Merkle roots, so chunk order matters;
- verification on every object read;
- atomic writes for objects, snapshots, `HEAD`, and restored files;
- rejection of symbolic links during ingestion;
- safe relative-path validation during restore;
- conservative quarantine behavior.

It does **not** yet provide authentication, authorization, encryption, remote
replication, filesystem mounting, garbage collection, or semantic malware
detection. The current DFT operates on sampled raw bytes, so usefulness and
thresholds must be calibrated against a representative corpus before any
security decision relies on it. Large files are reconstructed in memory during
commit in this prototype.

The 11-dimensional brane description remains a symbolic design metaphor. The
implemented software contract requires no claim of physical equivalence.

## Status ledger

- `EST` (`verification_type: software_test`): exact reconstruction, corruption
  detection, manifest-tamper detection, Merkle ordering, policy validation,
  quarantine defaults, and the CLI flow have automated tests.
- `DER`: given collision-resistant SHA-256 and successful verification, a
  restored file is byte-identical to the committed file.
- `HYP`: spectral coherence will expose useful anomalies in real mixed-file
  workloads with acceptably low false-positive and false-negative rates.
- `STOP`: production security use stops at the absence of a labelled corpus and
  calibrated operating thresholds. The smallest next observation is a
  benchmark containing known benign changes and known unwanted mutations.
- `SYM`: branes, potential wells, and resonance addressing are architectural
  metaphors here, not executable evidence.

## Source layout

```text
src/resonancefs/
  cli.py          JSON command-line interface
  hashing.py      canonical JSON, SHA-256, ordered Merkle tree
  policy.py       versioned Phi1766 policy and classification
  repository.py   snapshots, inspection, comparison, restore
  spectral.py     deterministic byte-spectral profiles and coherence
  storage.py      content-addressed chunks and exact reconstruction
tests/
  test_resonancefs.py
```

