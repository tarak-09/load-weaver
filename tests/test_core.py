import asyncio
import time
from unittest.mock import AsyncMock, patch
import pytest

from omniload.core import LoadGenerator, RequestResult

class MockResponse:
    def __init__(self, status):
        self.status = status
    
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc, tb):
        pass
        
    async def read(self):
        return b""

@pytest.mark.asyncio
async def test_load_generator_success():
    url = "http://test.local/api"
    qps = 10
    duration = 0.5
    
    with patch("aiohttp.ClientSession.request", return_value=MockResponse(200)):
        generator = LoadGenerator(url, qps, duration)
        results = await generator.run()
        
        assert len(results) == 5
        for res in results:
            assert res.status == 200
            assert res.error == ""
            assert res.latency >= 0


@pytest.mark.asyncio
async def test_load_generator_errors():
    url = "http://test.local/error"
    qps = 5
    duration = 0.4
    
    with patch("aiohttp.ClientSession.request", return_value=MockResponse(500)):
        generator = LoadGenerator(url, qps, duration)
        results = await generator.run()
        
        assert len(results) == 2
        for res in results:
            assert res.status == 500

@pytest.mark.asyncio
async def test_load_generator_custom_method_headers_data():
    url = "http://test.local/api"
    qps = 2
    duration = 0.5
    
    with patch("aiohttp.ClientSession.request", return_value=MockResponse(200)) as mock_request:
        generator = LoadGenerator(url, qps, duration, method="POST", headers={"Content-Type": "application/json"}, data='{"key": "value"}')
        results = await generator.run()
        
        assert len(results) == 1
        mock_request.assert_called_with("POST", url, headers={"Content-Type": "application/json"}, data='{"key": "value"}')


def test_latency_calculation():
    # Test that latency is calculated from intended start, not actual start
    res = RequestResult(
        intended_start_time=100.0,
        actual_start_time=105.0,  # Actually started 5s late!
        completion_time=106.0,
        status=200
    )
    
    # Intended latency = 106.0 - 100.0 = 6.0
    assert res.latency == 6.0
