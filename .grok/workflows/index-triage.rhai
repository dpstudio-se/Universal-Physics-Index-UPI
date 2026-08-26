let meta = #{
    name: "index-triage",
    description: "Read-only UPI index triage: scanner and schema-validator in parallel, then an independent verifier and a durable report",
    when_to_use: "Run after data/ or schema changes, or when the user asks for index triage, debug-index, or the weekly heartbeat",
    phases: [
        #{ title: "Specialists", detail: "scanner and schema-validator on separate artifacts" },
        #{ title: "Verify", detail: "independent check of both specialist outputs" },
        #{ title: "Report", detail: "ledger decision and durable artifact" },
    ],
};

let scan_schema = #{
    "type": "object",
    "required": ["findings_count", "unexpected_count", "heartbeat", "mutated_sources", "redacted"],
    "properties": #{
        "findings_count": #{ "type": "integer", "minimum": 0 },
        "unexpected_count": #{ "type": "integer", "minimum": 0 },
        "heartbeat": #{ "type": "boolean" },
        "mutated_sources": #{ "type": "boolean" },
        "redacted": #{ "type": "boolean" },
        "decision": #{ "type": "string" },
        "summary": #{ "type": "string" },
    },
};
let schema_schema = #{
    "type": "object",
    "required": ["passed", "summary"],
    "properties": #{
        "passed": #{ "type": "boolean" },
        "tests_run": #{ "type": "integer", "minimum": 0 },
        "summary": #{ "type": "string" },
    },
};
let verify_schema = #{
    "type": "object",
    "required": ["independent", "accepted", "reason", "evidence"],
    "properties": #{
        "independent": #{ "type": "boolean" },
        "accepted": #{ "type": "boolean" },
        "reason": #{ "type": "string" },
        "evidence": #{ "type": "string" },
    },
};

let root = "data";
let known = "examples/ledger/baselines/known-findings.json";
if args != () {
    if args.root != () { root = args.root; }
    if args.known != () { known = args.known; }
}

phase("Specialists");
let scan_prompt = "";
scan_prompt += "You are the index-triage scanner specialist, not the manager and not the verifier. ";
scan_prompt += "Use tools. Run this command with the project venv if needed: ";
scan_prompt += "upi triage ";
scan_prompt += json_encode(root);
scan_prompt += " --inspect --known ";
scan_prompt += json_encode(known);
scan_prompt += ". Do not mutate data/, schemas/, or examples/. ";
scan_prompt += "Read the command output and known-findings.json. ";
scan_prompt += "Return findings_count, unexpected_count, heartbeat, mutated_sources=false if git status of data/ is unchanged by you, ";
scan_prompt += "redacted=true only if the report redacts source values, plus decision and a short summary. ";
scan_prompt += "Empty unexpected_count is valid only after you ran the command.";

let schema_prompt = "";
schema_prompt += "You are the schema-validator specialist, not the scanner and not the manager. ";
schema_prompt += "Use tools. Run: pytest tests/test_governed_system.py tests/test_schema.py tests/test_workflow.py -q ";
schema_prompt += "Do not mutate source records. Do not run debug-index. ";
schema_prompt += "Return passed=true only if those tests passed, tests_run if known, and a short summary.";

let specialist_results = parallel([
    #{
        prompt: scan_prompt,
        label: "scanner",
        capability_mode: "execute",
        output_schema: scan_schema,
    },
    #{
        prompt: schema_prompt,
        label: "schema-validator",
        capability_mode: "execute",
        output_schema: schema_schema,
    },
]);

let scan = specialist_results[0];
let schema_job = specialist_results[1];

let findings_count = 0;
let unexpected_count = 0;
let heartbeat = false;
let mutated = true;
let redacted = false;
let scan_decision = "unavailable";
let scan_summary = "scan unavailable";
if scan != () && scan.success && scan.output != () {
    if scan.output.findings_count != () { findings_count = scan.output.findings_count; }
    if scan.output.unexpected_count != () { unexpected_count = scan.output.unexpected_count; }
    if scan.output.heartbeat == true { heartbeat = true; }
    if scan.output.mutated_sources != () { mutated = scan.output.mutated_sources; }
    if scan.output.redacted != () { redacted = scan.output.redacted; }
    if scan.output.decision != () { scan_decision = scan.output.decision; }
    if scan.output.summary != () { scan_summary = scan.output.summary; }
}

let schema_passed = false;
let schema_summary = "schema validation unavailable";
if schema_job != () && schema_job.success && schema_job.output != () {
    if schema_job.output.passed == true { schema_passed = true; }
    if schema_job.output.summary != () { schema_summary = schema_job.output.summary; }
}

phase("Verify");
let verify_prompt = "";
verify_prompt += "You are an independent verifier, not the scanner, not the schema-validator, and not the manager. ";
verify_prompt += "Use read-only tools. You MUST run `git status -- ";
verify_prompt += json_encode(root);
verify_prompt += "` and you MUST read tests/test_governed_system.py, tests/test_schema.py, and tests/test_workflow.py. ";
verify_prompt += "Independently inspect ";
verify_prompt += json_encode(root);
verify_prompt += " and ";
verify_prompt += json_encode(known);
verify_prompt += ". Scanner claimed findings_count=";
verify_prompt += findings_count.to_string();
verify_prompt += ", unexpected_count=";
verify_prompt += unexpected_count.to_string();
verify_prompt += ", heartbeat=";
verify_prompt += json_encode(heartbeat);
verify_prompt += ", mutated_sources=";
verify_prompt += json_encode(mutated);
verify_prompt += ", redacted=";
verify_prompt += json_encode(redacted);
verify_prompt += ", decision=";
verify_prompt += json_encode(scan_decision);
verify_prompt += ", summary=";
verify_prompt += json_encode(scan_summary);
verify_prompt += ". Schema-validator claimed passed=";
verify_prompt += json_encode(schema_passed);
verify_prompt += ", summary=";
verify_prompt += json_encode(schema_summary);
verify_prompt += ". Set independent=true. Set accepted=true only with evidence you inspected yourself ";
verify_prompt += "that sources were not mutated, values look redacted, and schema tests actually passed. ";
verify_prompt += "Fail closed: missing evidence means accepted=false. Fill evidence with files or commands you read.";

let verify = agent(verify_prompt, #{
    label: "verifier",
    capability_mode: "read-only",
    output_schema: verify_schema,
});

let accepted = false;
let verify_reason = "verifier unavailable";
let verify_evidence = "";
if verify != () && verify.success && verify.output != () {
    if verify.output.reason != () { verify_reason = verify.output.reason; }
    if verify.output.evidence != () { verify_evidence = verify.output.evidence; }
    if verify.output.accepted == true && verify.output.independent == true && verify_evidence != "" {
        accepted = true;
    }
}

phase("Report");
let decision = "escalate";
if accepted && schema_passed && mutated == false && redacted == true && unexpected_count == 0 {
    decision = "advance";
}

log("index-triage decision=" + decision + " unexpected=" + unexpected_count.to_string());

let report = "";
report += "# Index triage report\n\n";
report += "- Root: `" + root + "`\n";
report += "- Known catalog: `" + known + "`\n";
report += "- Findings: " + findings_count.to_string() + "\n";
report += "- Unexpected: " + unexpected_count.to_string() + "\n";
report += "- Heartbeat: " + json_encode(heartbeat) + "\n";
report += "- Schema passed: " + json_encode(schema_passed) + "\n";
report += "- Redacted: " + json_encode(redacted) + "\n";
report += "- Sources mutated: " + json_encode(mutated) + "\n";
report += "- Verifier accepted: " + json_encode(accepted) + "\n";
report += "- Decision: `" + decision + "`\n";
report += "- Verification type: software_test\n\n";
report += "## Scanner\n\n" + scan_summary + "\n\n";
report += "## Schema validator\n\n" + schema_summary + "\n\n";
report += "## Verifier\n\n" + verify_reason + "\n\n";
report += "Evidence: " + verify_evidence + "\n";
let artifact = write_scratch_file("index-triage-report.md", report);

complete(#{
    path: artifact,
    decision: decision,
    findings_count: findings_count,
    unexpected_count: unexpected_count,
    schema_passed: schema_passed,
    verification_type: "software_test",
    approval_required: decision != "advance",
});
