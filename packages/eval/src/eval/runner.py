from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from playbook_engine import PlaybookEngine, load_playbook_config


@dataclass
class ScenarioResult:
    scenario_id: str
    passed: bool
    message: str


def scenarios_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "scenarios"


def load_scenarios(category: str | None = None) -> list[dict[str, Any]]:
    root = scenarios_dir()
    files = sorted(root.rglob("*.json"))
    out: list[dict[str, Any]] = []
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        if category and data.get("category") != category:
            continue
        out.append(data)
    return out


def run_playbook_scenario(engine: PlaybookEngine, scenario: dict[str, Any]) -> ScenarioResult:
    sid = scenario["id"]
    expect = scenario.get("expect", {})
    fixtures = scenario.get("mock_fixtures", {})
    action = scenario.get("playbook_action")

    if action == "icp":
        decision = engine.evaluate_icp(
            employee_count=fixtures.get("employee_count"),
            country=fixtures.get("country"),
            industry=fixtures.get("industry"),
        )
    elif action == "citations":
        decision = engine.evaluate_citations(sources_count=int(fixtures.get("sources_count", 0)))
    elif action == "stage":
        decision = engine.evaluate_stage_change(
            approved=bool(fixtures.get("approved", False)),
            shadow_mode=bool(fixtures.get("shadow_mode", False)),
        )
    else:
        return ScenarioResult(sid, False, f"unknown playbook_action {action}")

    label = decision.to_eval_label()
    expected = expect.get("playbook")
    if expected and label != expected:
        return ScenarioResult(sid, False, f"expected {expected}, got {label} ({decision.code})")
    expected_code = expect.get("code")
    if expected_code and decision.code != expected_code:
        return ScenarioResult(sid, False, f"expected code {expected_code}, got {decision.code}")
    return ScenarioResult(sid, True, "ok")


def run_orchestrator_scenario(scenario: dict[str, Any]) -> ScenarioResult:
    from sales_api.orchestrator import LeadOrchestrator

    sid = scenario["id"]
    fixtures = scenario.get("mock_fixtures", {})
    expect = scenario.get("expect", {})
    engine = PlaybookEngine(load_playbook_config(None))
    orch = LeadOrchestrator(engine)
    result = orch.run(
        email=fixtures.get("email", "test@example.com"),
        first_name=fixtures.get("first_name", "Test"),
        company=fixtures.get("company", "Co"),
        employee_count=fixtures.get("employee_count"),
        country=fixtures.get("country"),
        industry=fixtures.get("industry"),
    )
    if expect.get("qualified") is not None and result.qualified != expect["qualified"]:
        return ScenarioResult(
            sid,
            False,
            f"expected qualified={expect['qualified']}, got {result.qualified}",
        )
    if expect.get("status") and result.status != expect["status"]:
        return ScenarioResult(
            sid, False, f"expected status {expect['status']}, got {result.status}"
        )
    if expect.get("has_draft") is not None:
        has = result.draft is not None
        if has != expect["has_draft"]:
            return ScenarioResult(
                sid, False, f"expected has_draft={expect['has_draft']}, got {has}"
            )
    return ScenarioResult(sid, True, "ok")


def run_all(config_path: Path | str | None = None) -> list[ScenarioResult]:
    engine = PlaybookEngine(load_playbook_config(config_path))
    results: list[ScenarioResult] = []
    for scenario in load_scenarios():
        cat = scenario.get("category", "playbook")
        if cat == "playbook":
            results.append(run_playbook_scenario(engine, scenario))
        elif cat == "orchestrator":
            results.append(run_orchestrator_scenario(scenario))
        else:
            results.append(
                ScenarioResult(scenario.get("id", "?"), False, f"unknown category {cat}")
            )
    return results


def main() -> None:
    root = Path(__file__).resolve().parents[4]
    cfg = root / "config" / "playbook.yaml"
    config_path = cfg if cfg.is_file() else None
    results = run_all(config_path)
    failed = [r for r in results if not r.passed]
    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        print(f"{mark}\t{r.scenario_id}\t{r.message}")
    if failed:
        sys.exit(1)
    print(f"All {len(results)} scenarios passed.")


if __name__ == "__main__":
    main()
