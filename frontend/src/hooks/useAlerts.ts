"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { alertsApi } from "@/lib/api";
import type { Alert } from "@/lib/types";

export function useAlerts() {
  return useQuery<Alert[]>({
    queryKey: ["alerts"],
    queryFn: alertsApi.list,
    refetchInterval: 60_000,
  });
}

export function useDismissAlert() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (alertId: string) => alertsApi.dismiss(alertId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts"] }),
  });
}
