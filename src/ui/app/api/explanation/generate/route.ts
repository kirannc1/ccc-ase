import { NextResponse } from "next/server";

import { ExplanationRequestSchema } from "@/types/domain";
import { stableId } from "@/utils/hash";

export async function POST(request: Request) {
  const body = ExplanationRequestSchema.parse(await request.json());
  const explanationId = stableId("exp", `${body.tenant_id}:${body.decision.decision_id}`);
  return NextResponse.json({
    tenant_id: body.tenant_id,
    explanation_id: explanationId,
    text: `${body.tone} decision summary: ${body.decision.rationale}. Chosen scenario: ${body.decision.chosen_scenario_id ?? "none"}. Confidence: ${body.decision.confidence.toFixed(2)}.`,
    bullets: [
      `Decision scorecard: ${JSON.stringify(body.decision.scorecard)}`,
      `Decision confidence: ${body.decision.confidence.toFixed(2)}`
    ]
  });
}

