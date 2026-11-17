from scripts.analyze_benchmark import aggregate_trials, render_report


def test_aggregate_report_includes_required_metrics_per_shape():
    trials = []
    for shape in ("workflow", "single", "orchestrator", "swarm"):
        for seed_index, seed in enumerate((11, 22, 33, 44, 55), start=1):
            for claim_id in ("A", "B"):
                passed = claim_id == "A" or seed != 55
                trials.append(
                    {
                        "shape": shape,
                        "claim_id": claim_id,
                        "seed": seed,
                        "passed": passed,
                        "cost_estimate": 10.0,
                        "steps": float(seed_index),
                        "model_calls": 1,
                        "tool_calls": 2,
                    }
                )

    summaries = aggregate_trials(trials)
    stats = summaries["single"]
    assert stats["pass_rate"] == 0.9
    assert stats["pass_5"] == 0.5
    assert stats["seed_pass_rates"] == {
        "11": 1.0,
        "22": 1.0,
        "33": 1.0,
        "44": 1.0,
        "55": 0.5,
    }
    assert stats["seed_min"] == 0.5
    assert stats["seed_max"] == 1.0
    assert stats["seed_variance"] == 0.04
    assert stats["total_simulated_cost_vnd"] == 100.0
    assert stats["cost_per_success_vnd"] == 100 / 9
    assert stats["mean_steps"] == 3.0
    assert stats["p95_steps"] == 5.0

    output = render_report(summaries)
    for expected in (
        "workflow",
        "single",
        "orchestrator",
        "swarm",
        "Pass^5: 50.0%",
        "55: 50.0%",
        "total 100.00 VND",
        "mean 3; p95 5",
        "Latency: unavailable",
    ):
        assert expected in output
