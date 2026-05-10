import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { RecommendationDetailScreen } from "@/features/recommendation/RecommendationDetailScreen";
import { renderWithProviders } from "@/test/render";

jest.mock("@/components/ChartWrapper/ChartWrapper", () => ({
  ChartWrapper: () => <div data-testid="chart" />
}));

test("generates decision artifact and explanation", async () => {
  const user = userEvent.setup();
  renderWithProviders(<RecommendationDetailScreen />);
  await user.click(screen.getByRole("button", { name: "Run Decision Flow" }));
  expect(await screen.findByText(/best optimized scenario selected/i)).toBeInTheDocument();
});

