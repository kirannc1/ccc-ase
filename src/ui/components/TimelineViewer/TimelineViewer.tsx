"use client";

import { Caption1, Card, CardHeader, Text } from "@fluentui/react-components";

import { AuditEvent } from "@/types/domain";

export function TimelineViewer({ events }: { events: AuditEvent[] }) {
  return (
    <div style={{ display: "grid", gap: 8 }}>
      {events.map((event) => (
        <Card key={event.event_id}>
          <CardHeader header={<Text weight="semibold">{event.event_type}</Text>} description={<Caption1>{event.created_at}</Caption1>} />
        </Card>
      ))}
    </div>
  );
}

