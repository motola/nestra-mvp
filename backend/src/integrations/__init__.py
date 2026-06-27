"""Vendor integrations — plugins that implement the SPIRE adapter contract.

Each vendor (govee, lifx, shelly_local, matter) is a self-contained adapter that
returns ``SpireDevice`` resources and accepts canonical commands. The contract
itself — ``VendorAdapter`` — lives in the standard, at ``spire.adapter``.
"""
