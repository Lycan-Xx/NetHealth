"""Network fingerprinting implementation."""
import json
import logging
import socket
from typing import Dict, List, Optional

import psutil
import requests
from requests.exceptions import RequestException
from stem import Signal
from stem.control import Controller

from nethealth.domain.interfaces import (
    NetworkFingerprint,
    NetworkInterface,
    NetworkFingerprintDetector,
    NetworkError,
    ServiceUnavailableError
)

logger = logging.getLogger(__name__)


class NetworkFingerprintError(NetworkError):
    """Base exception for network fingerprinting errors."""
    pass


class IPAPIFingerprintDetector(NetworkFingerprintDetector):
    """Network fingerprinting implementation using ip-api.com."""
    
    def __init__(self):
        self.api_url = "http://ip-api.com/json"
        self.tor_check_url = "https://check.torproject.org/api/ip"
    
    def get_fingerprint(self) -> NetworkFingerprint:
        """
        Get network fingerprint information.
        
        Raises:
            NetworkFingerprintError: When fingerprinting fails
            ServiceUnavailableError: When external services are unavailable
        """
        try:
            # Check internet connectivity first
            self._check_connectivity()
            
            # Get IP and location info
            try:
                response = requests.get(self.api_url, timeout=10)
                response.raise_for_status()
                data = response.json()
            except RequestException as e:
                logger.error(f"IP API request failed: {str(e)}")
                raise ServiceUnavailableError("IP geolocation service is unavailable") from e
            except json.JSONDecodeError as e:
                logger.error(f"Invalid IP API response: {str(e)}")
                raise NetworkFingerprintError("Invalid response from IP service") from e
            
            # Check Tor status
            is_tor = self._check_tor_status()
            
            # Get network interfaces
            try:
                interfaces = self._get_network_interfaces()
            except Exception as e:
                logger.error(f"Failed to get network interfaces: {str(e)}")
                interfaces = []  # Graceful degradation
            
            return NetworkFingerprint(
                public_ip=data.get("query", "unknown"),
                isp=data.get("isp", "unknown"),
                country=data.get("country", "unknown"),
                city=data.get("city", "unknown"),
                is_vpn=self._detect_vpn(data),
                is_proxy=data.get("proxy", False),
                is_tor=is_tor,
                interfaces=interfaces
            )
        except Exception as e:
            logger.error(f"Unexpected error during fingerprinting: {str(e)}")
            raise NetworkFingerprintError(f"Failed to get network information: {str(e)}") from e
    
    def _check_connectivity(self) -> None:
        """Check basic internet connectivity."""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
        except OSError as e:
            logger.error("No internet connection available")
            raise NetworkError("No internet connection available") from e
    
    def _check_tor_status(self) -> bool:
        """Check Tor status with graceful degradation."""
        try:
            response = requests.get(self.tor_check_url, timeout=5)
            return response.json().get("IsTor", False)
        except Exception as e:
            logger.warning(f"Tor status check failed: {str(e)}")
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
        
        try:
            for interface, addrs in psutil.net_if_addrs().items():
                try:
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
                except Exception as e:
                    logger.warning(f"Failed to process interface {interface}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to enumerate network interfaces: {str(e)}")
            
        return interfaces