"use client";

import { Field, Input } from "@fluentui/react-components";

export function FilterPanel({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <Field label={label}>
      <Input value={value} onChange={(_, data) => onChange(data.value)} />
    </Field>
  );
}

