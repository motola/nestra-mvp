# Integrations

Each vendor is a self-contained adapter that maps the vendor's devices into the
SPIRE model. Adding a vendor touches exactly two things: a folder here and one
line in `registry.py`.

## Structure

```
integrations/
├── registry.py        # single source of truth — every vendor is one VendorSpec
├── factory.py         # stamps adapter output into SpireDevice rows
├── sync.py            # DeviceSyncService — the fetch -> upsert orchestrator
├── scanner.py         # cross-vendor local-network discovery
└── <vendor>/
    └── adapter.py     # implements spire.VendorAdapter (list / read / control)
```

The convention is uniform: **the adapter always lives in `adapter.py`.** A vendor
that speaks a raw *local* protocol — rather than a simple cloud HTTP API — keeps
that transport in its own module alongside the adapter. That is the same rule
everywhere, not a per-vendor exception:

| Vendor | Extra modules | Why |
|---|---|---|
| `shelly` | `client.py`, `provisioning.py` | local RPC + Wi-Fi provisioning |
| `matter` | `server.py` | python-matter-server WebSocket client |

Cloud vendors make plain HTTP calls inline, so they need only `adapter.py`.

## Adding a vendor

1. Create `integrations/<vendor>/adapter.py` with a `class <Vendor>Adapter(VendorAdapter)`
   implementing `list_devices`, `get_device_state`, and `send_command`, mapping
   each device via `SpireDevice.from_vendor(...)`.
2. Add the vendor's credential field to `config.py`.
3. Add one `VendorSpec` line to `registry.py`.

## Current vendors

Govee, LIFX, Shelly, Matter, Philips Hue, SmartThings, Tuya, SwitchBot, ecobee,
tado, TP-Link Kasa, August, Aqara, eWeLink.

> The cloud adapters beyond Govee / LIFX / Shelly / Matter are scaffolds written
> from public API docs and are marked `# UNTESTED` — verify each against a real
> account or device before relying on it in production.
