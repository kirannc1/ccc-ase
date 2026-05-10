import { useMutation } from "@tanstack/react-query";

import { api } from "@/services/api";
import { ReplayRequest } from "@/types/domain";

export function useAuditReplay() {
  return useMutation({
    mutationFn: (request: ReplayRequest) => api.replayAudit(request)
  });
}

