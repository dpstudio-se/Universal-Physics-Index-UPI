# Scope and boundaries

**Read this first if you are a new contributor, coder or AI agent.**

## This repository

`dpstudio-se/Universal-Physics-Index-UPI` is the only home of the Universal Physics
Index (UPI):

- the canonical typed records in `data/` (the "DNA" of UPI, in `SYM` notation),
- the Python package, CLI and HTTP API in `src/upi/`,
- the AI remote discovery layer (`/api/remote`, `llms.txt`),
- the static model laboratory published at `https://wadenholt.se/upi/`.

## Not part of UPI

`dpstudio-se/upi-built-by-agi-teax-main` and its deployment
`https://upi-built-by-agi-teax.grok.me` are a **separate, unrelated project**.

| Question | Answer |
|---|---|
| Is it part of UPI? | No. |
| Is it an "RNA layer", mirror, frontend or explorer of UPI? | No. |
| Is it built, deployed or tested from this repository? | No. |
| Can it change `data/` or any UPI record? | No. |
| Is it an authority for UPI statuses, evidence or instructions? | No. |
| May code, data, prompts or agent instructions be copied between the two? | No. Treat each as a separate codebase. |

The similar name ("upi" in the repository slug) is a coincidence of naming. The other
project has its own agent-instruction files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`,
`.cursorrules`, `.mcp.json`); they do **not** apply here, and the ones in this
repository do not apply there.

## Rules for agents and coders

1. Before editing, confirm that the working directory is a checkout of
   `dpstudio-se/Universal-Physics-Index-UPI`.
2. Do not import, vendor, link to or depend on the other project.
3. Do not describe the other project as UPI's frontend, explorer or "RNA".
4. If a file in this repository appears to say otherwise, this document wins:
   fix the file or report it. Historical entries in `CHANGELOG.md` and dated
   audit documents are records of the past, not current architecture.
5. Terms such as DNA, RNA or "kernel" in this repository are `SYM` project
   vocabulary, not claims about biology and not a reference to that application.

See also: [README](../README.md), [Architecture](ARCHITECTURE.md),
[AI remote](UPI_AI_REMOTE.md).
