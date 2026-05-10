import { NextResponse } from "next/server";

import { DecisionRequestSchema } from "@/types/domain";
import { stableId } from "@/utils/hash";

function bounded(value: number, lower = 0, upper = 1) {
  return Math.max(lower, Math.min(upper, value));
}

export async function POST(request: Request) {
  const body = DecisionRequestSchema.parse(await request.json());
  const best = body.optimization.best_scenario_id ?? null;
  const baseConfidence = best ? 0.7 : 0.4;
  const policyPenalty = body.policy && body.policy.allowed === false ? 0.2 : 0;
  const confidence = Number(bounded(baseConfidence - policyPenalty).toFixed(3));
  const decisionId = stableId("dec", `${body.tenant_id}:${best ?? "none"}`);

  return NextResponse.json({
    decision_id: decisionId,
    tenant_id: body.tenant_id,
    chosen_scenario_id: best,
    rationale: "best optimized scenario selected",
    confidence,
    scorecard: {
      ranked: body.optimization.ranked_scenarios.length,
      ...(policyPenalty ? { policy_penalty: body.policy?.violations.length ?? 0 } : {})
    }
  });
}

