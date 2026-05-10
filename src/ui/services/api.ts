import {
  DecisionArtifactSchema,
  DecisionRequest,
  DecisionRequestSchema,
  ExplanationArtifactSchema,
  ExplanationRequest,
  ExplanationRequestSchema,
  Kpi,
  KpiSchema,
  OverrideRequest,
  OverrideRequestSchema,
  ReplayArtifactSchema,
  ReplayRequest,
  ReplayRequestSchema,
  ScenarioSimulationRequest,
  ScenarioSimulationRequestSchema,
  ScenarioSimulationResponseSchema,
  OptimizationRequest,
  OptimizationRequestSchema,
  OptimizationArtifactSchema
} from "@/types/domain";
import { fetchJson } from "@/services/http";
import { z } from "zod";

const KpisResponseSchema = z.object({ kpis: z.array(KpiSchema) });

export const api = {
  getKpis(): Promise<{ kpis: Kpi[] }> {
    return fetchJson("/api/kpis", KpisResponseSchema);
  },

  simulateScenario(request: ScenarioSimulationRequest) {
    const body = ScenarioSimulationRequestSchema.parse(request);
    return fetchJson("/api/scenario/simulate", ScenarioSimulationResponseSchema, { method: "POST", body });
  },

  rankOptimization(request: OptimizationRequest) {
    const body = OptimizationRequestSchema.parse(request);
    return fetchJson("/api/optimization/rank", OptimizationArtifactSchema, { method: "POST", body });
  },

  resolveDecision(request: DecisionRequest) {
    const body = DecisionRequestSchema.parse(request);
    return fetchJson("/api/decision/resolve", DecisionArtifactSchema, { method: "POST", body });
  },

  generateExplanation(request: ExplanationRequest) {
    const body = ExplanationRequestSchema.parse(request);
    return fetchJson("/api/explanation/generate", ExplanationArtifactSchema, { method: "POST", body });
  },

  applyOverride(request: OverrideRequest) {
    const body = OverrideRequestSchema.parse(request);
    return fetchJson("/api/overrides", OverrideRequestSchema, { method: "POST", body });
  },

  replayAudit(request: ReplayRequest) {
    const body = ReplayRequestSchema.parse(request);
    return fetchJson("/api/audit/replay", ReplayArtifactSchema, { method: "POST", body });
  }
};

