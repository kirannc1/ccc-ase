import { useMutation } from "@tanstack/react-query";

import { api } from "@/services/api";
import { DecisionRequest } from "@/types/domain";

export function useDecisioning() {
  return useMutation({
    mutationFn: (request: DecisionRequest) => api.resolveDecision(request)
  });
}

