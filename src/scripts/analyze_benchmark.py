"""Recompute and print benchmark metrics grouped by shape."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lab8.metrics import summarize

SHAPES = ("workflow", "single", "orchestrator", "swarm")
DEFAULT_REPORT = Path(__file__).resolve().parents[1] / "reports" / "benchmark.json"


def aggregate_trials(trials: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Aggregate raw trial rows using the metric definitions shared by the benchmark."""
    required_fields = {
        "shape",
        "claim_id",
        "seed",
        "passed",
        "cost_estimate",
        "steps",
        "model_calls",
        "tool_calls",
    }
    for index, trial in enumerate(trials):
        missing_fields = required_fields - trial.keys()
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(f"trial {index} is missing required field(s): {missing}")

    summaries = summarize(trials)
    missing = [shape for shape in SHAPES if shape not in summaries]
    if missing:
        raise ValueError(f"benchmark is missing required shape(s): {', '.join(missing)}")
    incomplete = [
        shape
        for shape in SHAPES
        if len(summaries[shape]["seed_pass_rates"]) != 5
    ]
    if incomplete:
        raise ValueError(
            "each required shape must contain trials for all five seeds: "
            + ", ".join(incomplete)
        )
    return summaries


def _rate(value: float | None) -> str:
    return "unavailable" if value is None else f"{value:.1%}"


def _vnd(value: float | None) -> str:
    return "unavailable" if value is None else f"{value:,.2f}"


def _steps(value: float | None) -> str:
    if value is None:
        return "unavailable"
    return str(int(value)) if value.is_integer() else f"{value:.2f}"


def render_report(summaries: dict[str, dict[str, Any]]) -> str:
    """Format the requested benchmark metrics in a stable shape order."""
    lines = [
        "Benchmark analysis by shape",
        "Cost: simulated VND (not an API bill) | Latency: unavailable",
    ]
    shape_order = [*SHAPES, *sorted(set(summaries) - set(SHAPES))]
    for shape in shape_order:
        stats = summaries[shape]
        lines.append(f"\n{shape}")
        lines.append(
            f"  Pass rate: {_rate(stats['pass_rate'])} "
            f"({stats['successes']}/{stats['graded_trials']} graded trials)"
        )
        lines.append(f"  Pass^5: {_rate(stats['pass_5'])}")

        seed_rates = stats["seed_pass_rates"]
        if seed_rates:
            ordered_rates = sorted(seed_rates.items(), key=lambda item: int(item[0]))
            rates_text = ", ".join(f"{seed}: {_rate(rate)}" for seed, rate in ordered_rates)
        else:
            rates_text = "unavailable"
        lines.append(f"  Seed pass rates: {rates_text}")
        lines.append(
            f"  Seed variance (population): {stats['seed_variance']!s}; "
            f"min: {_rate(stats['seed_min'])}; max: {_rate(stats['seed_max'])}"
        )

        lines.append(
            f"  Simulated cost: total {_vnd(stats['total_simulated_cost_vnd'])} VND; "
            f"per success {_vnd(stats['cost_per_success_vnd'])} VND"
        )
        lines.append(
            f"  Trace steps: mean {_steps(stats['mean_steps'])}; "
            f"p95 {_steps(stats['p95_steps'])}"
        )
        lines.append("  Latency: unavailable")
    return "\n".join(lines)


def analyze_file(path: Path) -> str:
    """Read a benchmark JSON file, recompute its by-shape metrics, and render them."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read benchmark JSON at {path}: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("trials"), list):
        raise ValueError("benchmark JSON must be an object containing a trials list")
    trials = payload["trials"]
    if any(not isinstance(trial, dict) for trial in trials):
        raise ValueError("every benchmark trial must be a JSON object")
    controls = payload.get("controlled_variables")
    seeds = controls.get("seeds") if isinstance(controls, dict) else None
    if (
        not isinstance(seeds, list)
        or len(seeds) != 5
        or any(isinstance(seed, bool) or not isinstance(seed, int) for seed in seeds)
        or len(set(seeds)) != 5
    ):
        raise ValueError("benchmark controlled_variables must specify five distinct integer seeds")
    trial_seeds = {trial.get("seed") for trial in trials}
    if trial_seeds != set(seeds):
        raise ValueError("benchmark trials do not match the five configured seeds")
    return render_report(aggregate_trials(trials))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aggregate benchmark metrics by shape")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_REPORT,
        help="benchmark JSON path (default: reports/benchmark.json)",
    )
    args = parser.parse_args(argv)
    try:
        print(analyze_file(args.input))
    except ValueError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
