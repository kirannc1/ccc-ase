import "@testing-library/jest-dom";

import { server } from "@/test/server";

jest.mock("next/link", () => {
  const React = require("react");
  return {
    __esModule: true,
    default: ({ href, children }: { href: string; children: unknown }) => React.createElement("a", { href }, children)
  };
});

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
