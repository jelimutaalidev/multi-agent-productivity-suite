from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging
from dateutil import parser
from googleapiclient.discovery import build
from langchain.tools import tool
from app.core.auth import authenticate_google_services
from app.core.utils import format_dt
from app.core.config import config

logger = logging.getLogger(__name__)

def get_calendar_service():
    """Returns an authenticated Google Calendar service resource."""
    creds = authenticate_google_services()
    service = build("calendar", "v3", credentials=creds)
    return service

class ListEventsInput(BaseModel):
    start_datetime: str = Field(description="ISO 8601 string for start time (e.g., '2024-01-01T09:00:00')")
    end_datetime: str = Field(description="ISO 8601 string for end time (e.g., '2024-01-01T17:00:00')")

@tool(args_schema=ListEventsInput)
def list_events(start_datetime: str, end_datetime: str) -> str:
    """
    List events on the user's calendar within a specified date range.
    """
    logger.info(f"Listing events from {start_datetime} to {end_datetime}")
    service = get_calendar_service()
    
    try:
        time_min = format_dt(start_datetime)
        time_max = format_dt(end_datetime)
    except ValueError as e:
        return f"Error parsing dates: {e}"
    
    try:
        events_result = service.events().list(
            calendarId=config.CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        events = events_result.get("items", [])
        
        if not events:
            return "No events found."
        
        result = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "No Title")
            result.append(f"{start} - {summary}")
            
        return "\n".join(result)
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        return f"Error listing events: {e}"

class CreateEventInput(BaseModel):
    title: str = Field(description="Title of the event")
    start_datetime: str = Field(description="ISO 8601 string for start time")
    end_datetime: str = Field(description="ISO 8601 string for end time")
    attendees: list[str] = Field(default=[], description="List of email addresses for attendees")

@tool(args_schema=CreateEventInput)
def create_event(title: str, start_datetime: str, end_datetime: str, attendees: list[str] = []) -> str:
    """
    Create a new event on the user's calendar.
    """
    logger.info(f"Creating event '{title}' from {start_datetime} to {end_datetime}")
    service = get_calendar_service()
    
    try:
        start_dt = format_dt(start_datetime)
        end_dt = format_dt(end_datetime)
    except ValueError as e:
        return f"Error parsing dates: {e}"
    
    event = {
        "summary": title,
        "start": {
            "dateTime": start_dt,
        },
        "end": {
            "dateTime": end_dt,
        },
        "attendees": [{"email": email} for email in attendees],
    }
    
    try:
        event = service.events().insert(calendarId=config.CALENDAR_ID, body=event).execute()
        return f"Event created: {event.get('htmlLink')}"
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        return f"Error creating event: {e}"

class GetAvailabilityInput(BaseModel):
    attendees: list[str] = Field(description="List of email addresses to check availability for")
    date: str = Field(description="The date to check availability on (ISO format: '2024-01-15')")
    duration_minutes: int = Field(default=30, description="The duration of the desired slot in minutes")

@tool(args_schema=GetAvailabilityInput)
def get_available_time_slots(
    attendees: list[str],
    date: str,
    duration_minutes: int = 30
) -> list[str]:
    """
    Check calendar availability for given attendees on a specific date.
    Implements 'Intersection of Free Time' algorithm.
    """
    logger.info(f"Checking availability for {attendees} on {date}")
    service = get_calendar_service()
    
    try:
        # Parse the target date
        target_date = parser.parse(date)
        if target_date.tzinfo is None:
            target_date = target_date.astimezone()
            
        # Define working hours (08:00 to 17:00) for that day
        work_start = target_date.replace(hour=8, minute=0, second=0, microsecond=0)
        work_end = target_date.replace(hour=17, minute=0, second=0, microsecond=0)
        
        # Ensure we are looking at the future or today
        now = datetime.now().astimezone()
        if work_end < now:
            return ["Date is in the past."]
            
        # If looking at today, start from next hour if work_start is passed
        if work_start < now:
            # Round up to next hour or half hour? Let's just start from now + buffer
            next_start = now.replace(second=0, microsecond=0) + timedelta(minutes=30 - now.minute % 30)
            if next_start > work_start:
                work_start = next_start
            
        time_min = work_start.isoformat()
        time_max = work_end.isoformat()
        
        # Step 1: Fetch Data (FreeBusy Query)
        items = [{"id": config.CALENDAR_ID}]
        for email in attendees:
            items.append({"id": email})
            
        body = {
            "timeMin": time_min,
            "timeMax": time_max,
            "timeZone": "UTC", 
            "items": items
        }
        
        freebusy_result = service.freebusy().query(body=body).execute()
        calendars = freebusy_result.get("calendars", {})
        
        # Step 2: Merge Busy Slots
        busy_intervals = []
        for cal_id, data in calendars.items():
            for busy in data.get("busy", []):
                start = parser.parse(busy["start"])
                end = parser.parse(busy["end"])
                busy_intervals.append((start, end))
                
        # Sort by start time
        busy_intervals.sort(key=lambda x: x[0])
        
        merged_busy = []
        for b_start, b_end in busy_intervals:
            if not merged_busy:
                merged_busy.append((b_start, b_end))
            else:
                last_start, last_end = merged_busy[-1]
                if b_start < last_end:
                    # Overlap, extend end if needed
                    merged_busy[-1] = (last_start, max(last_end, b_end))
                else:
                    merged_busy.append((b_start, b_end))
                    
        # Step 3 & 4: Calculate Free Slots & Filter Duration
        available_slots = []
        current_time = work_start
        
        # Iterate through the day in 30-minute steps (or whatever granularity desired)
        while current_time + timedelta(minutes=duration_minutes) <= work_end:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            is_busy = False
            
            # Check if this candidate slot overlaps with ANY "Forbidden Zone"
            for b_start, b_end in merged_busy:
                # Overlap condition: StartA < EndB AND EndA > StartB
                if current_time < b_end and slot_end > b_start:
                    is_busy = True
                    break
            
            if not is_busy:
                available_slots.append(current_time.isoformat())
                
            # Step forward by 30 minutes
            current_time += timedelta(minutes=30)
            
        if not available_slots:
            return ["No available slots found for the given criteria."]
            
        return available_slots

    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        return [f"Error checking availability: {e}"]
