from services.common.models import DecisionArtifact, ExplanationRequest
from services.decision_explanation.core import DecisionExplanationService


def test_explanation_generation():
    result = DecisionExplanationService().explain(
        ExplanationRequest(
            tenant_id="tenant-a",
            decision=DecisionArtifact(
                decision_id="dec_1",
                tenant_id="tenant-a",
                chosen_scenario_id="s2",
                rationale="best optimized scenario selected",
                confidence=0.8,
                scorecard={"ranked": 2.0},
            ),
        )
    )
    assert "best optimized scenario selected" in result.text

