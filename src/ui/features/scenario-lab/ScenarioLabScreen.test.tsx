import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ScenarioLabScreen } from "@/features/scenario-lab/ScenarioLabScreen";
import { renderWithProviders } from "@/test/render";

jest.mock("@/components/ChartWrapper/ChartWrapper", () => ({
  ChartWrapper: () => <div data-testid="chart" />
}));
jest.mock("@/components/GraphViewer/GraphViewer", () => ({
  GraphViewer: () => <div data-testid="graph" />
}));

test("runs simulation and enables ranking", async () => {
  const user = userEvent.setup();
  renderWithProviders(<ScenarioLabScreen />);
  await user.click(screen.getByRole("button", { name: "Run Simulation" }));
  expect(screen.getByRole("button", { name: "Rank Options" })).toBeEnabled();
});

