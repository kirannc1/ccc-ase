import { NextResponse } from "next/server";

import { OptimizationRequestSchema } from "@/types/domain";

function bounded(value: number, lower = 0, upper = 1) {
  return Math.max(lower, Math.min(upper, value));
}

export async function POST(request: Request) {
  const body = OptimizationRequestSchema.parse(await request.json());
  const penalty = Object.values(body.constraints).reduce((sum, value) => sum + value, 0);

  const ranked = body.scenarios
    .map((scenario) => {
      const impactScore = Object.values(scenario.impacts ?? {}).reduce((sum, value) => sum + value, 0);
      const score = Number(bounded(scenario.score + impactScore - penalty).toFixed(3));
      return { scenario_id: scenario.scenario_id, score, rationale: penalty ? "constraint penalty applied" : "base score" };
    })
    .sort((a, b) => b.score - a.score);

  return NextResponse.json({
    tenant_id: body.tenant_id,
    ranked_scenarios: ranked,
    best_scenario_id: ranked[0]?.scenario_id ?? null,
    notes: []
  });
}

