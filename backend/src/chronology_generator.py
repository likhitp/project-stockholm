"""
Chronology Generator Module

This module handles the extraction and organization of chronological events from legal documents.
It provides functionality for event extraction, date standardization, and chronology generation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import dateparser
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def standardize_date(date_str: Optional[str]) -> Optional[str]:
    """
    Standardize date strings to YYYY-MM-DD format using dateparser for robust parsing.
    Returns None if date cannot be parsed.
    
    Args:
        date_str: A string containing a date in various possible formats
        
    Returns:
        A string in YYYY-MM-DD format if parsing succeeds, None otherwise
    """
    if not date_str or str(date_str).lower() in ('null', 'none', '', 'n/a'):
        return None
        
    try:
        # Clean up the date string
        date_str = str(date_str).strip()
        
        # Try to parse with dateparser first
        parsed_date = dateparser.parse(
            date_str,
            settings={
                'PREFER_DAY_OF_MONTH': 'first',
                'PREFER_DATES_FROM': 'past',
                'RELATIVE_BASE': datetime.now(),
                'DATE_ORDER': 'YMD',
                'STRICT_PARSING': False
            }
        )
        
        if parsed_date:
            return parsed_date.strftime('%Y-%m-%d')
        
        # Try common date formats
        formats = [
            '%Y-%m-%d', '%Y/%m/%d',  # ISO-like formats
            '%d/%m/%Y', '%m/%d/%Y',  # Common formats with /
            '%d-%m-%Y', '%m-%d-%Y',  # Common formats with -
            '%B %d, %Y', '%d %B %Y', # Month name formats
            '%b %d, %Y', '%d %b %Y', # Abbreviated month formats
            '%Y%m%d',                # Compact format
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # Try to extract year, month, day from the string
        date_parts = re.findall(r'(\d{4})|(\d{1,2})', date_str)
        if date_parts and len(date_parts) >= 3:
            year = month = day = None
            for part in date_parts:
                num = int(''.join(filter(None, part)))
                if not year and 1900 <= num <= 2100:
                    year = num
                elif not month and 1 <= num <= 12:
                    month = num
                elif not day and 1 <= num <= 31:
                    day = num
            
            if year and month and day:
                try:
                    return f"{year:04d}-{month:02d}-{day:02d}"
                except ValueError:
                    pass
        
        return None
        
    except Exception as e:
        logger.warning(f"Error parsing date '{date_str}': {str(e)}")
        return None

def extract_event_details(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and validate event details from an event dictionary.
    Standardizes dates and ensures all required fields are present.
    """
    return {
        "date": standardize_date(event.get("date")),
        "description": event.get("description", "").strip(),
        "parties": list(set(p.strip() for p in event.get("parties", []))),
        "source_document": event.get("source_document", "Unknown"),
        "ai_observations": event.get("ai_observations", "")
    }

def sort_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort events chronologically, with null dates at the end.
    """
    def sort_key(event):
        date = event.get("date")
        return (date if date is not None else "9999-12-31", event.get("source_document", ""))
    
    return sorted(events, key=sort_key)

def generate_chronology_table(events: List[Dict[str, Any]], include_observations: bool = True) -> str:
    """
    Generate a markdown table from the chronology of events.
    """
    # Sort events chronologically
    sorted_events = sort_events(events)
    
    # Create table header
    headers = ["Date", "Description", "Parties", "Source"]
    if include_observations:
        headers.append("AI Observations")
    
    table = f"| {' | '.join(headers)} |\n"
    table += f"|{'|'.join(['---' for _ in headers])}|\n"
    
    # Add each event to the table
    for event in sorted_events:
        # Convert all values to strings, replacing None with "N/A"
        date = str(event.get("date", "N/A"))
        description = str(event.get("description", "")).replace("\n", " ")
        parties = ", ".join(str(p) for p in event.get("parties", []) if p is not None)
        source = str(event.get("source_document", "Unknown"))
        
        row = [date if date != "None" else "N/A", 
               description if description != "None" else "N/A", 
               parties if parties else "N/A", 
               source if source != "None" else "N/A"]
               
        if include_observations:
            observations = str(event.get("ai_observations", "")).replace("\n", " ")
            row.append(observations if observations != "None" else "N/A")
            
        table += f"| {' | '.join(row)} |\n"
    
    return table

def analyze_chronology(events: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Analyze the chronology to identify gaps, patterns, and key observations.
    """
    sorted_events = sort_events(events)
    analysis = {
        "key_observations": [],
        "potential_gaps": [],
        "recommendations": []
    }
    
    # Check for date gaps
    for i in range(len(sorted_events) - 1):
        current = sorted_events[i]
        next_event = sorted_events[i + 1]
        
        if current["date"] and next_event["date"]:
            current_date = datetime.strptime(current["date"], "%Y-%m-%d")
            next_date = datetime.strptime(next_event["date"], "%Y-%m-%d")
            gap_days = (next_date - current_date).days
            
            if gap_days > 30:  # Significant gap threshold
                analysis["potential_gaps"].append(
                    f"Gap of {gap_days} days between events on {current['date']} and {next_event['date']}"
                )
    
    # Check for missing dates
    missing_dates = [e for e in events if not e["date"]]
    if missing_dates:
        analysis["recommendations"].append(
            f"Found {len(missing_dates)} events with missing dates. Consider reviewing source documents."
        )
    
    # Identify key parties
    all_parties = set()
    for event in events:
        all_parties.update(event.get("parties", []))
    
    if all_parties:
        analysis["key_observations"].append(
            f"Key parties involved: {', '.join(sorted(all_parties))}"
        )
    
    return analysis

class ChronologyGenerator:
    """
    A class to generate and manage chronological event data.
    """
    
    def __init__(self):
        """Initialize the ChronologyGenerator."""
        pass
        
    def generate_chronology(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a chronological representation of events with analysis.
        
        Args:
            events: List of event dictionaries containing date, description, etc.
            
        Returns:
            Dictionary containing:
            - events: List of processed and sorted events
            - analysis: Dictionary of analysis results
            - markdown_table: String containing markdown formatted table
        """
        # Process and validate each event
        processed_events = [extract_event_details(event) for event in events]
        
        # Remove events with invalid dates
        valid_events = [event for event in processed_events if event['date'] is not None]
        
        # Sort events chronologically
        sorted_events = sort_events(valid_events)
        
        # Generate analysis
        analysis = analyze_chronology(sorted_events)
        
        # Generate markdown table
        markdown_table = generate_chronology_table(sorted_events)
        
        return {
            'events': sorted_events,
            'analysis': analysis,
            'markdown_table': markdown_table,
            'errors': [] if len(valid_events) == len(processed_events) else ['Some events had invalid dates']
        }
        
    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single event to ensure it has all required fields.
        
        Args:
            event: Dictionary containing event information
            
        Returns:
            Processed event dictionary
        """
        return extract_event_details(event)
        
    def validate_chronology(self, events: List[Dict[str, Any]]) -> List[str]:
        """
        Validate a list of events for consistency and completeness.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        if not events:
            errors.append("No events provided")
            return errors
            
        # Check for required fields
        for i, event in enumerate(events):
            if not event.get('description'):
                errors.append(f"Event {i+1} is missing a description")
            if not event.get('date'):
                errors.append(f"Event {i+1} is missing a date")
                
        # Check chronological order
        sorted_events = sort_events(events)
        if sorted_events != events:
            errors.append("Events are not in chronological order")
            
        return errors 