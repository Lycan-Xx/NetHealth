"""Domain interfaces for NetHealth core functionality."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Protocol


@dataclass
class NetworkSpeed:
    download_mbps: float
    upload_mbps: float
    ping_ms: float


@dataclass
class NetworkInterface:
    name: str
    ip_address: str
    is_active: bool
    mac_address: str


@dataclass
class VPNStatus:
    is_active: bool
    provider: Optional[str]
    server_location: Optional[str]


@dataclass
class NetworkFingerprint:
    public_ip: str
    isp: str
    country: str
    city: str
    is_vpn: bool
    is_proxy: bool
    is_tor: bool
    interfaces: List[NetworkInterface]


@dataclass
class NetworkReport:
    """Container for all network analysis results."""
    timestamp: datetime
    speed: NetworkSpeed
    fingerprint: NetworkFingerprint
    vpn_status: VPNStatus


class Reporter(Protocol):
    """Interface for result reporting implementations."""
    
    def report(self, data: NetworkReport) -> None:
        """Report network analysis results."""
        pass


class HistoryManager(Protocol):
    """Interface for managing test result history."""
    
    def save(self, report: NetworkReport) -> None:
        """Save a report to history."""
        pass
    
    def get_all(self) -> List[NetworkReport]:
        """Retrieve all historical reports."""
        pass
    
    def get_latest(self, n: int = 1) -> List[NetworkReport]:
        """Retrieve the n most recent reports."""
        pass