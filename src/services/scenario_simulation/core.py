from __future__ import annotations

from hashlib import sha1

from services.common.models import ScenarioArtifact, ScenarioSimulationRequest
from services.decision_common import bounded


class ScenarioSimulationService:
    def simulate(self, request: ScenarioSimulationRequest) -> list[ScenarioArtifact]:
        feature_score = sum(request.features.values()) / max(1, len(request.features))
        signal_bonus = 0.05 * len(request.graph_signals)
        constraint_penalty = 0.02 * len(request.constraints)
        base = bounded((feature_score / 10.0) + signal_bonus - constraint_penalty)
        scenarios = [
            self._build_scenario(request.tenant_id, "no_action", base * 0.5, "baseline", request.features),
            self._build_scenario(request.tenant_id, "targeted_action", base * 0.8, "targeted intervention", request.features),
            self._build_scenario(request.tenant_id, "automation", base, "automation uplift", request.features),
        ]
        return sorted(scenarios, key=lambda item: item.score, reverse=True)

    def _build_scenario(self, tenant_id: str, name: str, score: float, summary: str, features: dict[str, float]) -> ScenarioArtifact:
        token = f"{tenant_id}:{name}:{len(features)}".encode()
        scenario_id = f"scn_{sha1(token).hexdigest()[:12]}"
        impacts = {feature: round(value / 10.0, 3) for feature, value in features.items()}
        return ScenarioArtifact(
            scenario_id=scenario_id,
            tenant_id=tenant_id,
            name=name,
            summary=summary,
            score=round(bounded(score), 3),
            assumptions=[f"{feature}=stable" for feature in list(features)[:2]],
            impacts=impacts,
        )

