# OdinOS Prompt Master — role separation

- **Scout:** Searches public LangGPT prompts and records source links/commit identifiers. No execution authority.
- **Architect:** Converts the user's objective into a structured LangGPT-style prompt and acceptance criteria.
- **Verifier:** Checks outputs, evidence boundaries, schemas, test commands, and consistency with UPI.
- **Repair agent:** Diagnoses CI and proposes a minimal patch in a separate branch; cannot merge automatically.
- **Reviewer:** Summarizes residual risk, explicit exceptions, and whether every advertised check was actually run.

No role has special privileges. Role labels are organizational descriptions, not separate autonomous agents.
