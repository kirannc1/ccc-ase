import { NextResponse } from "next/server";

import { ScenarioSimulationRequestSchema } from "@/types/domain";
import { stableId } from "@/utils/hash";

export async function POST(request: Request) {
  const body = ScenarioSimulationRequestSchema.parse(await request.json());
  const featureScore =
    Object.values(body.features).reduce((sum, value) => sum + value, 0) / Math.max(1, Object.keys(body.features).length);
  const base = Math.max(0, Math.min(1, featureScore / 10 + body.graph_signals.length * 0.05 - Object.keys(body.constraints).length * 0.02));
  const tenant = body.tenant_id;

  const scenarios = [
    { name: "no_action", summary: "baseline", score: base * 0.5 },
    { name: "targeted_action", summary: "targeted intervention", score: base * 0.8 },
    { name: "automation", summary: "automation uplift", score: base }
  ]
    .map((item) => ({
      scenario_id: stableId("scn", `${tenant}:${item.name}:${Object.keys(body.features).length}`),
      tenant_id: tenant,
      name: item.name,
      summary: item.summary,
      score: Number(item.score.toFixed(3)),
      assumptions: Object.keys(body.features).slice(0, 2).map((key) => `${key}=stable`),
      impacts: Object.fromEntries(Object.entries(body.features).map(([k, v]) => [k, Number((v / 10).toFixed(3))]))
    }))
    .sort((a, b) => b.score - a.score);

  return NextResponse.json({ tenant_id: tenant, scenarios });
}

