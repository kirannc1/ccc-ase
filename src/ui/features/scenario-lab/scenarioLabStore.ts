import { create } from "zustand";

type ScenarioLabState = {
  tenantId: string;
  leaveDays: number;
  coverage: number;
  approvalRisk: number;
  setTenantId: (tenantId: string) => void;
  setLeaveDays: (leaveDays: number) => void;
  setCoverage: (coverage: number) => void;
  setApprovalRisk: (approvalRisk: number) => void;
};

export const useScenarioLabStore = create<ScenarioLabState>((set) => ({
  tenantId: "tenant-a",
  leaveDays: 2,
  coverage: 0.8,
  approvalRisk: 0.2,
  setTenantId: (tenantId) => set({ tenantId }),
  setLeaveDays: (leaveDays) => set({ leaveDays }),
  setCoverage: (coverage) => set({ coverage }),
  setApprovalRisk: (approvalRisk) => set({ approvalRisk })
}));

