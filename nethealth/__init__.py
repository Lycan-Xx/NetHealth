"""NetHealth - Network Analysis Tool."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from nethealth.domain.interfaces import (
    NetworkReport,
    NetworkSpeed,
    NetworkFingerprint,
    NetworkInterface,
    VPNStatus,
)

__all__ = [
    "NetworkReport",
    "NetworkSpeed",
    "NetworkFingerprint",
    "NetworkInterface",
    "VPNStatus",
]