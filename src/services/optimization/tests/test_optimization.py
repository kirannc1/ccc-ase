from services.common.models import OptimizationRequest, ScenarioArtifact
from services.optimization.core import OptimizationService


def test_optimization_ranking():
    result = OptimizationService().optimize(
        OptimizationRequest(
            tenant_id="tenant-a",
            scenarios=[
                ScenarioArtifact(scenario_id="s1", tenant_id="tenant-a", name="a", summary="a", score=0.4),
                ScenarioArtifact(scenario_id="s2", tenant_id="tenant-a", name="b", summary="b", score=0.8),
            ],
            constraints={"cost": 0.1},
        )
    )
    assert result.best_scenario_id == "s2"
    assert result.ranked_scenarios[0].scenario_id == "s2"

