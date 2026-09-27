# Schema migration policy (v1.0.0)

Breaking schema changes require a new major version. Additive optional
fields are allowed in a minor version.

v1.0.0 additions versus 0.1.0-alpha:

- node: `replaces`, `superseded_by`, `source_status`
- theory: `evidence`, `primary_sources`
- contribution-batch, ledger, handoff, skill, routine schemas

Readers must ignore unknown fields they do not implement. Writers targeting
v1 must not require new fields on old records.

`verification_type: software_test` is unchanged: tests do not become
experiments by a version bump.
