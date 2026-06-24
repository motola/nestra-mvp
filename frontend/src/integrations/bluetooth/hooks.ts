/**React hooks for Bluetooth device management. */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import {
  BluetoothDeviceIn,
  BluetoothDeviceOut,
  BluetoothPairResponse,
  BluetoothUnpairResponse,
} from "./types";

export function useBluetoothDevices(propertyId?: string) {
  return useQuery({
    queryKey: ["bluetooth-devices", propertyId],
    queryFn: async () => {
      const url = propertyId
        ? `/integrations/bluetooth/devices?property_id=${propertyId}`
        : "/integrations/bluetooth/devices";
      return apiFetch<BluetoothDeviceOut[]>(url);
    },
  });
}

export function usePairBluetoothDevice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (device: BluetoothDeviceIn) => {
      return apiFetch<BluetoothPairResponse>("/integrations/bluetooth/pair", {
        method: "POST",
        body: JSON.stringify(device),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bluetooth-devices"] });
    },
  });
}

export function useUnpairBluetoothDevice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (deviceId: string) => {
      return apiFetch<BluetoothUnpairResponse>(
        `/integrations/bluetooth/unpair?device_id=${deviceId}`,
        {
          method: "POST",
        },
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bluetooth-devices"] });
    },
  });
}
