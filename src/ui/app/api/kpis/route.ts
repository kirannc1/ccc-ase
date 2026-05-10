import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    kpis: [
      { id: "kpi-1", label: "SLA Breach Risk", value: 0.22, trend: -0.03, unit: "%" },
      { id: "kpi-2", label: "Attrition Risk", value: 0.34, trend: 0.05, unit: "%" },
      { id: "kpi-3", label: "Cost Drift", value: 0.18, trend: 0.02, unit: "%" },
      { id: "kpi-4", label: "Decision Confidence", value: 0.76, trend: 0.01 }
    ]
  });
}

