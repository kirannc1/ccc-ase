import { z } from "zod";

import { ApiError } from "@/types/errors";

type FetcherOptions = {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
  headers?: Record<string, string>;
  signal?: AbortSignal;
};

const ErrorEnvelopeSchema = z.object({
  error: z
    .object({
      code: z.string(),
      message: z.string(),
      correlation_id: z.string().optional()
    })
    .optional(),
  detail: z.string().optional()
});

export async function fetchJson<TSchema extends z.ZodTypeAny>(
  path: string,
  schema: TSchema,
  options: FetcherOptions = {}
): Promise<z.output<TSchema>> {
  const response = await fetch(path, {
    method: options.method ?? "GET",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {})
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
    signal: options.signal
  });

  const contentType = response.headers.get("content-type") ?? "";
  const raw = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    const envelope = ErrorEnvelopeSchema.safeParse(raw);
    const message = envelope.success
      ? envelope.data.error?.message ?? envelope.data.detail ?? response.statusText
      : response.statusText;
    const code = envelope.success ? envelope.data.error?.code ?? "HTTP_ERROR" : "HTTP_ERROR";
    const correlationId = envelope.success ? envelope.data.error?.correlation_id : undefined;
    throw new ApiError({ status: response.status, code, message, correlationId });
  }

  const parsed = schema.safeParse(raw);
  if (!parsed.success) {
    throw new ApiError({ status: 500, code: "SCHEMA_MISMATCH", message: "Invalid response shape" });
  }
  return parsed.data;
}

