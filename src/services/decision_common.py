from __future__ import annotations

from hashlib import sha1

from services.common.models import DecisionArtifact, ExplanationArtifact, OptimizationArtifact, ScenarioArtifact


def bounded(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def score_scenario(scenario: ScenarioArtifact, constraint_weights: dict[str, float]) -> float:
    impact_score = sum(scenario.impacts.values())
    constraint_penalty = sum(constraint_weights.values()) if constraint_weights else 0.0
    return round(bounded(scenario.score + impact_score - constraint_penalty), 3)


def decision_id(tenant_id: str, scenario_id: str | None) -> str:
    token = f"{tenant_id}:{scenario_id or 'none'}".encode()
    return f"dec_{sha1(token).hexdigest()[:12]}"


def explanation_id(tenant_id: str, decision_id_value: str) -> str:
    token = f"{tenant_id}:{decision_id_value}".encode()
    return f"exp_{sha1(token).hexdigest()[:12]}"


def render_explanation(decision: DecisionArtifact, tone: str = "executive") -> ExplanationArtifact:
    lines = [
        f"{tone.title()} decision summary: {decision.rationale}.",
        f"Chosen scenario: {decision.chosen_scenario_id or 'none'}.",
        f"Confidence: {decision.confidence:.2f}.",
    ]
    bullets = [
        f"Decision scorecard: {decision.scorecard}",
        f"Decision confidence: {decision.confidence:.2f}",
    ]
    return ExplanationArtifact(
        tenant_id=decision.tenant_id,
        explanation_id=explanation_id(decision.tenant_id, decision.decision_id),
        text=" ".join(lines),
        bullets=bullets,
    )
