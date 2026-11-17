"""Focused contract tests for Shape C: orchestrator, handoff and trace."""

import json
from pathlib import Path

import pytest

from lab8.durability import InjectedCrash
from lab8.handoff import HandoffError, make_handoff
from lab8.shapes import orchestrator


def read_trace(trace_path: str) -> dict:
    return json.loads(Path(trace_path).read_text(encoding="utf-8"))


def test_handoff_only_has_allowed_fields_and_no_parent_secret():
    handoff = make_handoff(
        request_id="REQ-C-001",
        claim_id="C-001",
        task="check_applicable_policy",
        facts={
            "delay_days": 4,
            "parent_secret": "CANARY_SECRET_PARENT_C-001",
        },
        allowed_tools=[
            "lookup_order",
            "lookup_policy",
            "compute_compensation",
        ],
    )

    assert set(handoff) == {
        "contract_version",
        "request_id",
        "claim_id",
        "principal_scope",
        "task",
        "facts",
        "allowed_tools",
        "max_output_tokens",
    }

    assert "parent_secret" not in handoff
    assert "CANARY_SECRET_PARENT_C-001" not in json.dumps(handoff)

    assert set(handoff["allowed_tools"]).isdisjoint({"issue_refund", "append_audit"})


def test_handoff_rejects_write_tool():
    with pytest.raises(HandoffError):
        make_handoff(
            request_id="REQ-C-001",
            claim_id="C-001",
            task="pay_refund",
            facts={},
            allowed_tools=["issue_refund"],
        )


def test_orchestrator_trace_has_correct_run_id_and_no_secret_or_pii(
    public_db,
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    result = orchestrator.run_claim(
        "C-001",
        seed=11,
        store_path=str(public_db),
    )

    trace = read_trace(result.trace_path)
    trace_text = json.dumps(trace, ensure_ascii=False)

    assert result.run_id == "R-orchestrator-C-001-s11"
    assert trace["run_id"] == result.run_id

    assert "CANARY_SECRET_PARENT_C-001" not in trace_text
    assert "Bearer CANARY_SECRET_PARENT_C-001" not in trace_text

    # Không ghi principal_id hoặc nội dung ticket vào trace.
    assert "P-100" not in trace_text
    assert "Đơn O-107 giao trễ 4 ngày" not in trace_text


def test_orchestrator_forwards_crash_to_issue_refund(
    public_db,
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(InjectedCrash):
        orchestrator.run_claim(
            "C-001",
            seed=11,
            store_path=str(public_db),
            crash_at="after_effect_before_checkpoint",
        )

    trace_path = tmp_path / "traces" / "R-orchestrator-C-001-s11.json"

    trace = json.loads(trace_path.read_text(encoding="utf-8"))

    assert trace["run_id"] == "R-orchestrator-C-001-s11"

    event_kinds = {event["kind"] for event in trace["events"]}

    assert "handoff" in event_kinds
    assert "crash" in event_kinds
