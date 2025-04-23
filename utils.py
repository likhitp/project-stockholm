import os
from typing import List, Dict, Any
from pathlib import Path
import google.generativeai as genai
from helicone.openai_proxy import openai
from PyPDF2 import PdfReader
import re

def setup_gemini():
    """Configure Gemini API with API key and Helicone headers"""
    api_key = os.getenv("GOOGLE_API_KEY")
    helicone_key = os.getenv("HELICONE_API_KEY")
    
    if not api_key or not helicone_key:
        raise ValueError("Missing required API keys in environment variables")
    
    genai.configure(api_key=api_key)
    # Configure Helicone headers for monitoring
    openai.api_base = "https://api.helicone.ai/v1"
    openai.api_key = helicone_key

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text content from a PDF file"""
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def clean_and_normalize_text(text: str) -> str:
    """Clean and normalize extracted text"""
    # Remove multiple newlines and spaces
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    
    # Remove special characters while preserving important punctuation
    text = re.sub(r'[^\w\s\-.,;:!?()\'\"$%]', '', text)
    
    # Normalize dates (convert various formats to YYYY-MM-DD)
    date_patterns = [
        (r'(\d{1,2})/(\d{1,2})/(\d{4})', r'\3-\1-\2'),  # MM/DD/YYYY to YYYY-MM-DD
        (r'(\d{1,2})-(\d{1,2})-(\d{4})', r'\3-\1-\2'),  # MM-DD-YYYY to YYYY-MM-DD
    ]
    for pattern, replacement in date_patterns:
        text = re.sub(pattern, replacement, text)
    
    # Normalize line endings
    text = text.replace('\r\n', '\n')
    
    return text.strip()

def process_document(file) -> Dict[str, Any]:
    """Process a single document and extract its content"""
    file_extension = Path(file.name).suffix.lower()
    
    if file_extension != '.pdf':
        raise ValueError(f"Unsupported file type: {file_extension}. Only PDF files are supported in this version.")
    
    text = extract_text_from_pdf(file)
    cleaned_text = clean_and_normalize_text(text)
    
    return {
        "filename": file.name,
        "content": cleaned_text,
        "type": "pdf",
        "raw_text": text  # Keep the raw text for reference if needed
    }

def extract_events_from_document(document: Dict[str, Any], model) -> List[Dict[str, Any]]:
    """Extract events from a single document using Gemini 2.5 Flash"""
    try:
        prompt = f"""Extract key events from the following legal document. For each event, identify:
        1. The date (in YYYY-MM-DD format if available)
        2. A clear description of what happened
        3. The parties involved
        
        Document name: {document['filename']}
        Content:
        {document['content']}
        
        Format your response as a list of JSON objects with the following structure:
        {{"date": "YYYY-MM-DD", "description": "event description", "parties": ["party1", "party2"]}}
        
        If a date is unclear or not provided, use null for the date field.
        Focus on factual events, legal proceedings, communications, and significant actions."""
        
        response = model.generate_content(prompt, generation_config={
            'temperature': 0.1,
            'top_p': 0.8,
            'top_k': 40,
            'max_output_tokens': 2048,
        })
        
        # Parse the response to extract events
        # The response should be in JSON format, but we'll handle potential formatting issues
        try:
            import json
            events = json.loads(response.text)
            if not isinstance(events, list):
                events = [events]  # Handle single event case
            
            # Add source document to each event
            for event in events:
                event['source_document'] = document['filename']
            
            return events
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse events from model response for document: {document['filename']}")
            
    except Exception as e:
        raise Exception(f"Error extracting events from document {document['filename']}: {str(e)}")

def reason_over_events(events: List[Dict[str, Any]], case_description: str, model) -> List[Dict[str, Any]]:
    """Use Gemini 2.5 Pro to reason over and organize events"""
    try:
        # Convert events to a formatted string for the prompt
        events_str = "\n".join([
            f"Date: {event.get('date', 'Unknown')}\n"
            f"Description: {event['description']}\n"
            f"Parties: {', '.join(event['parties'])}\n"
            f"Source: {event['source_document']}\n"
            for event in events
        ])
        
        prompt = f"""Given the following case description and extracted events, please:
        1. Verify and validate the chronological order
        2. Identify any inconsistencies or conflicts in dates
        3. Add relevant observations about event relationships
        4. Merge or split events if needed for clarity
        5. Ensure all dates are in YYYY-MM-DD format where possible
        
        Case Description:
        {case_description}
        
        Events:
        {events_str}
        
        Format your response as a list of JSON objects with the following structure:
        {{
            "date": "YYYY-MM-DD",
            "description": "event description",
            "parties": ["party1", "party2"],
            "source_document": "filename",
            "ai_observations": "relevant observations about this event"
        }}
        
        Sort events chronologically, with null dates at the end."""
        
        response = model.generate_content(prompt, generation_config={
            'temperature': 0.2,
            'top_p': 0.9,
            'top_k': 40,
            'max_output_tokens': 4096,
        })
        
        try:
            import json
            reasoned_events = json.loads(response.text)
            if not isinstance(reasoned_events, list):
                reasoned_events = [reasoned_events]
            return reasoned_events
        except json.JSONDecodeError:
            raise ValueError("Failed to parse reasoned events from model response")
            
    except Exception as e:
        raise Exception(f"Error reasoning over events: {str(e)}")

def generate_chronology_table(events: List[Dict[str, Any]]) -> str:
    """Generate a markdown table from the chronology of events"""
    try:
        # Sort events by date (null dates will be at the end)
        sorted_events = sorted(
            events,
            key=lambda x: x.get('date', '9999-12-31')  # Use far future date for null dates
        )
        
        # Create markdown table header
        table = "| Date | Event Description | Parties Involved | Source Document | AI Observations |\n"
        table += "|------|------------------|-----------------|-----------------|----------------|\n"
        
        # Add each event to the table
        for event in sorted_events:
            date = event.get('date', 'Unknown')
            description = event['description'].replace('\n', ' ')
            parties = ', '.join(event['parties'])
            source = event['source_document']
            observations = event.get('ai_observations', '').replace('\n', ' ')
            
            table += f"| {date} | {description} | {parties} | {source} | {observations} |\n"
        
        return table
    except Exception as e:
        raise Exception(f"Error generating chronology table: {str(e)}")

async def process_documents_and_generate_chronology(documents: List[Dict[str, Any]], case_description: str) -> str:
    """Main function to process documents and generate a chronology"""
    try:
        # Initialize LLM processor
        llm_processor = LLMProcessor()
        
        # Extract events from each document
        all_events = []
        for doc in documents:
            events = await llm_processor.extract_events(doc["content"], doc["filename"])
            all_events.extend(events)
        
        # Generate chronology
        chronology = await llm_processor.create_chronology(all_events, case_description)
        
        # Format and return the chronology
        return llm_processor.format_chronology(chronology)
    except Exception as e:
        raise Exception(f"Error in chronology generation pipeline: {str(e)}")

def process_pdf(file) -> str:
    """
    Process a PDF file and return its cleaned text content.
    
    Args:
        file: A file object or path to a PDF file
        
    Returns:
        Cleaned and normalized text content from the PDF
    """
    text = extract_text_from_pdf(file)
    return clean_and_normalize_text(text) 