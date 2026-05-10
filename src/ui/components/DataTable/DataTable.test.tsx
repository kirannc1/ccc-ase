import { screen } from "@testing-library/react";

import { DataTable, Column } from "@/components/DataTable/DataTable";
import { renderWithProviders } from "@/test/render";

type Row = { id: string; name: string };

test("renders headers and rows", () => {
  const columns: Column<Row>[] = [
    { key: "name", header: "Name", render: (row) => row.name }
  ];
  renderWithProviders(<DataTable columns={columns} rows={[{ id: "1", name: "Alice" }]} />);
  expect(screen.getByText("Name")).toBeInTheDocument();
  expect(screen.getByText("Alice")).toBeInTheDocument();
});

