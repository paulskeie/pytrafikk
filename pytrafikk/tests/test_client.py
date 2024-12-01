import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from ..client import (
    query_traffic_volume, TrafficVolume, VolumeByHour,
    query_traffic_volume_by_day, DailyTrafficVolume, VolumeByDay
)

# Test constants
INVALID_URL = "https://invalid-url-that-does-not-exist.com/"
INVALID_POINT_ID = "invalid_point_id"
BASE_URL = "https://trafikkdata-api.atlas.vegvesen.no/"
TEST_POINT_ID = "97411V72313"  # E6 Mortenhals

def test_pagination_byHour():
    """Test that pagination works correctly for hourly data over multiple days"""
    # Request 3 days of data (72 hours, should require pagination as limit is 100)
    end_time = datetime.now(ZoneInfo("Europe/Oslo")).replace(minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(days=3)
    
    result = query_traffic_volume(
        BASE_URL,
        TEST_POINT_ID,
        start_time.astimezone(ZoneInfo("Europe/Oslo")).isoformat(),
        end_time.astimezone(ZoneInfo("Europe/Oslo")).isoformat()
    )
    
    assert isinstance(result, TrafficVolume)
    assert result.point_id == TEST_POINT_ID
    assert len(result.volumes) >= 70  # Should have ~72 hours of data
    
    # Verify chronological order and no gaps
    for i in range(len(result.volumes) - 1):
        current = result.volumes[i]
        next_vol = result.volumes[i + 1]
        assert current.to_time == next_vol.from_time
        assert isinstance(current.total, int)
        assert 0 <= current.coverage_percentage <= 100

def test_single_page_byHour():
    """Test fetching data that fits in a single page"""
    # Request 12 hours of data (should fit in one page)
    end_time = datetime.now(ZoneInfo("Europe/Oslo")).replace(minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(hours=12)
    
    result = query_traffic_volume(
        BASE_URL,
        TEST_POINT_ID,
        start_time.isoformat(),
        end_time.isoformat()
    )
    
    assert isinstance(result, TrafficVolume)
    assert len(result.volumes) <= 12
    assert all(isinstance(v, VolumeByHour) for v in result.volumes)
    
    # Verify timezone information is preserved
    for volume in result.volumes:
        assert volume.from_time.tzinfo is not None
        assert volume.to_time.tzinfo is not None
        # Accept both named timezones and offset format
        tz_name = volume.from_time.tzname()
        assert any(name in tz_name for name in ["CET", "CEST", "UTC+01:00", "UTC+02:00"])

def test_invalid_url():
    """Test that invalid URL raises appropriate exception"""
    with pytest.raises(Exception) as exc_info:
        query_traffic_volume(
            INVALID_URL,
            TEST_POINT_ID,
            datetime.now(ZoneInfo("Europe/Oslo")).isoformat(),
            datetime.now(ZoneInfo("Europe/Oslo")).isoformat()
        )
    # Connection errors are also valid for invalid URLs
    error_msg = str(exc_info.value)
    assert any(msg in error_msg for msg in ["Query failed", "Max retries exceeded", "Failed to resolve"])

def test_invalid_point_id():
    """Test that invalid point ID results in GraphQL error"""
    with pytest.raises(Exception) as exc_info:
        query_traffic_volume(
            BASE_URL,
            INVALID_POINT_ID,
            datetime.now(ZoneInfo("Europe/Oslo")).isoformat(),
            datetime.now(ZoneInfo("Europe/Oslo")).isoformat()
        )
    assert "GraphQL errors" in str(exc_info.value)

def test_daily_volume():
    """Test fetching daily traffic volume data"""
    # Request 7 days of data
    end_time = datetime.now(ZoneInfo("Europe/Oslo")).replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(days=7)
    
    result = query_traffic_volume_by_day(
        BASE_URL,
        TEST_POINT_ID,
        start_time.isoformat(),
        end_time.isoformat()
    )
    
    assert isinstance(result, DailyTrafficVolume)
    assert result.point_id == TEST_POINT_ID
    assert len(result.volumes) <= 7  # Should have up to 7 days of data
    
    # Verify data structure and values
    for volume in result.volumes:
        assert isinstance(volume, VolumeByDay)
        assert isinstance(volume.total, int)
        assert 0 <= volume.coverage_percentage <= 100
        assert volume.from_time.tzinfo is not None
        assert volume.to_time.tzinfo is not None
        # Verify each period is exactly 24 hours
        assert (volume.to_time - volume.from_time).total_seconds() == 24 * 60 * 60

def test_invalid_date_range():
    """Test that end time before start time raises error"""
    end_time = datetime.now(ZoneInfo("Europe/Oslo"))
    start_time = end_time + timedelta(days=1)  # Start time after end time
    
    with pytest.raises(Exception) as exc_info:
        query_traffic_volume(
            BASE_URL,
            TEST_POINT_ID,
            start_time.isoformat(),
            end_time.isoformat()
        )
    assert "GraphQL errors" in str(exc_info.value)
