"""Tests for network speed testing functionality."""
import pytest
from unittest.mock import Mock, patch

from nethealth.adapters.speed_test import SpeedTestAdapter, SpeedTestError
from nethealth.domain.interfaces import NetworkSpeed

@pytest.fixture
def mock_speedtest():
    with patch('speedtest.Speedtest') as mock:
        client = mock.return_value
        client.download.return_value = 100_000_000  # 100 Mbps
        client.upload.return_value = 50_000_000    # 50 Mbps
        client.results.ping = 20.5
        client.get_best_server.return_value = {
            'host': 'test.server.com',
            'country': 'Test Country'
        }
        yield mock

def test_measure_speed_success(mock_speedtest):
    adapter = SpeedTestAdapter()
    result = adapter.measure_speed()
    
    assert isinstance(result, NetworkSpeed)
    assert result.download_mbps == 100.0
    assert result.upload_mbps == 50.0
    assert result.ping_ms == 20.5

@pytest.mark.parametrize("error_class,error_message", [
    (speedtest.ConfigRetrievalError, "Failed to retrieve speedtest configuration"),
    (speedtest.NoMatchedServers, "No available speedtest servers found"),
    (speedtest.SpeedtestException, "Speed test failed: Generic error"),
])
def test_measure_speed_errors(mock_speedtest, error_class, error_message):
    mock_speedtest.return_value.get_servers.side_effect = error_class("Generic error")
    
    adapter = SpeedTestAdapter()
    with pytest.raises(SpeedTestError, match=error_message):
        adapter.measure_speed()

def test_measure_speed_timeout():
    adapter = SpeedTestAdapter(timeout=1)
    with pytest.raises(SpeedTestError):
        adapter.measure_speed()