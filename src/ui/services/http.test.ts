import { http, HttpResponse } from "msw";

import { fetchJson } from "@/services/http";
import { server } from "@/test/server";
import { z } from "zod";

test("throws ApiError on non-200", async () => {
  server.use(http.get("/api/fail", () => HttpResponse.json({ detail: "boom" }, { status: 500 })));
  await expect(fetchJson("/api/fail", z.object({ ok: z.boolean() }))).rejects.toMatchObject({ name: "ApiError", status: 500 });
});

test("throws ApiError on schema mismatch", async () => {
  server.use(http.get("/api/bad", () => HttpResponse.json({ nope: true })));
  await expect(fetchJson("/api/bad", z.object({ ok: z.boolean() }))).rejects.toMatchObject({ code: "SCHEMA_MISMATCH" });
});

