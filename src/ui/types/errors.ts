export type ApiErrorShape = {
  code: string;
  message: string;
  correlation_id?: string;
};

export class ApiError extends Error {
  public readonly status: number;
  public readonly code: string;
  public readonly correlationId?: string;

  constructor(args: { status: number; code: string; message: string; correlationId?: string }) {
    super(args.message);
    this.name = "ApiError";
    this.status = args.status;
    this.code = args.code;
    this.correlationId = args.correlationId;
  }
}

