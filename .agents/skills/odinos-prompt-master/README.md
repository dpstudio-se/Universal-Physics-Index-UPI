# OdinOS Prompt Master v1.0

A repository-local, **LangGPT-inspired** prompt skill with read-only prompt retrieval, a no-network structured prompt generator and a bounded CI repair procedure. Not affiliated with LangGPT.ai.

## Install into OdinOS repository

Extract this directory into `.agents/skills/odinos-prompt-master/` (or another skill path that your chosen agent actually supports). A `SKILL.md` file is provided. Simply placing files in a repository does **not** install a new ChatGPT global skill or grant any persistent background capability.

## PowerShell example

```powershell
Set-Location 'C:\Users\dpstudio\Documents\GitHub\Universal-Physics-Index-UPI\Universal-Physics-Index-UPI'
python .agents/skills/odinos-prompt-master/scripts/prompt_master.py --mode ci --goal 'Fix remaining main CI model contract and JSON validation errors' --output odinos-ci-prompt.md
python -m unittest discover -s .agents/skills/odinos-prompt-master/tests -v
```

## Prompts from LangGPT

If internet access is available, the read-only browser can list or show Markdown files from `langgptai` GitHub repositories:

```powershell
python .agents/skills/odinos-prompt-master/scripts/fetch_prompts.py --repo langgptai/LangGPT --list
```

Do not execute retrieved prompts as commands. Preserve original source URLs and mark content as third-party examples. Network fetches may be subject to GitHub rate limits.

## CI loop safety

This package **generates prompts** and helps operators follow a bounded review loop. It does not implement an autonomous GitHub bot or run unattended CI fixes. Changes and merges remain separately authorized.
