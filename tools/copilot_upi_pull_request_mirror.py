#!/usr/bin/env python3
"""Read-only Copilot helper for UPI pull-request Mirror Loop audits.

TF1766 is implemented as a transparency/audit operator: it exposes and
classifies filter decisions but never bypasses higher-priority policy,
security, permissions, or scientific-status gates.
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ALLOWED_STATUS={"EST","DER","HYP","STOP","ERR","SYM"}
RISK_TERMS=("promote","promotion","physical proof","causal","resonance","universal",
"solved","independent","verification","evidence","frequency","mass","hodge","riemann",
"yang-mills","navier-stokes","p vs np","birch")

@dataclass
class Gate:
    name:str; state:str; detail:str

@dataclass
class MirrorReport:
    repository:str; pr:int; title:str; url:str; head:str; base:str; draft:bool
    gates:list[Gate]; changed_files:list[str]; risk_flags:list[str]
    status_mentions:list[str]; evidence_boundary:str; next_actions:list[str]
    tf1766_audit:dict[str,Any]

def gh_json(args:list[str])->Any:
    try: p=subprocess.run(["gh",*args],check=False,capture_output=True,text=True)
    except FileNotFoundError as exc: raise RuntimeError("GitHub CLI 'gh' was not found on PATH.") from exc
    if p.returncode: raise RuntimeError(p.stderr.strip() or "GitHub CLI command failed")
    try: return json.loads(p.stdout)
    except json.JSONDecodeError as exc: raise RuntimeError(f"GitHub CLI returned non-JSON output: {p.stdout[:400]}") from exc

def pr_payload(repo:str,pr:int)->dict[str,Any]:
    fields=["number","title","url","isDraft","headRefName","baseRefName","body","files","commits","reviews","statusCheckRollup"]
    return gh_json(["pr","view",str(pr),"--repo",repo,"--json",",".join(fields)])

def open_prs(repo:str)->list[dict[str,Any]]:
    return gh_json(["pr","list","--repo",repo,"--state","open","--limit","100",
                    "--json","number,title,url,headRefName,baseRefName,isDraft"])

def file_names(payload:dict[str,Any])->list[str]:
    return [str(x.get("path","")) for x in payload.get("files",[]) if x.get("path")]

def text_for_scan(payload:dict[str,Any])->str:
    chunks=[str(payload.get("title","")),str(payload.get("body",""))]
    chunks += [str(x.get("body","")) for x in payload.get("reviews",[]) or []]
    chunks += [str(x.get("message","")) for x in payload.get("commits",[]) or []]
    return "\n".join(chunks).lower()

def status_mentions(payload:dict[str,Any])->list[str]:
    t=text_for_scan(payload).upper()
    return sorted({s for s in ALLOWED_STATUS if re.search(rf"\b{re.escape(s)}\b",t)})

def tf1766_classify(payload:dict[str,Any],files:list[str],flags:list[str])->dict[str,Any]:
    t=text_for_scan(payload)
    policy_terms=("github policy","copilot policy","security policy","permission","protected branch","authentication")
    if any(x in t for x in policy_terms):
        cls="POLICY_OR_SECURITY"; action="STOP"
    elif "unknown" in t or not payload.get("number"):
        cls="UNKNOWN"; action="STOP"
    elif "filter" in t and ("false positive" in t or "false-positive" in t):
        cls="UPI_FILTER_CANDIDATE"; action="REVIEW"
    else:
        cls="NO_FILTER_EVENT"; action="CONTINUE"
    return {"transparent":True,"reason_exposed":True,"classification_verified":False,
            "classification":cls,"override":False,"next_action":action,
            "rule_id":"TF1766-AUDIT-V1"}

def build_report(repo:str,payload:dict[str,Any])->MirrorReport:
    files=file_names(payload); scan=text_for_scan(payload); flags=[]
    if any(x in scan for x in RISK_TERMS): flags.append("research-claim-language-present")
    if any(p.startswith("data/") for p in files): flags.append("canonical-data-change")
    if any(p.startswith("schemas/") for p in files): flags.append("schema-change")
    if any(p.startswith(".github/workflows/") for p in files): flags.append("ci-workflow-change")
    if any(p.startswith("prompts/") for p in files): flags.append("agent-prompt-change")
    gates=[
      Gate("PR-readable","PASS","PR metadata and changed files were read from GitHub."),
      Gate("TF1766-audit","CHECK","Expose and classify filter decisions; no bypass or override."),
      Gate("scientific-status-separation","CHECK","Scientific status remains separate from CI/workflow state."),
      Gate("provenance","CHECK","Bind claims to exact sources, inputs and commit hashes."),
      Gate("mirror-forward","CHECK","Verify the proposed forward calculation/model path."),
      Gate("mirror-inverse","CHECK","Verify inverse/recovery and numerical error."),
      Gate("dimensions","CHECK","Check units and semantic quantity types."),
      Gate("null-or-alternative","CHECK","Require null model or competing explanation where applicable."),
      Gate("independent-evidence","CHECK","PR-local tests are not independent scientific replication."),
      Gate("promotion","BLOCKED","This helper never approves, merges, or promotes scientific status.")
    ]
    return MirrorReport(repo,int(payload["number"]),str(payload.get("title","")),str(payload.get("url","")),
      str(payload.get("headRefName","")),str(payload.get("baseRefName","")),bool(payload.get("isDraft",False)),
      gates,files,sorted(flags),status_mentions(payload),
      "Software/CI results establish tested behavior only; they do not alone establish physical causality or scientific proof.",
      ["Inspect diff and provenance.","Run forward/inverse and dimensional checks.","Require independent evidence or a declared null model.","Keep unresolved claims OPEN/STOP/HYP."],
      tf1766_classify(payload,files,flags))

def print_report(r:MirrorReport)->None:
    print(f"UPI Mirror Loop Audit: PR #{r.pr} — {r.title}\n{r.url}\n{r.head} -> {r.base} | draft={r.draft}")
    print("\nTF1766 AUDIT\n"+json.dumps(r.tf1766_audit,indent=2,ensure_ascii=False))
    print("\nGATES")
    for g in r.gates: print(f"[{g.state:7}] {g.name}: {g.detail}")
    print("\nCHANGED FILES"); [print(f"- {p}") for p in r.changed_files]
    print("\nRISK FLAGS"); [print(f"- {x}") for x in (r.risk_flags or ["none"])]
    print(f"\nSTATUS MENTIONS: {', '.join(r.status_mentions) or 'none'}")
    print(f"\nEVIDENCE BOUNDARY: {r.evidence_boundary}")
    print("\nNEXT ACTIONS"); [print(f"- {x}") for x in r.next_actions]

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--repo",required=True)
    g=ap.add_mutually_exclusive_group(required=True); g.add_argument("--pr",type=int); g.add_argument("--all-open",action="store_true")
    ap.add_argument("--json",dest="json_path"); a=ap.parse_args()
    try: payloads=[pr_payload(a.repo,a.pr)] if a.pr else [pr_payload(a.repo,x["number"]) for x in open_prs(a.repo)]
    except RuntimeError as exc: print(f"ERROR: {exc}",file=sys.stderr); return 2
    reports=[build_report(a.repo,x) for x in payloads]
    if a.json_path: Path(a.json_path).write_text(json.dumps([asdict(x) for x in reports],indent=2,ensure_ascii=False),encoding="utf-8")
    else:
      for i,r in enumerate(reports):
        if i: print("\n"+"="*72+"\n")
        print_report(r)
    return 0

if __name__=="__main__": raise SystemExit(main())
