import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { AuditReplayScreen } from "@/features/audit/AuditReplayScreen";
import { renderWithProviders } from "@/test/render";

test("replays audit and renders timeline", async () => {
  const user = userEvent.setup();
  renderWithProviders(<AuditReplayScreen />);
  await user.click(screen.getByRole("button", { name: "Replay" }));
  expect(await screen.findByText("decision.created")).toBeInTheDocument();
});

