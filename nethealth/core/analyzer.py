"""Core network analysis functionality."""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from nethealth.adapters.speed_test import SpeedTestAdapter
from nethealth.adapters.network_fingerprinter import IPAPIFingerprintDetector
from nethealth.adapters.vpn_detector import VPNDetector
from nethealth.domain.interfaces import NetworkReport, NetworkSpeed, NetworkFingerprint, VPNStatus
from nethealth.plugins import PluginManager

logger = logging.getLogger(__name__)

class NetworkAnalyzer:
    """Coordinates network analysis components."""
    
    def __init__(self):
        self.speed_tester = SpeedTestAdapter()
        self.fingerprinter = IPAPIFingerprintDetector()
        self.vpn_detector = VPNDetector()
        self.plugin_manager = PluginManager()
    
    def analyze(self) -> NetworkReport:
        """Perform synchronous network analysis."""
        logger.info("Starting network analysis")
        
        # Measure network speed
        speed: Optional[NetworkSpeed] = None
        try:
            speed = self.speed_tester.measure_speed()
            logger.info(f"Speed test results: {speed}")
        except Exception as e:
            logger.error(f"Speed test failed: {str(e)}")
        
        # Get network fingerprint
        fingerprint: Optional[NetworkFingerprint] = None
        try:
            fingerprint = self.fingerprinter.get_fingerprint()
            logger.info(f"Network fingerprint: {fingerprint}")
        except Exception as e:
            logger.error(f"Fingerprinting failed: {str(e)}")
        
        # Check VPN status
        vpn_status: Optional[VPNStatus] = None
        try:
            vpn_status = self.vpn_detector.check_status()
            logger.info(f"VPN status: {vpn_status}")
        except Exception as e:
            logger.error(f"VPN detection failed: {str(e)}")
        
        # Create report
        report = NetworkReport(
            timestamp=datetime.now(),
            speed=speed,
            fingerprint=fingerprint,
            vpn_status=vpn_status or VPNStatus(is_active=False, provider=None, server_location=None)
        )
        
        # Process through plugins
        try:
            report = self.plugin_manager.process_report(report)
        except Exception as e:
            logger.error(f"Plugin processing failed: {str(e)}")
        
        return report
    
    async def analyze_async(self) -> NetworkReport:
        """Perform asynchronous network analysis."""
        return await asyncio.to_thread(self.analyze)