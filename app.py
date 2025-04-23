import streamlit as st
import os
from google import genai
from dotenv import load_dotenv
from llm_processor import LLMProcessor
from typing import List, Dict, Any, Tuple
import PyPDF2
import io
import asyncio
from pathlib import Path
import pandas as pd
from chronology_generator import generate_chronology_table
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def process_file(file) -> Tuple[str, bool]:
    """Extract text from a file (PDF or text).
    Returns tuple of (text, success)"""
    try:
        # Get file extension
        file_ext = Path(file.name).suffix.lower()
        
        if file_ext == '.pdf':
            # Process PDF file
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.getvalue()))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                text = text.strip()
                if not text:
                    st.error(f"No text could be extracted from {file.name}. The PDF might be scanned or image-based.")
                    return "", False
                return text, True
            except Exception as e:
                st.error(f"Error processing PDF file {file.name}: {str(e)}")
                logger.error(f"PDF processing error for {file.name}: {str(e)}", exc_info=True)
                return "", False
        else:
            # Process text file
            try:
                text = file.getvalue().decode('utf-8').strip()
                if not text:
                    st.error(f"File {file.name} is empty.")
                    return "", False
                return text, True
            except Exception as e:
                st.error(f"Error processing text file {file.name}: {str(e)}")
                logger.error(f"Text file processing error for {file.name}: {str(e)}", exc_info=True)
                return "", False
            
    except Exception as e:
        st.error(f"Error processing file {file.name}: {str(e)}")
        logger.error(f"File processing error for {file.name}: {str(e)}", exc_info=True)
        return "", False

async def process_documents(files, case_description: str):
    """Process multiple documents and create chronology."""
    try:
        # Initialize LLM processor
        processor = LLMProcessor()
        
        all_events = []
        
        # Process each file
        with st.spinner('Processing documents...'):
            for file in files:
                st.write(f"Processing {file.name}...")
                
                # Extract text from file
                text, success = process_file(file)
                if not success:
                    continue
                
                # Extract events
                try:
                    events = await processor.extract_events(text, file.name)
                    if events:
                        all_events.extend(events)
                        st.write(f"✓ Successfully extracted {len(events)} events from {file.name}")
                    else:
                        st.warning(f"No events could be extracted from {file.name}")
                except Exception as e:
                    st.error(f"Error extracting events from {file.name}: {str(e)}")
                    logger.error(f"Event extraction error for {file.name}: {str(e)}", exc_info=True)
                    continue
        
        if not all_events:
            st.error("No events could be extracted from any of the documents.")
            return
        
        # Create chronology
        with st.spinner('Creating chronology...'):
            try:
                chronology = await processor.create_chronology(all_events, case_description)
                
                # Format chronology as markdown
                markdown_output = processor.format_chronology(chronology)
                
                # Display results
                st.markdown(markdown_output)
                
                # Add download button
                st.download_button(
                    label="Download Chronology",
                    data=markdown_output,
                    file_name="chronology.md",
                    mime="text/markdown"
                )
                
            except Exception as e:
                st.error(f"Error creating chronology: {str(e)}")
                logger.error("Chronology creation error", exc_info=True)
                return
            
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        logger.error("Unexpected error in document processing", exc_info=True)
        return

def main():
    st.title('Case Chronology Generator')
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload documents (PDF or text files)", 
        accept_multiple_files=True,
        type=['pdf', 'txt']
    )
    
    # Case description
    case_description = st.text_area(
        "Case Description",
        help="Provide a brief description of the case to help with analysis."
    )
    
    # Process button
    if st.button('Generate Chronology'):
        if not uploaded_files:
            st.error("Please upload at least one document.")
            return
            
        if not case_description:
            st.warning("Adding a case description will improve the analysis.")
            
        # Process documents
        asyncio.run(process_documents(uploaded_files, case_description))

if __name__ == '__main__':
    main() 