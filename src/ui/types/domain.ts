import { z } from "zod";

export const HealthResponseSchema = z.object({
  status: z.literal("ok"),
  service: z.string()
});
export type HealthResponse = z.infer<typeof HealthResponseSchema>;

export const KpiSchema = z.object({
  id: z.string(),
  label: z.string(),
  value: z.number(),
  trend: z.number(),
  unit: z.string().optional()
});
export type Kpi = z.infer<typeof KpiSchema>;

export const ScenarioArtifactSchema = z.object({
  scenario_id: z.string(),
  tenant_id: z.string(),
  name: z.string(),
  summary: z.string(),
  score: z.number(),
  assumptions: z.array(z.string()).default([]),
  impacts: z.record(z.number()).default({})
});
export type ScenarioArtifact = z.infer<typeof ScenarioArtifactSchema>;

export const ScenarioSimulationRequestSchema = z.object({
  tenant_id: z.string(),
  features: z.record(z.number()).default({}),
  graph_signals: z.array(z.string()).default([]),
  constraints: z.record(z.number()).default({})
});
export type ScenarioSimulationRequest = z.infer<typeof ScenarioSimulationRequestSchema>;

export const ScenarioSimulationResponseSchema = z.object({
  tenant_id: z.string(),
  scenarios: z.array(ScenarioArtifactSchema)
});
export type ScenarioSimulationResponse = z.infer<typeof ScenarioSimulationResponseSchema>;

export const OptimizationRequestSchema = z.object({
  tenant_id: z.string(),
  scenarios: z.array(ScenarioArtifactSchema),
  constraints: z.record(z.number()).default({})
});
export type OptimizationRequest = z.infer<typeof OptimizationRequestSchema>;

export const RankedScenarioSchema = z.object({
  scenario_id: z.string(),
  score: z.number(),
  rationale: z.string()
});
export type RankedScenario = z.infer<typeof RankedScenarioSchema>;

export const OptimizationArtifactSchema = z.object({
  tenant_id: z.string(),
  ranked_scenarios: z.array(RankedScenarioSchema),
  best_scenario_id: z.string().nullable().optional(),
  notes: z.array(z.string()).default([])
});
export type OptimizationArtifact = z.infer<typeof OptimizationArtifactSchema>;

export const PolicyResponseSchema = z.object({
  tenant_id: z.string(),
  allowed: z.boolean(),
  violations: z.array(z.string()).default([]),
  evaluated_metrics: z.record(z.number()).default({})
});
export type PolicyResponse = z.infer<typeof PolicyResponseSchema>;

export const DecisionRequestSchema = z.object({
  tenant_id: z.string(),
  optimization: OptimizationArtifactSchema,
  policy: PolicyResponseSchema.nullable().optional()
});
export type DecisionRequest = z.infer<typeof DecisionRequestSchema>;

export const DecisionArtifactSchema = z.object({
  decision_id: z.string(),
  tenant_id: z.string(),
  chosen_scenario_id: z.string().nullable().optional(),
  rationale: z.string(),
  confidence: z.number(),
  scorecard: z.record(z.number()).default({})
});
export type DecisionArtifact = z.infer<typeof DecisionArtifactSchema>;

export const ExplanationRequestSchema = z.object({
  tenant_id: z.string(),
  decision: DecisionArtifactSchema,
  tone: z.string().default("executive")
});
export type ExplanationRequest = z.infer<typeof ExplanationRequestSchema>;

export const ExplanationArtifactSchema = z.object({
  tenant_id: z.string(),
  explanation_id: z.string(),
  text: z.string(),
  bullets: z.array(z.string()).default([])
});
export type ExplanationArtifact = z.infer<typeof ExplanationArtifactSchema>;

export const AuditEventSchema = z.object({
  event_id: z.string(),
  tenant_id: z.string(),
  correlation_id: z.string(),
  event_type: z.string(),
  resource_id: z.string(),
  payload: z.record(z.unknown()),
  created_at: z.string()
});
export type AuditEvent = z.infer<typeof AuditEventSchema>;

export const ReplayRequestSchema = z.object({
  tenant_id: z.string(),
  correlation_id: z.string().nullable().optional(),
  resource_id: z.string().nullable().optional()
});
export type ReplayRequest = z.infer<typeof ReplayRequestSchema>;

export const ReplayArtifactSchema = z.object({
  tenant_id: z.string(),
  events: z.array(AuditEventSchema)
});
export type ReplayArtifact = z.infer<typeof ReplayArtifactSchema>;

export const OverrideRequestSchema = z.object({
  tenant_id: z.string(),
  recommendation_id: z.string(),
  decision_id: z.string(),
  actor_id: z.string(),
  reason: z.string(),
  override_status: z.enum(["APPROVED", "REJECTED"])
});
export type OverrideRequest = z.infer<typeof OverrideRequestSchema>;

