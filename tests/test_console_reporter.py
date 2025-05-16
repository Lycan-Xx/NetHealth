"""Tests for console reporting functionality."""
from datetime import datetime
from unittest.mock import Mock

import pytest
from rich.console import Console

from nethealth.adapters.console_reporter import ConsoleReporter
from nethealth.domain.interfaces import (
    NetworkReport,
    NetworkSpeed,
    NetworkFingerprint,
    NetworkInterface,
    VPNStatus
)


@pytest.fixture
def mock_report():
    return NetworkReport(
        timestamp=datetime(2023, 1, 1, 12, 0, 0),
        speed=NetworkSpeed(
            download_mbps=100.0,
            upload_mbps=50.0,
            ping_ms=20.5
        ),
        fingerprint=NetworkFingerprint(
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
        ),
        vpn_status=VPNStatus(
            is_active=False,
            provider=None,
            server_location=None
        )
    )


def test_console_reporter(mock_report, capsys):
    reporter = ConsoleReporter()
    reporter.report(mock_report)
    
    # Basic output verification
    captured = capsys.readouterr()
    assert "Network Health Report" in captured.out
    assert "Speed Test Results" in captured.out
    assert "Network Fingerprint" in captured.out
    assert "Network Interfaces" in captured.out
    
    # Verify specific data points
    assert "100.0 Mbps" in captured.out  # Download speed
    assert "50.0 Mbps" in captured.out   # Upload speed
    assert "20.5 ms" in captured.out     # Ping
    assert "1.2.3.4" in captured.out     # Public IP
    assert "Test ISP" in captured.out    # ISP
    assert "eth0" in captured.out        # Interface name