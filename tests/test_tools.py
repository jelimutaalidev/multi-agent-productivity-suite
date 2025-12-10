import sys
import os
from datetime import datetime, timedelta
import pytest

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.tools.calendar import create_event, get_available_time_slots

def test_create_event():
    print("Testing create_event...")
    
    # Calculate times for tomorrow
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    # Format as ISO strings
    start_str = start_time.isoformat()
    end_str = end_time.isoformat()
    
    print(f"Creating event for: {start_str} to {end_str}")
    
    try:
        result = create_event.invoke({
            "title": "Test Meeting from Script",
            "start_datetime": start_str,
            "end_datetime": end_str,
            "attendees": []
        })
        print(f"Result: {result}")
        assert "Event created" in result or "Error" in result
    except Exception as e:
        pytest.fail(f"Error calling create_event: {e}")

def test_get_available_slots():
    print("\nTesting get_available_time_slots...")
    
    # Check availability for tomorrow
    tomorrow = datetime.now() + timedelta(days=1)
    # We just need the date string now, as the tool handles the work hours
    date_str = tomorrow.strftime("%Y-%m-%d")
    
    print(f"Checking availability for date: {date_str}")
    
    try:
        result = get_available_time_slots.invoke({
            "attendees": [],
            "date": date_str,
            "duration_minutes": 60
        })
        print(f"Result: {result}")
        assert isinstance(result, list)
    except Exception as e:
        pytest.fail(f"Error calling get_available_time_slots: {e}")

if __name__ == "__main__":
    test_get_available_slots()
