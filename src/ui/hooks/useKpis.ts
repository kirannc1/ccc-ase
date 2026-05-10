import { useQuery } from "@tanstack/react-query";

import { api } from "@/services/api";

export function useKpis() {
  return useQuery({
    queryKey: ["kpis"],
    queryFn: () => api.getKpis(),
    staleTime: 10_000
  });
}

