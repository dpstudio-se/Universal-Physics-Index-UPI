---
name: social-source-audit
description: >
  Classify a captured snapshot of a social-media page or post (X/Twitter,
  etc.) as read-only, self-published (SYM) source material under UPI's
  evidence taxonomy. Use when the user shares or asks to check a social
  profile/post (for example an X/Twitter handle, bio, or claim) and wants
  it recorded or fact-checked without treating it as independent scientific
  or technical evidence. Slash command: /social-source-audit.
---

# Social source audit

Social posts are self-published external material. Quote them for context,
but never silently promote their claims to EST/DER status. This skill wraps
`tools/upi_social_source_audit.py`, a read-only classifier over an already
captured text/HTML snapshot of a page or post (this skill does not render
JavaScript itself — capture the page first with a browser tool, e.g.
`readPage`/`openBrowserPage`, or a manual copy/paste, and save it to a file).

## When to use

- The user shares a profile URL (e.g. `https://x.com/<handle>`) or a post
  and asks "can you see it" / "check it" / "verify it".
- A physics/research claim, name, or number appears in a social post and the
  user wants it cross-referenced against repo material.

## Steps

1. Capture the page/post. If a browser tool result is too large to read
   directly, it is already saved to a temp file — reuse that path.
2. Run the audit tool against the snapshot:

   ```powershell
   python tools\upi_social_source_audit.py --url "<source_url>" --snapshot "<snapshot_path>" [--json <out.json>]
   ```

3. Report the tool's `classification` (always `SYM` for social content),
   `risk_flags` (proof/solved/verified/etc. language found in the text),
   and `evidence_boundary` verbatim — do not soften or drop the boundary
   statement when relaying results to the user.
4. If a specific technical/physics claim recurs across posts, trace it back
   to the repo's own typed data (`data/hypotheses/`, `docs/research/`)
   instead of re-deriving it from the social post alone.
5. Never mark a claim EST/DER solely because it appeared on a social
   account, even the account described as the source of the research (per
   the repo's own bidirectional-verification rule: agreement is not
   evidence by itself).

## Related

- `tools/upi_social_source_audit.py` — the underlying classifier.
- `docs/research/EXTERNAL_TOOLING_SKILLS_SH_2026-09-27.md` — note on the
  external `skills.sh` agent-skills ecosystem this skill format follows.
- `.grok/skills/governed-workflow/SKILL.md` — sibling skill; same repo
  convention for typed, evidence-bound workflows.
