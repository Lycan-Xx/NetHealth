"""VPN detection implementation."""
import logging
import socket
from typing import Optional, List

import requests

from nethealth.domain.interfaces import VPNStatus, NetworkError

logger = logging.getLogger(__name__)

class VPNDetectionError(NetworkError):
    """Base exception for VPN detection errors."""
    pass

class VPNDetector:
    """VPN detection implementation."""
    
    def __init__(self):
        self.vpn_port_list = [1194, 1197, 1723, 500]  # Common VPN ports
        self.vpn_providers = {
            "nordvpn": ["nordvpn.com"],
            "expressvpn": ["expressvpn.com"],
            "protonvpn": ["protonvpn.com"],
        }
    
    def check_status(self) -> VPNStatus:
        """
        Check VPN connection status.
        
        Returns:
            VPNStatus object with connection details
        """
        try:
            is_active = self._detect_vpn_connection()
            provider = self._identify_provider() if is_active else None
            location = self._get_server_location() if is_active else None
            
            return VPNStatus(
                is_active=is_active,
                provider=provider,
                server_location=location
            )
            
        except Exception as e:
            logger.error(f"VPN detection failed: {str(e)}")
            raise VPNDetectionError(f"Failed to detect VPN status: {str(e)}") from e
    
    def _detect_vpn_connection(self) -> bool:
        """Check for active VPN connections."""
        # Check common VPN ports
        for port in self.vpn_port_list:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                
                if result == 0:
                    return True
            except:
                continue
        
        return False
    
    def _identify_provider(self) -> Optional[str]:
        """Identify VPN provider if possible."""
        try:
            # Get current DNS servers
            with open('/etc/resolv.conf', 'r') as f:
                resolv_conf = f.read()
            
            # Check for known provider DNS servers
            for provider, domains in self.vpn_providers.items():
                if any(domain in resolv_conf for domain in domains):
                    return provider
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to identify VPN provider: {str(e)}")
            return None
    
    def _get_server_location(self) -> Optional[str]:
        """Get VPN server location if available."""
        try:
            response = requests.get('https://ipapi.co/json/', timeout=5)
            data = response.json()
            return f"{data.get('city', 'Unknown')}, {data.get('country_name', 'Unknown')}"
        except Exception as e:
            logger.warning(f"Failed to get server location: {str(e)}")
            return None