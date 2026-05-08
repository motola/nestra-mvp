"use client";

import { useQuery } from "@tanstack/react-query";
import { integrationsApi } from "@/lib/api";
import type { VendorIntegration } from "@/lib/types";

export function useIntegrations() {
  return useQuery<VendorIntegration[]>({
    queryKey: ["integrations"],
    queryFn: integrationsApi.list,
  });
}
