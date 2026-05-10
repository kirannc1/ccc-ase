import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { LeadershipDashboardScreen } from "@/features/leadership-dashboard/LeadershipDashboardScreen";
import { renderWithProviders } from "@/test/render";

jest.mock("@/components/ChartWrapper/ChartWrapper", () => ({
  ChartWrapper: () => <div data-testid="chart" />
}));
jest.mock("@/components/GraphViewer/GraphViewer", () => ({
  GraphViewer: () => <div data-testid="graph" />
}));

test("renders KPI tiles", async () => {
  renderWithProviders(<LeadershipDashboardScreen />);
  await waitFor(() => expect(screen.getByText("SLA Breach Risk")).toBeInTheDocument());
  expect(screen.getByText("Attrition Risk")).toBeInTheDocument();
});

test("runs sample simulation", async () => {
  const user = userEvent.setup();
  renderWithProviders(<LeadershipDashboardScreen />);
  await user.click(screen.getByRole("button", { name: "Run Sample" }));
  expect(await screen.findByTestId("chart")).toBeInTheDocument();
});

