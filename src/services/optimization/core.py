from __future__ import annotations

from services.common.models import OptimizationArtifact, OptimizationRequest, RankedScenario
from services.decision_common import score_scenario


class OptimizationService:
    def optimize(self, request: OptimizationRequest) -> OptimizationArtifact:
        ranked = [
            RankedScenario(
                scenario_id=scenario.scenario_id,
                score=score_scenario(scenario, request.constraints),
                rationale="constraint-adjusted score",
            )
            for scenario in request.scenarios
        ]
        ranked.sort(key=lambda item: item.score, reverse=True)
        return OptimizationArtifact(
            tenant_id=request.tenant_id,
            ranked_scenarios=ranked,
            best_scenario_id=ranked[0].scenario_id if ranked else None,
            notes=["pareto-lite ranking"],
        )

