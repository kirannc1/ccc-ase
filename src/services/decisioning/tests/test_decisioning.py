from services.common.models import DecisionRequest, OptimizationArtifact, RankedScenario
from services.decisioning.core import DecisioningService


def test_decisioning_selects_best():
    result = DecisioningService().decide(
        DecisionRequest(
            tenant_id="tenant-a",
            optimization=OptimizationArtifact(
                tenant_id="tenant-a",
                ranked_scenarios=[
                    RankedScenario(scenario_id="s1", score=0.3, rationale="x"),
                    RankedScenario(scenario_id="s2", score=0.9, rationale="y"),
                ],
                best_scenario_id="s2",
            ),
        )
    )
    assert result.chosen_scenario_id == "s2"
    assert result.confidence >= 0.7

