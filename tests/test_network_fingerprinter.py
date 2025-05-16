"""Tests for network fingerprinting functionality."""
import json
from unittest.mock import Mock, patch

import pytest
import responses
from requests.exceptions import RequestException

from nethealth.adapters.network_fingerprinter import (
    IPAPIFingerprintDetector,
    NetworkFingerprintError,
)
from nethealth.domain.interfaces import NetworkFingerprint, NetworkInterface


@pytest.fixture
def mock_ip_api_response():
    return {
        "query": "1.2.3.4",
        "isp": "Test ISP",
        "country": "Test Country",
        "city": "Test City",
        "proxy": False,
        "hosting": False,
        "mobile": False,
    }


@pytest.fixture
def mock_tor_response():
    return {
        "IsTor": False,
        "IP": "1.2.3.4"
    }


@pytest.fixture
def mock_network_interfaces():
    return {
        "eth0": [
            Mock(family=2, address="192.168.1.1"),  # AF_INET
            Mock(family=17, address="00:11:22:33:44:55"),  # AF_LINK
        ]
    }


@pytest.fixture
def mock_interface_stats():
    return {
        "eth0": Mock(isup=True)
    }


@responses.activate
def test_get_fingerprint_success(
    mock_ip_api_response,
    mock_tor_response,
    mock_network_interfaces,
    mock_interface_stats,
):
    detector = IPAPIFingerprintDetector()
    
    # Mock IP API response
    responses.add(
        responses.GET,
        detector.api_url,
        json=mock_ip_api_response,
        status=200
    )
    
    # Mock Tor check response
    responses.add(
        responses.GET,
        detector.tor_check_url,
        json=mock_tor_response,
        status=200
    )
    
    with patch("psutil.net_if_addrs", return_value=mock_network_interfaces), \
         patch("psutil.net_if_stats", return_value=mock_interface_stats):
        
        result = detector.get_fingerprint()
        
        assert isinstance(result, NetworkFingerprint)
        assert result.public_ip == "1.2.3.4"
        assert result.isp == "Test ISP"
        assert result.country == "Test Country"
        assert result.city == "Test City"
        assert not result.is_vpn
        assert not result.is_proxy
        assert not result.is_tor
        assert len(result.interfaces) == 1
        assert result.interfaces[0].name == "eth0"
        assert result.interfaces[0].ip_address == "192.168.1.1"
        assert result.interfaces[0].mac_address == "00:11:22:33:44:55"
        assert result.interfaces[0].is_active


@responses.activate
def test_get_fingerprint_api_error():
    detector = IPAPIFingerprintDetector()
    
    responses.add(
        responses.GET,
        detector.api_url,
        status=500
    )
    
    with pytest.raises(NetworkFingerprintError):
        detector.get_fingerprint()


def test_get_fingerprint_invalid_response():
    detector = IPAPIFingerprintDetector()
    
    responses.add(
        responses.GET,
        detector.api_url,
        body="Invalid JSON",
        status=200
    )
    
    with pytest.raises(NetworkFingerprintError):
        detector.get_fingerprint()