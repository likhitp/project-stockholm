"""
This module contains all the prompts used in the application for LLM interactions.
"""

# System instruction for event extraction from documents
EVENT_EXTRACTION_SYSTEM_INSTRUCTION = """Extract key events, dates, and entities from legal documents and format them as specified.

Analyze the given legal document text to identify and extract all events mentioned. 

- **Events**: Describe what happened in a specific and detailed manner.
- **Dates**: Convert all dates to the YYYY-MM-DD format.
- **Parties**: Identify all relevant parties involved.
- **Source**: Provide the document reference.

# Steps

1. **Read the Document**: Carefully analyze the provided text.
2. **Identify Key Information**: Extract specific details regarding the events, dates, involved parties, and the source of the information.
3. **Convert Date Format**: Ensure all identified dates are in YYYY-MM-DD format for consistency.
4. **Compile Results**: Structure the extracted data as a JSON array following the given format accurately.

# Output Format

Provide the extracted events in a JSON array format. Each event should be structured as follows:
```json
{
  "event": "Description of what happened",
  "date": "YYYY-MM-DD",
  "parties": ["Party A", "Party B", ...],
  "source": "Document reference"
}
```

# Examples

**Example Start:**

Input:
"On January 5, 2022, Company A entered into a merger agreement with Company B as per document ref. ABC-123."

Output:
```json
[
  {
    "event": "Entered into a merger agreement",
    "date": "2022-01-05",
    "parties": ["Company A", "Company B"],
    "source": "ABC-123"
  }
]
```

**Example End**

# Notes

- Pay attention to linguistic nuances that might indicate parties, such as "plaintiff," "defendant," or corporate roles like "CEO."
- Highlight overlapping events to ensure clarity in distinction.
- Handle diverse date formats and convert them accurately."""

# Chronology analysis prompt
# CHRONOLOGY_PROMPT = '''You are a legal chronology expert. Analyze the provided events and create a coherent chronological narrative.
#
# Your tasks:
# 1. Sort events by date
# 2. Identify relationships between events
# 3. Highlight key turning points
# 4. Note any inconsistencies or gaps in the timeline
# 5. Consider the case context: {case_description}
#
# For each event, add an 'ai_observations' field with insights about:
# - How this event relates to others
# - Its significance in the timeline
# - Any potential implications
# - Connections to the case description
#
# Format your response as a JSON array of events, where each event has:
# {
#     "date": "YYYY-MM-DD",
#     "description": "event description",
#     "parties": ["party1", "party2"],
#     "source_document": "filename",
#     "ai_observations": "Your insights about this event"
# }'''
