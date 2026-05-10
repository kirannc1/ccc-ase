import { http, HttpResponse } from "msw";

import { stableId } from "@/utils/hash";

export const handlers = [
  http.get("/api/kpis", () =>
    HttpResponse.json({
      kpis: [
        { id: "kpi-1", label: "SLA Breach Risk", value: 0.22, trend: -0.03, unit: "%" },
        { id: "kpi-2", label: "Attrition Risk", value: 0.34, trend: 0.05, unit: "%" }
      ]
    })
  ),

  http.post("/api/scenario/simulate", async ({ request }) => {
    const body = (await request.json()) as { tenant_id: string; features: Record<string, number>; graph_signals: string[]; constraints: Record<string, number> };
    const tenant = body.tenant_id;
    return HttpResponse.json({
      tenant_id: tenant,
      scenarios: [
        { scenario_id: stableId("scn", `${tenant}:no_action:3`), tenant_id: tenant, name: "no_action", summary: "baseline", score: 0.3, assumptions: [], impacts: {} },
        { scenario_id: stableId("scn", `${tenant}:automation:3`), tenant_id: tenant, name: "automation", summary: "automation uplift", score: 0.6, assumptions: [], impacts: {} }
      ]
    });
  }),

  http.post("/api/optimization/rank", async ({ request }) => {
    const body = (await request.json()) as { tenant_id: string; scenarios: Array<{ scenario_id: string; score: number }> };
    const best = body.scenarios[0]?.scenario_id ?? null;
    return HttpResponse.json({
      tenant_id: body.tenant_id,
      ranked_scenarios: body.scenarios.map((scenario) => ({ scenario_id: scenario.scenario_id, score: scenario.score, rationale: "base score" })),
      best_scenario_id: best,
      notes: []
    });
  }),

  http.post("/api/decision/resolve", async ({ request }) => {
    const body = (await request.json()) as { tenant_id: string; optimization: { best_scenario_id: string | null; ranked_scenarios: unknown[] } };
    return HttpResponse.json({
      decision_id: stableId("dec", `${body.tenant_id}:${body.optimization.best_scenario_id ?? "none"}`),
      tenant_id: body.tenant_id,
      chosen_scenario_id: body.optimization.best_scenario_id,
      rationale: "best optimized scenario selected",
      confidence: 0.7,
      scorecard: { ranked: body.optimization.ranked_scenarios.length }
    });
  }),

  http.post("/api/explanation/generate", async ({ request }) => {
    const body = (await request.json()) as { tenant_id: string; decision: { decision_id: string; confidence: number; rationale: string; chosen_scenario_id: string | null; scorecard: unknown } };
    return HttpResponse.json({
      tenant_id: body.tenant_id,
      explanation_id: stableId("exp", `${body.tenant_id}:${body.decision.decision_id}`),
      text: `decision summary: ${body.decision.rationale}`,
      bullets: [`confidence: ${body.decision.confidence}`]
    });
  }),

  http.post("/api/audit/replay", async ({ request }) => {
    const body = (await request.json()) as { tenant_id: string };
    const now = new Date().toISOString();
    return HttpResponse.json({
      tenant_id: body.tenant_id,
      events: [
        { event_id: "e1", tenant_id: body.tenant_id, correlation_id: "c1", event_type: "decision.created", resource_id: "decision", payload: {}, created_at: now }
      ]
    });
  }),

  http.post("/api/overrides", async ({ request }) => HttpResponse.json(await request.json()))
];

