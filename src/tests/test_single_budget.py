import pytest

from lab8.config_loader import pricing
from lab8.shapes.single import run_claim


def test_single_budget_tracks_mock_llm_tokens_and_cost(public_db):
    result = run_claim("C-001", seed=11, store_path=str(public_db))

    assert result.model_calls == 5
    assert result.input_tokens > 0
    assert result.output_tokens > 0

    prices = pricing()
    expected_cost = (
        result.tool_calls * float(prices["tool_call_vnd"])
        + result.input_tokens / 1000 * float(prices["input_per_1k_tokens_vnd"])
        + result.output_tokens / 1000 * float(prices["output_per_1k_tokens_vnd"])
    )
    assert result.cost_estimate == pytest.approx(expected_cost, abs=1e-6)
