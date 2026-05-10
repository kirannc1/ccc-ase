import { useMutation } from "@tanstack/react-query";

import { api } from "@/services/api";
import { OptimizationRequest } from "@/types/domain";

export function useOptimization() {
  return useMutation({
    mutationFn: (request: OptimizationRequest) => api.rankOptimization(request)
  });
}

