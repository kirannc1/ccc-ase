"use client";

import { Button, Card, CardHeader, Field, Input, Text, Title2 } from "@fluentui/react-components";
import { useMemo, useState } from "react";

import { ChartWrapper, type EChartsOption } from "@/components/ChartWrapper/ChartWrapper";
import { useDecisioning } from "@/hooks/useDecisioning";
import { useExplanation } from "@/hooks/useExplanation";
import { useOptimization } from "@/hooks/useOptimization";
import { useScenarioSimulation } from "@/hooks/useScenarioSimulation";
import { api } from "@/services/api";
import { OverrideRequest } from "@/types/domain";

export function RecommendationDetailScreen() {
  const simulate = useScenarioSimulation();
  const optimize = useOptimization();
  const decide = useDecisioning();
  const explain = useExplanation();
  const [overrideReason, setOverrideReason] = useState("manual adjustment");
  const [overrideStatus, setOverrideStatus] = useState<OverrideRequest["override_status"]>("APPROVED");

  const confidenceOption = useMemo<EChartsOption>(() => {
    const before = decide.data?.confidence ?? 0;
    const after = overrideStatus === "REJECTED" ? Math.max(0, before - 0.2) : before;
    return {
      xAxis: { type: "category", data: ["Before", "After"] },
      yAxis: { type: "value", min: 0, max: 1 },
      series: [{ type: "bar", data: [before, after] }]
    };
  }, [decide.data, overrideStatus]);

  const runFlow = async () => {
    const sim = await simulate.mutateAsync({
      tenant_id: "tenant-a",
      features: { engagement: 8, absenteeism: 2 },
      graph_signals: ["skill_fragility"],
      constraints: { cost: 1 }
    });
    const opt = await optimize.mutateAsync({ tenant_id: sim.tenant_id, scenarios: sim.scenarios, constraints: { cost: 1 } });
    const decision = await decide.mutateAsync({ tenant_id: sim.tenant_id, optimization: opt, policy: null });
    await explain.mutateAsync({ tenant_id: sim.tenant_id, decision, tone: "executive" });
  };

  const applyOverride = async () => {
    if (!decide.data) return;
    await api.applyOverride({
      tenant_id: decide.data.tenant_id,
      recommendation_id: "rec_1",
      decision_id: decide.data.decision_id,
      actor_id: "user_1",
      reason: overrideReason,
      override_status: overrideStatus
    });
  };

  return (
    <div style={{ display: "grid", gap: 16, width: "100%" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <Title2>Recommendation Detail</Title2>
        <Button appearance="primary" onClick={runFlow} disabled={simulate.isPending || optimize.isPending || decide.isPending || explain.isPending}>
          Run Decision Flow
        </Button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 420px", gap: 12 }}>
        <Card>
          <CardHeader header={<Text weight="semibold">Decision Artifact</Text>} description={<Text>{decide.data?.decision_id ?? "Run flow to generate"}</Text>} />
          <div style={{ padding: 16, display: "grid", gap: 8 }}>
            <Text>Chosen: {decide.data?.chosen_scenario_id ?? "-"}</Text>
            <Text>Confidence: {decide.data?.confidence ?? "-"}</Text>
            <Text>Rationale: {decide.data?.rationale ?? "-"}</Text>
            <Text>Scorecard: {decide.data ? JSON.stringify(decide.data.scorecard) : "-"}</Text>
          </div>
        </Card>

        <Card>
          <CardHeader header={<Text weight="semibold">Override</Text>} />
          <div style={{ padding: 16, display: "grid", gap: 12 }}>
            <Field label="Override reason">
              <Input value={overrideReason} onChange={(_, data) => setOverrideReason(data.value)} />
            </Field>
            <Field label="Override status (APPROVED/REJECTED)">
              <Input value={overrideStatus} onChange={(_, data) => setOverrideStatus(data.value === "REJECTED" ? "REJECTED" : "APPROVED")} />
            </Field>
            <Button appearance="secondary" onClick={applyOverride} disabled={!decide.data}>
              Apply Override
            </Button>
          </div>
        </Card>
      </div>

      <Card>
        <CardHeader header={<Text weight="semibold">Before vs After</Text>} description={<Text>Confidence delta</Text>} />
        <div style={{ padding: 16 }}>
          <ChartWrapper option={confidenceOption} height={240} />
        </div>
      </Card>

      <Card>
        <CardHeader header={<Text weight="semibold">Explanation</Text>} description={<Text>{explain.data?.explanation_id ?? ""}</Text>} />
        <div style={{ padding: 16 }}>
          <Text>{explain.data?.text ?? "Run flow to generate explanation"}</Text>
        </div>
      </Card>
    </div>
  );
}

