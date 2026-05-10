from __future__ import annotations

from services.common.models import DecisionArtifact, DecisionRequest
from services.decision_common import bounded, decision_id


class DecisioningService:
    def decide(self, request: DecisionRequest) -> DecisionArtifact:
        best = request.optimization.best_scenario_id
        confidence = 0.7 if best else 0.4
        scorecard = {"ranked": float(len(request.optimization.ranked_scenarios))}
        if request.policy and not request.policy.allowed:
            confidence = bounded(confidence - 0.2)
            scorecard["policy_penalty"] = float(len(request.policy.violations))
        return DecisionArtifact(
            decision_id=decision_id(request.tenant_id, best),
            tenant_id=request.tenant_id,
            chosen_scenario_id=best,
            rationale="best optimized scenario selected",
            confidence=round(confidence, 3),
            scorecard=scorecard,
        )

