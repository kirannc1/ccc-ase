"use client";

import { Button, Card, CardHeader, Caption1, Text, Title2 } from "@fluentui/react-components";
import Link from "next/link";
import { useMemo } from "react";

import { ChartWrapper } from "@/components/ChartWrapper/ChartWrapper";
import { GraphViewer } from "@/components/GraphViewer/GraphViewer";
import { useKpis } from "@/hooks/useKpis";
import { useScenarioSimulation } from "@/hooks/useScenarioSimulation";

export function LeadershipDashboardScreen() {
  const kpis = useKpis();
  const simulate = useScenarioSimulation();

  const chartOption = useMemo(() => {
    const scenarios = simulate.data?.scenarios ?? [];
    return {
      tooltip: { trigger: "axis" },
      xAxis: { type: "category", data: scenarios.map((s) => s.name) },
      yAxis: { type: "value", min: 0, max: 1 },
      series: [{ type: "bar", data: scenarios.map((s) => s.score) }]
    };
  }, [simulate.data]);

  return (
    <div style={{ display: "grid", gap: 16, width: "100%" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <Title2>Leadership Dashboard</Title2>
        <div style={{ display: "flex", gap: 8 }}>
          <Link href="/scenario-lab">
            <Button appearance="secondary">Open Scenario Lab</Button>
          </Link>
          <Button
            appearance="primary"
            onClick={() =>
              simulate.mutate({
                tenant_id: "tenant-a",
                features: { engagement: 8, absenteeism: 2 },
                graph_signals: ["skill_fragility"],
                constraints: { cost: 1 }
              })
            }
            disabled={simulate.isPending}
          >
            Run Sample
          </Button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: 12 }}>
        {(kpis.data?.kpis ?? []).map((kpi) => (
          <Card key={kpi.id}>
            <CardHeader header={<Text weight="semibold">{kpi.label}</Text>} description={<Caption1>Trend {kpi.trend >= 0 ? "+" : ""}{kpi.trend}</Caption1>} />
            <div style={{ padding: "0 16px 16px" }}>
              <Text size={600}>{kpi.value}{kpi.unit ?? ""}</Text>
            </div>
          </Card>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 12 }}>
        <Card>
          <CardHeader header={<Text weight="semibold">Scenario Comparison</Text>} description={<Caption1>Simulated outputs</Caption1>} />
          <div style={{ padding: 16 }}>
            <ChartWrapper option={chartOption} height={260} />
          </div>
        </Card>
        <Card>
          <CardHeader header={<Text weight="semibold">Dependency Graph</Text>} description={<Caption1>Drivers → outcomes</Caption1>} />
          <div style={{ padding: 16 }}>
            <GraphViewer
              nodes={[
                { id: "skill", label: "Skill Fragility", status: "risk" },
                { id: "sla", label: "SLA Breach", status: "default" },
                { id: "rev", label: "Revenue/Penalty", status: "default" }
              ]}
              edges={[
                { id: "e1", source: "skill", target: "sla", label: "increases" },
                { id: "e2", source: "sla", target: "rev", label: "exposure" }
              ]}
              height={260}
            />
          </div>
        </Card>
      </div>
    </div>
  );
}

