from upi.research import build_research_report, render_research_markdown


def valid_node(address: str, title: str) -> dict:
    return {
        "record_type": "node",
        "payload": {
            "address": address,
            "title": title,
            "description": "Research candidate.",
            "status": "EST",
            "evidence": [{"type": "calculation", "source": "fixture"}],
        },
    }


def test_research_mode_is_non_blocking_and_preserves_open_branches():
    session = {
        "format": "upi-research-session",
        "version": "0.1.0",
        "session_id": "research-8200",
        "intent": "Explore a cross-domain functional loop.",
        "items": [
            {
                "id": "frequency",
                "title": "Frequency map",
                "links": ["mass"],
                "record": valid_node(
                    "UPI<information_physics,1,inertia,frequency>",
                    "Frequency candidate",
                ),
            },
            {
                "id": "mass",
                "title": "Mass map",
                "links": ["frequency"],
                "record": valid_node(
                    "UPI<information_physics,1,inertia,mass>",
                    "Mass candidate",
                ),
            },
            {
                "id": "open-vortex",
                "title": "Vortex mechanism",
                "function": "rotation -> coupling -> feedback",
            },
        ],
    }

    report = build_research_report(session)

    assert report["mode"] == "research"
    assert report["promotion"] == "none"
    assert report["policy"]["exploration_is_non_blocking"] is True
    assert report["policy"]["closed_loop_is_not_required"] is True
    assert set(report["shadow"]["validated_candidate_ids"]) == {"frequency", "mass"}
    assert report["shadow"]["connected_subchains"] == [["frequency", "mass"]]
    assert any(item["id"] == "open-vortex" for item in report["shadow"]["open_threads"])


def test_research_mode_keeps_invalid_candidate_open():
    session = {
        "format": "upi-research-session",
        "version": "0.1.0",
        "items": [
            {
                "id": "unknown",
                "title": "Unresolved claim",
                "record": {
                    "record_type": "node",
                    "payload": {
                        "address": "UPI<physics,1,test,unknown>",
                        "title": "Unresolved",
                        "description": "No evidence.",
                        "status": "HYP",
                    },
                },
            }
        ],
    }

    report = build_research_report(session)

    assert report["shadow"]["validated_candidate_ids"] == []
    assert report["shadow"]["open_threads"][0]["id"] == "unknown"


def test_research_markdown_exposes_open_threads():
    report = build_research_report(
        {
            "format": "upi-research-session",
            "version": "0.1.0",
            "session_id": "md",
            "items": [{"id": "x", "title": "Open"}],
        }
    )
    rendered = render_research_markdown(report)
    assert "# UPI Research Mode" in rendered
    assert "Open threads" in rendered
    assert "x" in rendered


def test_shadow_preserves_original_and_rejects_duplicate_identity():
    session = {
        "format": "upi-research-session",
        "version": "0.1.0",
        "items": [
            {"id": "same", "record": valid_node("UPI<physics,1,test,a>", "A")},
            {"id": "same", "record": valid_node("UPI<physics,1,test,b>", "B")},
            {"id": "raw", "record": "not an object", "unknown_equation": "x = ?"},
        ],
    }
    report = build_research_report(session)
    assert report["input_snapshot"] == session
    assert report["shadow"]["validated_candidate_ids"] == []
    session["items"].clear()
    assert len(report["input_snapshot"]["items"]) == 3


def test_unvalidated_link_does_not_close_a_valid_node():
    report = build_research_report(
        {
            "items": [
                {
                    "id": "valid",
                    "links": ["open"],
                    "record": valid_node("UPI<physics,1,test,valid>", "Valid"),
                },
                {"id": "open"},
            ]
        }
    )
    assert report["shadow"]["connected_validated_ids"] == []
    assert {n["id"] for n in report["shadow"]["open_threads"]} == {"valid", "open"}
