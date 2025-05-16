"""Network fingerprinting implementation."""
import json
import socket
from typing import Dict, List, Optional

import psutil
import requests
from requests.exceptions import RequestException
from stem import Signal
from stem.control import Controller

from nethealth.domain.interfaces import NetworkFingerprint, NetworkInterface, NetworkFingerprintDetector


class NetworkFingerprintError(Exception):
    """Base exception for network fingerprinting errors."""
    pass


class IPAPIFingerprintDetector(NetworkFingerprintDetector):
    """Network fingerprinting implementation using ip-api.com."""
    
    def __init__(self):
        self.api_url = "http://ip-api.com/json"
        self.tor_check_url = "https://check.torproject.org/api/ip"
    
    def get_fingerprint(self) -> NetworkFingerprint:
        try:
            # Get IP and location info
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check Tor status
            is_tor = self._check_tor_status()
            
            # Get network interfaces
            interfaces = self._get_network_interfaces()
            
            return NetworkFingerprint(
                public_ip=data["query"],
                isp=data["isp"],
                country=data["country"],
                city=data["city"],
                is_vpn=self._detect_vpn(data),
                is_proxy=data.get("proxy", False),
                is_tor=is_tor,
                interfaces=interfaces
            )
        except RequestException as e:
            raise NetworkFingerprintError(f"Failed to get network information: {str(e)}")
        except (KeyError, json.JSONDecodeError) as e:
            raise NetworkFingerprintError(f"Invalid response format: {str(e)}")
    
    def _check_tor_status(self) -> bool:
        try:
            response = requests.get(self.tor_check_url, timeout=10)
            return response.json().get("IsTor", False)
        except (RequestException, json.JSONDecodeError):
            return False
    
    def _detect_vpn(self, ip_data: Dict) -> bool:
        """Detect VPN usage based on IP data."""
        vpn_indicators = [
            ip_data.get("proxy", False),
            ip_data.get("hosting", False),
            ip_data.get("mobile", False) and ip_data.get("proxy", False),
            "vpn" in ip_data.get("isp", "").lower(),
        ]
        return any(vpn_indicators)
    
    def _get_network_interfaces(self) -> List[NetworkInterface]:
        """Get information about network interfaces."""
        interfaces = []
        
        for interface, addrs in psutil.net_if_addrs().items():
            ip_addr = ""
            mac_addr = ""
            
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip_addr = addr.address
                elif addr.family == psutil.AF_LINK:
                    mac_addr = addr.address
            
            if ip_addr and mac_addr:
                is_active = interface in psutil.net_if_stats() and \
                           psutil.net_if_stats()[interface].isup
                
                interfaces.append(NetworkInterface(
                    name=interface,
                    ip_address=ip_addr,
                    mac_address=mac_addr,
                    is_active=is_active
                ))
        
        return interfaces