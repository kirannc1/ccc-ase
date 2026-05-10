from __future__ import annotations

from services.common.models import ExplanationArtifact, ExplanationRequest
from services.decision_common import render_explanation


class DecisionExplanationService:
    def explain(self, request: ExplanationRequest) -> ExplanationArtifact:
        return render_explanation(request.decision, request.tone)

