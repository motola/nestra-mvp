"use client";

import { useQuery } from "@tanstack/react-query";
import { devicesApi } from "@/lib/api";
import type { AlphaconDevice } from "@/lib/types";

export function useDevices() {
  return useQuery<AlphaconDevice[]>({
    queryKey: ["devices"],
    queryFn: devicesApi.list,
    refetchInterval: 30_000,
  });
}

export function useDevice(id: string) {
  return useQuery<AlphaconDevice>({
    queryKey: ["device", id],
    queryFn: () => devicesApi.get(id),
    refetchInterval: 30_000,
    enabled: Boolean(id),
  });
}
