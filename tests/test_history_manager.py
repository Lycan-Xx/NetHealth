"""Tests for history management functionality."""
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from nethealth.core.history_manager import JSONHistoryManager
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


@pytest.fixture
def temp_history_file(tmp_path):
    history_file = tmp_path / "history.json"
    history_file.write_text("[]")
    return str(history_file)


def test_save_and_load_report(mock_report, temp_history_file):
    manager = JSONHistoryManager(temp_history_file)
    
    # Save report
    manager.save(mock_report)
    
    # Load and verify
    reports = manager.get_all()
    assert len(reports) == 1
    
    loaded_report = reports[0]
    assert loaded_report.timestamp == mock_report.timestamp
    assert loaded_report.speed.download_mbps == mock_report.speed.download_mbps
    assert loaded_report.fingerprint.public_ip == mock_report.fingerprint.public_ip
    assert len(loaded_report.fingerprint.interfaces) == len(mock_report.fingerprint.interfaces)


def test_get_latest_reports(mock_report, temp_history_file):
    manager = JSONHistoryManager(temp_history_file)
    
    # Save multiple reports
    reports = [
        mock_report,
        NetworkReport(
            timestamp=datetime(2023, 1, 1, 13, 0, 0),
            speed=mock_report.speed,
            fingerprint=mock_report.fingerprint,
            vpn_status=mock_report.vpn_status
        )
    ]
    
    for report in reports:
        manager.save(report)
    
    # Get latest report
    latest = manager.get_latest(1)
    assert len(latest) == 1
    assert latest[0].timestamp == reports[1].timestamp


def test_handle_corrupted_history_file(temp_history_file):
    # Write corrupted JSON
    Path(temp_history_file).write_text("invalid json")
    
    manager = JSONHistoryManager(temp_history_file)
    reports = manager.get_all()
    
    assert reports == []