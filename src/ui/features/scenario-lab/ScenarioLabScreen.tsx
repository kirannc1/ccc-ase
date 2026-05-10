"use client";

import { Button, Card, CardHeader, Field, Input, Slider, Text, Title2 } from "@fluentui/react-components";
import { useMemo } from "react";

import { ChartWrapper, type EChartsOption } from "@/components/ChartWrapper/ChartWrapper";
import { GraphViewer } from "@/components/GraphViewer/GraphViewer";
import { useOptimization } from "@/hooks/useOptimization";
import { useScenarioSimulation } from "@/hooks/useScenarioSimulation";
import { useScenarioLabStore } from "@/features/scenario-lab/scenarioLabStore";

export function ScenarioLabScreen() {
  const store = useScenarioLabStore();
  const simulate = useScenarioSimulation();
  const optimize = useOptimization();

  const chartOption = useMemo<EChartsOption>(() => {
    const scenarios = simulate.data?.scenarios ?? [];
    return {
      tooltip: { trigger: "axis" },
      legend: { data: ["score"] },
      xAxis: { type: "category", data: scenarios.map((s) => s.name) },
      yAxis: { type: "value", min: 0, max: 1 },
      series: [{ name: "score", type: "line", data: scenarios.map((s) => s.score) }]
    };
  }, [simulate.data]);

  const ranked = optimize.data?.ranked_scenarios ?? [];

  return (
    <div style={{ display: "grid", gridTemplateColumns: "360px 1fr", gap: 16, width: "100%" }}>
      <Card>
        <CardHeader header={<Title2>Scenario Lab</Title2>} description={<Text>Configure and run what-if simulations</Text>} />
        <div style={{ padding: 16, display: "grid", gap: 12 }}>
          <Field label="Tenant">
            <Input value={store.tenantId} onChange={(_, data) => store.setTenantId(data.value)} />
          </Field>
          <Field label={`Leave days (${store.leaveDays})`}>
            <Slider value={store.leaveDays} min={0} max={10} onChange={(_, data) => store.setLeaveDays(data.value)} />
          </Field>
          <Field label={`Coverage (${store.coverage.toFixed(2)})`}>
            <Slider value={store.coverage} min={0} max={1} step={0.05} onChange={(_, data) => store.setCoverage(data.value)} />
          </Field>
          <Field label={`Approval risk (${store.approvalRisk.toFixed(2)})`}>
            <Slider value={store.approvalRisk} min={0} max={1} step={0.05} onChange={(_, data) => store.setApprovalRisk(data.value)} />
          </Field>
          <Button
            appearance="primary"
            onClick={() =>
              simulate.mutate({
                tenant_id: store.tenantId,
                features: { leave_days: store.leaveDays, coverage: store.coverage, approval_risk: store.approvalRisk },
                graph_signals: ["leave_policy"],
                constraints: { min_coverage: 0.7 }
              })
            }
            disabled={simulate.isPending}
          >
            Run Simulation
          </Button>
          <Button
            appearance="secondary"
            onClick={() => {
              if (!simulate.data) return;
              optimize.mutate({ tenant_id: simulate.data.tenant_id, scenarios: simulate.data.scenarios, constraints: { min_coverage: 0.7 } });
            }}
            disabled={!simulate.data || optimize.isPending}
          >
            Rank Options
          </Button>
        </div>
      </Card>

      <div style={{ display: "grid", gap: 16 }}>
        <Card>
          <CardHeader header={<Text weight="semibold">Scenario Outputs</Text>} />
          <div style={{ padding: 16 }}>
            <ChartWrapper option={chartOption} height={260} />
          </div>
        </Card>
        <Card>
          <CardHeader header={<Text weight="semibold">Ranked Scenarios</Text>} description={<Text>{ranked[0] ? `Best: ${ranked[0].scenario_id}` : "Run ranking"}</Text>} />
          <div style={{ padding: 16 }}>
            <GraphViewer
              nodes={[
                { id: "leave", label: "Regular Leave", status: "highlight" },
                { id: "coverage", label: "Coverage", status: store.coverage < 0.7 ? "risk" : "default" },
                { id: "policy", label: "Policy", status: "default" }
              ]}
              edges={[
                { id: "l1", source: "leave", target: "coverage", label: "reduces" },
                { id: "l2", source: "policy", target: "leave", label: "constrains" }
              ]}
              height={260}
            />
          </div>
        </Card>
      </div>
    </div>
  );
}

