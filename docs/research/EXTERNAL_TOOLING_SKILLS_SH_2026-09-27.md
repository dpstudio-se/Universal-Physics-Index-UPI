# External tooling note: skills.sh (Agent Skills ecosystem)

**Status:** SYM (external, self-published tooling reference) / DER (the
repo skill built here follows its documented pattern).

**Date:** 2026-09-27

## What this is

[`skills.sh`](https://www.skills.sh/) is a third-party, Vercel-hosted
directory site ("The Agent Skills Directory") for reusable "skills" that
extend AI coding agents (Claude Code, Cline, Amp, opencode, and similar
tools are listed as supported agent icons on the site). It advertises a
one-line install flow:

```bash
npx skills add <owner/repo>
```

The site exposes browsing sections for **Packs**, **Topics**, **Official**,
and **Audits**.

## Why it is noted here (evidence boundary)

This is an **external product page**, not a scientific or mathematical
source. Nothing on `skills.sh` bears on the Ω1766/Ψ27D physics research
program in this repository. It is recorded here only because the user
asked for a UPI-native skill to be modeled on that ecosystem's
conventions (a small, declarative `SKILL.md` capability description with a
narrow, auditable scope).

- `EST`: the page's stated name, tagline, and install command, as fetched
  on 2026-09-27.
- `SYM`: any implied endorsement, ranking, or quality signal from being
  listed on that site — this repo does not publish to or depend on
  `skills.sh`, and no claim on that site has been independently verified.
- `STOP`: whether any specific listed skill/pack is safe, correct, or
  suitable for use in this repository has not been evaluated and is out of
  scope unless a specific package is named and reviewed.

## What was actually built in this repo

Rather than depending on the external `npx skills add` installer (which
would pull unreviewed third-party code into this repository — a
supply-chain risk this repo explicitly avoids per its own tooling
policy), a same-shaped, repo-native skill was authored locally:

- [`.grok/skills/social-source-audit/SKILL.md`](/C:/Users/dpstudio/Documents/GitHub/Universal-Physics-Index-UPI-main/.grok/skills/social-source-audit/SKILL.md)
  — declarative capability description, same frontmatter shape as the
  existing [`.grok/skills/governed-workflow/SKILL.md`](/C:/Users/dpstudio/Documents/GitHub/Universal-Physics-Index-UPI-main/.grok/skills/governed-workflow/SKILL.md).
- [`tools/upi_social_source_audit.py`](/C:/Users/dpstudio/Documents/GitHub/Universal-Physics-Index-UPI-main/tools/upi_social_source_audit.py)
  — the read-only implementation, classifying a captured social-media
  snapshot as `SYM` evidence and surfacing risk-language flags
  (proof/solved/verified/etc.).

## Next observation needed to change this status

None required to keep this note accurate; it already reflects only what
was fetched from the public page. If the user wants an actual third-party
skill installed from `skills.sh`, that specific package must be named and
reviewed (license, code contents, network calls) before installation, per
this repo's general supply-chain policy for external code.
