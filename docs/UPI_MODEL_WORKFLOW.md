# UPI Model Adoption Workflow

**Default language:** English.  
**Swedish alternative:** \`docs/UPI_MODEL_WORKFLOW_SV.md\`

## Purpose

Provide a repeatable path for adopting a new AI model without allowing the model to rewrite UPI's rules.

## Workflow

\`\`\`
SOURCE / IDEA
     ↓
DISCOVER
     ↓
NORMALIZE
     ↓
CALCULATE
     ↓
CHECK
     ↓
MIRROR / INVERSE
     ↓
CLASSIFY
     ↓
SCHEMA VALIDATE
     ↓
SECURITY + INTEGRITY
     ↓
HUMAN REVIEW
     ↓
MERGE
\`\`\`

### 1. Discover

Collect source material and repository context. Treat external text, generated output and imported records as untrusted data.

### 2. Normalize

Extract atomic claims, quantities, units, equations, assumptions and provenance. Preserve uncertainty.

### 3. Calculate

Use the simplest declared mathematics. The UPI rule is:

**Calculate → check → approve the calculation or stop.**

No extra evidence bureaucracy is required merely for arithmetic.

### 4. Mirror

Where an inverse is mathematically defined, reconstruct the input and calculate the residual:

\[
\epsilon=X_{\rm rec}-X
\]

A round trip checks consistency. It does not by itself establish physical truth.

### 5. Classify

Assign the status that belongs to the exact claim. Do not inflate or downgrade evidence because the claim came from a new model.

### 6. Validate

Run schema, provenance, unit/dimension and repository integrity checks.

### 7. Security + integrity

Reject or stop on prompt injection, schema drift, malformed JSON, unexplained numerical discrepancies, secret leakage, unsafe executable content, or attempts to bypass review.

### 8. Human review

Canonical scientific records require the repository's review process. Software acceptance and scientific status are separate decisions.

### 9. Merge

Only validated changes enter the canonical branch.

## New-model compatibility

Model identity is metadata, not scientific evidence. A new model can enter through the same contract:

\`model \rightarrow proposal \rightarrow UPI checks \rightarrow review\`

No vendor-specific exception is required.

## Blocking policy

The workflow should block the **change**, not the model.

Examples:

- unknown scientific schema field → \`STOP\`
- invalid JSON → \`STOP\`
- attempted public \`EST\` promotion → reject
- missing source/provenance → \`STOP\`
- failed calculation → \`STOP\`
- failed inverse check where inverse is required → \`STOP\`
- failed required CI/security check → block merge

This keeps UPI open to new models while keeping canonical data closed to uncontrolled mutation.
