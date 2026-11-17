def test_react_stops_at_step_cap(public_db):
    from lab8.db import connect
    from lab8.runtime import run_react
    from lab8.schemas import Budget

    conn = connect(public_db)
    try:
        budget = Budget()
        outcome = run_react(
            conn,
            budget,
            observation={"claim": {"claim_id": "C-001"}},
            decide=lambda _: {"tool": "lookup_policy", "args": {}},
            max_steps=2,
            worker=True,
        )
        assert outcome["stopped"] == "step_cap"
        assert outcome["final"]["error_reason"] == "step_cap"
        assert budget.tool_calls == 2
    finally:
        conn.close()
