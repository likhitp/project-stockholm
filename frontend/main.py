import streamlit as st
import requests
from utils.file_processor import process_file
import logging
from typing import List, Tuple, Any
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants
BACKEND_URL = "http://backend:8000/api/v1"  # Using docker-compose service name

def process_documents(files: List[Any], case_description: str) -> None:
    """Process multiple documents and create chronology."""
    try:
        documents_text = []
        document_names = []
        
        # Process each file
        with st.spinner('Processing documents...'):
            for file in files:
                st.write(f"Processing {file.name}...")
                
                # Extract text from file
                text, success = process_file(file.getvalue(), file.name)
                if not success:
                    continue
                
                documents_text.append(text)
                document_names.append(file.name)
        
        if not documents_text:
            st.error("No text could be extracted from any of the documents.")
            return
            
        # Send request to backend
        response = requests.post(
            f"{BACKEND_URL}/chronology/generate",
            json={
                "case_description": case_description,
                "documents_text": documents_text,
                "document_names": document_names
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Display results
            st.markdown(data["markdown_output"])
            
            # Add download button
            st.download_button(
                label="Download Chronology",
                data=data["markdown_output"],
                file_name="chronology.md",
                mime="text/markdown"
            )
        else:
            st.error(f"Error from backend: {response.text}")
            
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
        process_documents(uploaded_files, case_description)

if __name__ == '__main__':
    main() 