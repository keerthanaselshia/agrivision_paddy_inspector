"""
core/location.py  –  Location helper (manual entry now, GPS later).

The function get_location() returns whatever location is available.
On the laptop it always returns None for lat/lon because there is no GPS.

When the Raspberry Pi 4 gains a NEO-6M GPS module (serial or gpsd), replace
the body of _read_gps() with the real implementation.  The rest of the UI
code does not need to change.

Design rule: this module must NEVER print, log or store GPS coordinates
without the user seeing them first.
"""

from __future__ import annotations


def get_location(manual_text: str = "Erode, Tamil Nadu") -> dict:
    """Return a location dict.

    Parameters
    ----------
    manual_text : str
        The location string typed by the user in the sidebar.

    Returns
    -------
    dict with keys:
        text      : str   – human-readable location
        latitude  : float | None
        longitude : float | None
        source    : str   – 'manual' | 'gps'
    """
    lat, lon = _read_gps()
    return {
        "text": manual_text,
        "latitude": lat,
        "longitude": lon,
        "source": "gps" if lat is not None else "manual",
    }


def _read_gps() -> tuple[float | None, float | None]:
    """Read GPS coordinates from the hardware module.

    Currently returns (None, None) because GPS is not yet fitted.
    Replace this function body when the NEO-6M is connected.

    Example skeleton for gpsd:
        import gpsd
        gpsd.connect()
        p = gpsd.get_current()
        return p.lat, p.lon
    """
    return None, None
