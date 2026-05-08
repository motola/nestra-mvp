"use client";

import { useQuery } from "@tanstack/react-query";
import { propertiesApi } from "@/lib/api";
import type { Property } from "@/lib/types";

export function useProperties() {
  return useQuery<Property[]>({
    queryKey: ["properties"],
    queryFn: propertiesApi.list,
  });
}

export function useProperty(id: string) {
  return useQuery<Property>({
    queryKey: ["property", id],
    queryFn: () => propertiesApi.get(id),
    enabled: Boolean(id),
  });
}
