let meta = #{
    name: "index-triage",
    description: "Read-only UPI index triage with an independent verifier and a durable report",
    phases: [
        #{ title: "Scan", detail: "read-only debug-index of the declared root" },
        #{ title: "Verify", detail: "independent check of findings and redaction" },
        #{ title: "Report", detail: "ledger decision and durable artifact" },
    ],
};

let scan_schema = #{
    "type": "object",
    "required": ["findings_count", "records_classified", "mutated_sources", "redacted"],
    "properties": #{
        "findings_count": #{ "type": "integer", "minimum": 0 },
        "records_classified": #{ "type": "integer", "minimum": 0 },
        "mutated_sources": #{ "type": "boolean" },
        "redacted": #{ "type": "boolean" },
        "summary": #{ "type": "string" },
    },
};
let verify_schema = #{
    "type": "object",
    "required": ["independent", "accepted", "reason"],
    "properties": #{
        "independent": #{ "type": "boolean" },
        "accepted": #{ "type": "boolean" },
        "reason": #{ "type": "string" },
    },
};

let root = "data";
if args != () && args.root != () {
    root = args.root;
}

phase("Scan");
let scan_prompt = "";
scan_prompt += "You are the index-triage scanner, not the manager. ";
scan_prompt += "Use read-only tools only. Inspect the directory ";
scan_prompt += json_encode(root);
scan_prompt += " and the UPI debug/index validation path. ";
scan_prompt += "Do not mutate source records. ";
scan_prompt += "Prefer running or describing `upi debug-index` with --inspect on that root. ";
scan_prompt += "Return findings_count, records_classified, mutated_sources=false, redacted=true, ";
scan_prompt += "and a short summary. Empty findings are valid only after you inspected files.";
let scan = agent(scan_prompt, #{
    label: "scanner",
    capability_mode: "read-only",
    output_schema: scan_schema,
});

let findings_count = 0;
let records_classified = 0;
let mutated = true;
let redacted = false;
let scan_summary = "scan unavailable";
if scan != () && scan.success && scan.output != () {
    if scan.output.findings_count != () { findings_count = scan.output.findings_count; }
    if scan.output.records_classified != () { records_classified = scan.output.records_classified; }
    if scan.output.mutated_sources != () { mutated = scan.output.mutated_sources; }
    if scan.output.redacted != () { redacted = scan.output.redacted; }
    if scan.output.summary != () { scan_summary = scan.output.summary; }
}

phase("Verify");
let verify_prompt = "";
verify_prompt += "You are an independent verifier, not the scanner and not the manager. ";
verify_prompt += "Adversarially check this scan of ";
verify_prompt += json_encode(root);
verify_prompt += ": findings_count=";
verify_prompt += findings_count.to_string();
verify_prompt += ", records_classified=";
verify_prompt += records_classified.to_string();
verify_prompt += ", mutated_sources=";
verify_prompt += json_encode(mutated);
verify_prompt += ", redacted=";
verify_prompt += json_encode(redacted);
verify_prompt += ", summary=";
verify_prompt += json_encode(scan_summary);
verify_prompt += ". Read the same tree yourself. Set accepted=true only if sources were not mutated ";
verify_prompt += "and values look redacted. independent must be true. Fail closed on missing evidence.";
let verify = agent(verify_prompt, #{
    label: "verifier",
    capability_mode: "read-only",
    output_schema: verify_schema,
});

let accepted = false;
let verify_reason = "verifier unavailable";
if verify != () && verify.success && verify.output != () {
    if verify.output.accepted == true && verify.output.independent == true {
        accepted = true;
    }
    if verify.output.reason != () { verify_reason = verify.output.reason; }
}

phase("Report");
let decision = "escalate";
if accepted && mutated == false && redacted == true {
    if findings_count == 0 {
        decision = "advance";
    } else {
        decision = "retry";
    }
}

let report = "";
report += "# Index triage report\n\n";
report += "- Root: " + root + "\n";
report += "- Records classified: " + records_classified.to_string() + "\n";
report += "- Findings: " + findings_count.to_string() + "\n";
report += "- Redacted: " + json_encode(redacted) + "\n";
report += "- Sources mutated: " + json_encode(mutated) + "\n";
report += "- Verifier accepted: " + json_encode(accepted) + "\n";
report += "- Decision: " + decision + "\n";
report += "- Verification type: software_test\n\n";
report += "Scan: " + scan_summary + "\n\n";
report += "Verifier: " + verify_reason + "\n";
let artifact = write_scratch_file("index-triage-report.md", report);

complete(#{
    path: artifact,
    decision: decision,
    findings_count: findings_count,
    verification_type: "software_test",
    approval_required: decision != "advance",
});
