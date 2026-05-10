"use client";

import { Button, Card, CardHeader, Field, Input, Switch, Text, Title2 } from "@fluentui/react-components";
import { useState } from "react";

export function AdminGovernanceScreen() {
  const [policyEnabled, setPolicyEnabled] = useState(true);
  const [role, setRole] = useState("manager");
  const [healthChecked, setHealthChecked] = useState(false);

  return (
    <div style={{ display: "grid", gap: 16, width: "100%" }}>
      <Title2>Admin & Governance</Title2>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <Card>
          <CardHeader header={<Text weight="semibold">Policy Configuration</Text>} />
          <div style={{ padding: 16, display: "grid", gap: 12 }}>
            <Switch checked={policyEnabled} onChange={(_, data) => setPolicyEnabled(Boolean(data.checked))} label="Enable policy checks" />
            <Field label="Default role">
              <Input value={role} onChange={(_, data) => setRole(data.value)} />
            </Field>
          </div>
        </Card>
        <Card>
          <CardHeader header={<Text weight="semibold">System Health</Text>} description={<Text>{healthChecked ? "checked" : "not checked"}</Text>} />
          <div style={{ padding: 16, display: "grid", gap: 12 }}>
            <Button appearance="secondary" onClick={() => setHealthChecked(true)}>
              Check Health
            </Button>
            <Text>Services: UI mock mode</Text>
          </div>
        </Card>
      </div>
      <Card>
        <CardHeader header={<Text weight="semibold">Roles & Access</Text>} description={<Text>PoC view</Text>} />
        <div style={{ padding: 16 }}>
          <Text>Role-based approvals and overrides are enforced server-side; this screen is a PoC admin surface.</Text>
        </div>
      </Card>
    </div>
  );
}

