/**Bluetooth integration types and interfaces. */

export interface BluetoothDeviceOut {
  id: string;
  property_id: string;
  mac_address: string;
  name: string;
  device_type: string;
  rssi: number;
  battery_level: number | null;
  is_paired: boolean;
  last_sync: string;
  created_at: string;
}

export interface BluetoothDeviceIn {
  mac_address: string;
  name: string;
  property_id: string;
  device_type?: string;
  rssi?: number;
  battery_level?: number | null;
}

export interface BluetoothPairResponse {
  device_id: string;
  status: string;
  message: string;
}

export interface BluetoothUnpairResponse {
  status: string;
  message: string;
}

export interface ScannedDevice {
  name: string;
  mac_address: string;
}
