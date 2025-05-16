"""Integration tests for network analysis functionality."""
import pytest
from unittest.mock import Mock, patch

from nethealth.core.analyzer import NetworkAnalyzer
from nethealth.domain.interfaces import (
    NetworkReport,
    NetworkSpeed,
    NetworkFingerprint,
    NetworkInterface,
    VPNStatus,
)

@pytest.fixture
def analyzer():
    return NetworkAnalyzer()

@pytest.fixture
def mock_speed_test():
    with patch('nethealth.adapters.speed_test.SpeedTestAdapter') as mock:
        mock.return_value.measure_speed.return_value = NetworkSpeed(
            download_mbps=100.0,
            upload_mbps=50.0,
            ping_ms=20.5
        )
        yield mock

@pytest.fixture
def mock_fingerprinter():
    with patch('nethealth.adapters.network_fingerprinter.IPAPIFingerprintDetector') as mock:
        mock.return_value.get_fingerprint.return_value = NetworkFingerprint(
            public_ip="1.2.3.4",
            isp="Test ISP",
            country="Test Country",
            city="Test City",
            is_vpn=False,
            is_proxy=False,
            is_tor=False,
            interfaces=[
                NetworkInterface(
                    name="eth0",
                    ip_address="192.168.1.1",
                    mac_address="00:11:22:33:44:55",
                    is_active=True
                )
            ]
        )
        yield mock

def test_full_analysis(analyzer, mock_speed_test, mock_fingerprinter):
    """Test the complete network analysis flow."""
    report = analyzer.analyze()
    
    assert isinstance(report, NetworkReport)
    assert report.speed.download_mbps == 100.0
    assert report.fingerprint.public_ip == "1.2.3.4"
    assert len(report.fingerprint.interfaces) == 1

def test_analysis_with_failed_speed_test(analyzer, mock_fingerprinter):
    """Test graceful handling of speed test failures."""
    with patch('nethealth.adapters.speed_test.SpeedTestAdapter') as mock:
        mock.return_value.measure_speed.side_effect = Exception("Speed test failed")
        
        report = analyzer.analyze()
        
        assert report.speed is None
        assert report.fingerprint.public_ip == "1.2.3.4"

def test_analysis_with_failed_fingerprinting(analyzer, mock_speed_test):
    """Test graceful handling of fingerprinting failures."""
    with patch('nethealth.adapters.network_fingerprinter.IPAPIFingerprintDetector') as mock:
        mock.return_value.get_fingerprint.side_effect = Exception("Fingerprinting failed")
        
        report = analyzer.analyze()
        
        assert report.speed.download_mbps == 100.0
        assert report.fingerprint is None

@pytest.mark.asyncio
async def test_async_analysis(analyzer, mock_speed_test, mock_fingerprinter):
    """Test asynchronous network analysis."""
    report = await analyzer.analyze_async()
    
    assert isinstance(report, NetworkReport)
    assert report.speed.download_mbps == 100.0
    assert report.fingerprint.public_ip == "1.2.3.4"