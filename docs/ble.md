# Govee H617C Bluetooth LE Integration

A record of how the BLE control layer works and the debugging steps that got it working.

---

## How Govee BLE works

The Govee H617C is a Bluetooth Low Energy (BLE) device. Unlike Wi-Fi devices, it does not connect to the internet — it only accepts commands from a device that is physically nearby via BLE radio.

Govee does not publish an official BLE protocol spec. The packet format used here was reverse-engineered by the open-source community and confirmed working against the physical device during development.

---

## Discovering the correct characteristic

BLE devices expose **services** (groups of functionality) and **characteristics** (individual read/write endpoints). You have to inspect the device to find which characteristic accepts control commands.

We connected to the H617C and enumerated all services and characteristics:

```
Service: 00010203-0405-0607-0809-0a0b0c0d1910
  Char: 00010203-0405-0607-0809-0a0b0c0d2b10  props=[read, notify]
  Char: 00010203-0405-0607-0809-0a0b0c0d2b11  props=[write, read, write-without-response, notify]

Service: 02f00000-0000-0000-0000-00000000fe00
  Char: 02f00000-0000-0000-0000-00000000ff01  props=[write, write-without-response]
  ...
```

The characteristic `00010203-0405-0607-0809-0a0b0c0d2b11` in the first service has `write` in its properties. That is the control channel. An earlier attempt used `...0a0b0c0d1911` (from an outdated community source) which silently accepted writes but produced no effect. Reading the actual device returned the correct UUID ending in `2b11`.

---

## Packet format

All commands are exactly 20 bytes:

```
[0x33, CMD, DATA..., PADDING..., XOR_CHECKSUM]
```

| Position | Value | Meaning |
|---|---|---|
| 0 | `0x33` | Header — fixed for all Govee commands |
| 1 | `0x01` | Command type — `0x01` = power |
| 2 | `0x01` or `0x00` | Value — `0x01` = on, `0x00` = off |
| 3–18 | `0x00` | Padding |
| 19 | XOR | Checksum — XOR of bytes 0–18 |

Power ON:  `33 01 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 33`
Power OFF: `33 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 32`

The Python implementation in `backend/src/demo/govee_ble.py`:

```python
def _packet(cmd: int, data: list[int]) -> bytes:
    payload = [0x33, cmd] + data
    payload += [0x00] * (19 - len(payload))
    xor = 0
    for b in payload:
        xor ^= b
    payload.append(xor)
    return bytes(payload)
```

---

## The CoreBluetooth conflict

The first working test ran BLE commands directly from a Python script (`asyncio.run()`). When the same code ran inside the FastAPI/uvicorn server, writes completed without error but the light did not respond.

**Root cause:** On macOS, BLE is managed by CoreBluetooth, which runs on its own dispatch queue. When `BleakScanner.discover()` ran inside the uvicorn event loop to scan for devices, it left the CoreBluetooth central manager in a state that blocked subsequent `BleakClient` connections in the same process from being processed by the device.

**Fix:** Hardcode the device's BLE address in `.env` as `GOVEE_BLE_ADDRESS`. When this is set, `list_devices()` skips the scan entirely and returns the device directly. No scanner ever runs inside the server process, so no conflict occurs.

```python
async def list_devices() -> list[dict[str, object]]:
    address = get_settings().govee_ble_address
    if address:
        return [{
            "device": address,
            "deviceName": "Govee H617C",
            "model": "ble",
            ...
        }]
    # Falls back to BleakScanner.discover() only if address not configured
```

The BLE address for the H617C was found by running a standalone scan:

```bash
PYTHONPATH=src python -c "
import asyncio
from bleak import BleakScanner
async def scan():
    found = await BleakScanner.discover(timeout=8.0)
    for d in found:
        print(d.name, d.address)
asyncio.run(scan())
"
```

Output included: `Govee_H617C_475E  BF7E3E31-201B-A69C-98C4-AF0D517937BF`

That address is now set in `backend/.env` as `GOVEE_BLE_ADDRESS`.

---

## Architecture summary

```
Browser (localhost:3000)
  → POST /demo/devices/govee/{address}/power?model=ble
  → FastAPI route (routes.py)
  → govee_ble.set_power(address, on=True/False)
  → BleakClient connects to H617C via BLE
  → Writes 20-byte packet to characteristic 00010203-...-2b11
  → Light responds
```

The `model=ble` query parameter acts as a routing sentinel. The frontend sends it automatically because `DemoDevice.model` is set to `"ble"` for BLE-sourced devices. The same power endpoint handles both REST Govee devices (any other model string) and BLE devices.

---

## Known limitations

- **Local only.** BLE requires physical proximity. This integration cannot work when the backend is deployed to a remote server (Fly.io). It is suitable for investor demos only.
- **Single device.** The current implementation is hardcoded to one address. Multiple BLE devices would require a proper scan-and-register flow.
- **No live state.** BLE doesn't return the current power state. The UI reflects the last toggle sent from this session, not the actual hardware state.
- **macOS only tested.** The CoreBluetooth backend is macOS-specific. Linux uses BlueZ and may behave differently.
