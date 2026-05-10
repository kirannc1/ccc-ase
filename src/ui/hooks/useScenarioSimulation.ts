import { useMutation } from "@tanstack/react-query";

import { api } from "@/services/api";
import { ScenarioSimulationRequest } from "@/types/domain";

export function useScenarioSimulation() {
  return useMutation({
    mutationFn: (request: ScenarioSimulationRequest) => api.simulateScenario(request)
  });
}

