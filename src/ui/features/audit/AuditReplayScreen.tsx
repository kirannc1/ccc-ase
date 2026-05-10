"use client";

import { Button, Card, CardHeader, Field, Input, Text, Title2 } from "@fluentui/react-components";
import { useState } from "react";

import { FilterPanel } from "@/components/FilterPanel/FilterPanel";
import { TimelineViewer } from "@/components/TimelineViewer/TimelineViewer";
import { useAuditReplay } from "@/hooks/useAuditReplay";

export function AuditReplayScreen() {
  const replay = useAuditReplay();
  const [tenantId, setTenantId] = useState("tenant-a");
  const [correlationId, setCorrelationId] = useState("");
  const [filter, setFilter] = useState("");

  const events = (replay.data?.events ?? []).filter((evt) => (filter ? evt.event_type.toLowerCase().includes(filter.toLowerCase()) : true));

  return (
    <div style={{ display: "grid", gap: 16, width: "100%" }}>
      <Title2>Audit & Replay</Title2>
      <Card>
        <CardHeader header={<Text weight="semibold">Replay</Text>} />
        <div style={{ padding: 16, display: "grid", gridTemplateColumns: "1fr 1fr 200px", gap: 12, alignItems: "end" }}>
          <Field label="Tenant">
            <Input value={tenantId} onChange={(_, data) => setTenantId(data.value)} />
          </Field>
          <Field label="Correlation ID (optional)">
            <Input value={correlationId} onChange={(_, data) => setCorrelationId(data.value)} />
          </Field>
          <Button
            appearance="primary"
            onClick={() => replay.mutate({ tenant_id: tenantId, correlation_id: correlationId || null, resource_id: null })}
            disabled={replay.isPending}
          >
            Replay
          </Button>
        </div>
      </Card>

      <Card>
        <CardHeader header={<Text weight="semibold">Timeline</Text>} description={<Text>{events.length} events</Text>} />
        <div style={{ padding: 16, display: "grid", gap: 12 }}>
          <FilterPanel label="Filter by event type" value={filter} onChange={setFilter} />
          <TimelineViewer events={events} />
        </div>
      </Card>
    </div>
  );
}

