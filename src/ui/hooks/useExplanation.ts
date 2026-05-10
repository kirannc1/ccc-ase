import { useMutation } from "@tanstack/react-query";

import { api } from "@/services/api";
import { ExplanationRequest } from "@/types/domain";

export function useExplanation() {
  return useMutation({
    mutationFn: (request: ExplanationRequest) => api.generateExplanation(request)
  });
}

