from services.common.models import ScenarioSimulationRequest
from services.scenario_simulation.core import ScenarioSimulationService


def test_scenario_generation():
    result = ScenarioSimulationService().simulate(
        ScenarioSimulationRequest(
            tenant_id="tenant-a",
            features={"engagement": 8.0, "absenteeism": 2.0},
            graph_signals=["skill_fragility"],
            constraints={"cost": 1.0},
        )
    )
    assert len(result) == 3
    assert result[0].score >= result[-1].score

