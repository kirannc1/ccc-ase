import { NextResponse } from "next/server";

import { ReplayRequestSchema } from "@/types/domain";
import { stableId } from "@/utils/hash";

export async function POST(request: Request) {
  const body = ReplayRequestSchema.parse(await request.json());
  const correlation = body.correlation_id ?? stableId("corr", body.tenant_id);
  const now = new Date().toISOString();
  return NextResponse.json({
    tenant_id: body.tenant_id,
    events: [
      { event_id: stableId("evt", `${correlation}:1`), tenant_id: body.tenant_id, correlation_id: correlation, event_type: "scenario.completed", resource_id: "scenario", payload: {}, created_at: now },
      { event_id: stableId("evt", `${correlation}:2`), tenant_id: body.tenant_id, correlation_id: correlation, event_type: "optimization.completed", resource_id: "optimization", payload: {}, created_at: now },
      { event_id: stableId("evt", `${correlation}:3`), tenant_id: body.tenant_id, correlation_id: correlation, event_type: "decision.created", resource_id: "decision", payload: {}, created_at: now }
    ]
  });
}

