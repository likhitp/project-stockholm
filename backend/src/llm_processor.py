import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import dateparser
from dotenv import load_dotenv
from google import genai
from google.genai import types

from .chronology_generator import (
    analyze_chronology,
    extract_event_details,
    generate_chronology_table,
)
from .prompts import EVENT_EXTRACTION_SYSTEM_INSTRUCTION

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class LLMProcessor:
    def __init__(self):
        # Initialize Gemini client with Helicone integration
        self.client = genai.Client(
            api_key=os.environ.get("GOOGLE_API_KEY"),
            http_options={
                "base_url": "https://gateway.helicone.ai",
                "headers": {
                    "helicone-auth": f"Bearer {os.environ.get('HELICONE_API_KEY')}",
                    "helicone-target-url": "https://generativelanguage.googleapis.com",
                },
            },
        )
        self.model = "gemini-2.5-flash-preview-04-17"

    async def extract_events(self, document_text: str, document_name: str) -> List[Dict[str, Any]]:
        """Extract events from a single document using Gemini."""
        try:
            # Create content
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=document_text),
                    ],
                ),
            ]

            # Create generation config
            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=0,
                ),
                response_mime_type="text/plain",
                system_instruction=[
                    types.Part.from_text(text=EVENT_EXTRACTION_SYSTEM_INSTRUCTION),
                ],
            )

            logger.info(f"Sending request to Gemini API for {document_name}...")

            # Generate response
            response_stream = self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )

            # Collect response chunks
            response_text = ""
            for chunk in response_stream:
                response_text += chunk.text

            response_text = response_text.strip()

            # Find JSON content
            json_start = response_text.find("[")
            json_end = response_text.rfind("]") + 1

            if json_start == -1 or json_end == 0:
                logger.warning(
                    f"No JSON array found in response for {document_name}: '{response_text[:100]}...'"
                )
                return []

            # Extract and clean JSON
            json_text = response_text[json_start:json_end]
            json_text = re.sub(r"\s+", " ", json_text)  # Normalize whitespace

            try:
                # Parse JSON
                events = json.loads(json_text)
                if not isinstance(events, list):
                    logger.warning(
                        f"Parsed JSON is not a list for {document_name}, wrapping in list. Type: {type(events)}"
                    )
                    events = [events] if isinstance(events, dict) else []

                # Validate and standardize events
                standardized_events = []
                for event in events:
                    if isinstance(event, dict):
                        # Convert the new format to the old format if needed
                        if "event" in event:
                            event["description"] = event.pop("event")
                        if "source" in event:
                            event["source_document"] = event.pop("source")

                        event["source_document"] = document_name
                        standardized_event = extract_event_details(event)
                        if standardized_event and standardized_event.get("description"):
                            standardized_events.append(standardized_event)
                        else:
                            logger.warning(
                                f"Skipping invalid or empty event structure in {document_name}: {event}"
                            )
                    else:
                        logger.warning(
                            f"Skipping non-dict item in JSON array for {document_name}: {event}"
                        )

                logger.info(
                    f"Successfully extracted and standardized {len(standardized_events)} events from {document_name}"
                )
                return standardized_events

            except json.JSONDecodeError as je:
                logger.error(f"JSON parsing error for {document_name}: {str(je)}", exc_info=True)
                logger.error(f"Failed to parse JSON text: {json_text}")
                return []
            except TypeError as te:
                logger.error(
                    f"Type error during event processing for {document_name}: {str(te)}",
                    exc_info=True,
                )
                return []

        except Exception as e:
            logger.error(
                f"Unexpected error extracting events from {document_name}: {type(e).__name__} - {str(e)}",
                exc_info=True,
            )
            return []

    async def create_chronology(
        self, events: List[Dict[str, Any]], case_description: str
    ) -> Dict[str, Any]:
        """Create a chronological analysis using Gemini."""
        try:
            # Format the events as text
            events_text = json.dumps(events, indent=2)

            # Create content
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(
                            text=f"Case Description:\n{case_description}\n\nEvents:\n{events_text}"
                        ),
                    ],
                ),
            ]

            # Create generation config
            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=0,
                ),
                response_mime_type="text/plain",
                system_instruction=[
                    types.Part.from_text(text=EVENT_EXTRACTION_SYSTEM_INSTRUCTION),
                ],
            )

            logger.info("Sending request to Gemini API for chronology creation...")

            # Generate response
            response_stream = self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )

            # Collect response chunks
            response_text = ""
            for chunk in response_stream:
                response_text += chunk.text

            response_text = response_text.strip()

            # Try to find JSON content within the response
            json_start = response_text.find("[")
            json_end = response_text.rfind("]")

            if json_start != -1 and json_end != -1:
                response_text = response_text[json_start : json_end + 1]
            else:
                # If no array found, try to find a single object
                json_start = response_text.find("{")
                json_end = response_text.rfind("}")
                if json_start != -1 and json_end != -1:
                    response_text = f"[{response_text[json_start:json_end + 1]}]"
                else:
                    logger.error(f"No valid JSON found in chronology response")
                    return {"events": events, "analysis": analyze_chronology(events)}

            # Clean up common formatting issues
            response_text = response_text.replace("\n", " ")
            response_text = " ".join(response_text.split())  # Normalize whitespace

            # Parse the response as JSON and standardize events
            try:
                processed_events = json.loads(response_text)
                if not isinstance(processed_events, list):
                    processed_events = [processed_events]

                # Validate and standardize each event
                standardized_events = []
                for event in processed_events:
                    if isinstance(event, dict):
                        standardized_event = extract_event_details(event)
                        if standardized_event.get(
                            "description"
                        ):  # Only include events with descriptions
                            standardized_events.append(standardized_event)

                # If no valid events were found, use the original events
                if not standardized_events:
                    standardized_events = events

                # Generate analysis
                analysis = analyze_chronology(standardized_events)

                return {"events": standardized_events, "analysis": analysis}

            except json.JSONDecodeError as je:
                logger.error(f"JSON parsing error in chronology creation: {str(je)}", exc_info=True)
                return {"events": events, "analysis": analyze_chronology(events)}

        except Exception as e:
            logger.error(f"Error creating chronology: {str(e)}", exc_info=True)
            return {"events": events, "analysis": analyze_chronology(events)}

    def format_chronology(self, chronology: Dict[str, Any]) -> str:
        """Format the chronology as a markdown document."""
        # Generate the main chronology table
        output = "# Case Chronology\n\n"
        output += "## Timeline of Events\n\n"
        output += generate_chronology_table(chronology["events"])

        # Add analysis sections
        analysis = chronology["analysis"]

        if analysis["key_observations"]:
            output += "\n## Key Observations\n\n"
            for obs in analysis["key_observations"]:
                output += f"- {obs}\n"

        if analysis["potential_gaps"]:
            output += "\n## Timeline Gaps\n\n"
            for gap in analysis["potential_gaps"]:
                output += f"- {gap}\n"

        if analysis["recommendations"]:
            output += "\n## Recommendations\n\n"
            for rec in analysis["recommendations"]:
                output += f"- {rec}\n"

        return output


def parse_date(date_str: str) -> Optional[str]:
    """Parse a date string into a standardized format."""
    if not date_str:
        return None
    try:
        # Use dateparser to handle various date formats
        parsed_date = dateparser.parse(
            date_str,
            settings={
                "PREFER_DAY_OF_MONTH": "first",
                "PREFER_DATES_FROM": "past",
                "RELATIVE_BASE": datetime.now(),
            },
        )
        if parsed_date:
            return parsed_date.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Error parsing date '{date_str}': {str(e)}")
    return None


def extract_event_details(event: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and standardize event details."""
    try:
        # Get required fields with defaults
        description = str(event.get("description", "")).strip()
        date = parse_date(str(event.get("date", "")))

        # Get parties/participants (handle both field names)
        parties = event.get("parties", event.get("participants", []))
        if isinstance(parties, str):
            parties = [p.strip() for p in parties.split(",") if p.strip()]
        elif not isinstance(parties, list):
            parties = []

        # Get source document
        source_document = str(event.get("source_document", event.get("source", ""))).strip()

        # Create standardized event
        return {
            "description": description,
            "date": date,
            "source_document": source_document,
            "parties": parties,
        }
    except Exception as e:
        print(f"Error extracting event details: {str(e)}")
        return {"description": "", "date": None, "source_document": "", "parties": []}
