"""History management for network analysis results."""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List

from nethealth.domain.interfaces import (
    NetworkReport,
    NetworkSpeed,
    NetworkFingerprint,
    NetworkInterface,
    VPNStatus,
    HistoryManager
)

logger = logging.getLogger(__name__)


class JSONHistoryManager(HistoryManager):
    """JSON-based implementation of history management."""
    
    def __init__(self, storage_path: str = "~/.nethealth/history.json"):
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.storage_path.exists():
            self.storage_path.write_text("[]")
    
    def save(self, report: NetworkReport) -> None:
        """Save a report to history."""
        try:
            # Load existing history
            history = self._load_history()
            
            # Convert report to dictionary
            report_dict = {
                "timestamp": report.timestamp.isoformat(),
                "speed": {
                    "download_mbps": report.speed.download_mbps,
                    "upload_mbps": report.speed.upload_mbps,
                    "ping_ms": report.speed.ping_ms
                },
                "fingerprint": {
                    "public_ip": report.fingerprint.public_ip,
                    "isp": report.fingerprint.isp,
                    "country": report.fingerprint.country,
                    "city": report.fingerprint.city,
                    "is_vpn": report.fingerprint.is_vpn,
                    "is_proxy": report.fingerprint.is_proxy,
                    "is_tor": report.fingerprint.is_tor,
                    "interfaces": [
                        {
                            "name": i.name,
                            "ip_address": i.ip_address,
                            "mac_address": i.mac_address,
                            "is_active": i.is_active
                        }
                        for i in report.fingerprint.interfaces
                    ]
                },
                "vpn_status": {
                    "is_active": report.vpn_status.is_active,
                    "provider": report.vpn_status.provider,
                    "server_location": report.vpn_status.server_location
                }
            }
            
            # Add new report and save
            history.append(report_dict)
            self.storage_path.write_text(json.dumps(history, indent=2))
            
        except Exception as e:
            logger.error(f"Failed to save report to history: {str(e)}")
            raise
    
    def get_all(self) -> List[NetworkReport]:
        """Retrieve all historical reports."""
        return self._load_and_convert_history()
    
    def get_latest(self, n: int = 1) -> List[NetworkReport]:
        """Retrieve the n most recent reports."""
        history = self._load_and_convert_history()
        return sorted(history, key=lambda x: x.timestamp, reverse=True)[:n]
    
    def _load_history(self) -> List[dict]:
        """Load raw history data from storage."""
        try:
            return json.loads(self.storage_path.read_text())
        except Exception as e:
            logger.error(f"Failed to load history: {str(e)}")
            return []
    
    def _load_and_convert_history(self) -> List[NetworkReport]:
        """Load and convert history data to NetworkReport objects."""
        history = self._load_history()
        reports = []
        
        for entry in history:
            try:
                # Convert stored interfaces
                interfaces = [
                    NetworkInterface(
                        name=i["name"],
                        ip_address=i["ip_address"],
                        mac_address=i["mac_address"],
                        is_active=i["is_active"]
                    )
                    for i in entry["fingerprint"]["interfaces"]
                ]
                
                # Create report object
                report = NetworkReport(
                    timestamp=datetime.fromisoformat(entry["timestamp"]),
                    speed=NetworkSpeed(
                        download_mbps=entry["speed"]["download_mbps"],
                        upload_mbps=entry["speed"]["upload_mbps"],
                        ping_ms=entry["speed"]["ping_ms"]
                    ),
                    fingerprint=NetworkFingerprint(
                        public_ip=entry["fingerprint"]["public_ip"],
                        isp=entry["fingerprint"]["isp"],
                        country=entry["fingerprint"]["country"],
                        city=entry["fingerprint"]["city"],
                        is_vpn=entry["fingerprint"]["is_vpn"],
                        is_proxy=entry["fingerprint"]["is_proxy"],
                        is_tor=entry["fingerprint"]["is_tor"],
                        interfaces=interfaces
                    ),
                    vpn_status=VPNStatus(
                        is_active=entry["vpn_status"]["is_active"],
                        provider=entry["vpn_status"]["provider"],
                        server_location=entry["vpn_status"]["server_location"]
                    )
                )
                
                reports.append(report)
                
            except Exception as e:
                logger.error(f"Failed to convert history entry: {str(e)}")
                continue
        
        return reports