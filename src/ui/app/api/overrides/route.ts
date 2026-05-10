import { NextResponse } from "next/server";

import { OverrideRequestSchema } from "@/types/domain";

export async function POST(request: Request) {
  const body = OverrideRequestSchema.parse(await request.json());
  return NextResponse.json(body);
}

