import io
import logging
from pathlib import Path
from typing import Tuple

import PyPDF2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_file(file_content: bytes, filename: str) -> Tuple[str, bool]:
    """Extract text from a file (PDF or text).
    Returns tuple of (text, success)"""
    try:
        # Get file extension
        file_ext = Path(filename).suffix.lower()

        if file_ext == ".pdf":
            # Process PDF file
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                text = text.strip()
                if not text:
                    logger.error(
                        f"No text could be extracted from {filename}. The PDF might be scanned or image-based."
                    )
                    return "", False
                return text, True
            except Exception as e:
                logger.error(f"PDF processing error for {filename}: {str(e)}", exc_info=True)
                return "", False
        else:
            # Process text file
            try:
                text = file_content.decode("utf-8").strip()
                if not text:
                    logger.error(f"File {filename} is empty.")
                    return "", False
                return text, True
            except Exception as e:
                logger.error(f"Text file processing error for {filename}: {str(e)}", exc_info=True)
                return "", False

    except Exception as e:
        logger.error(f"File processing error for {filename}: {str(e)}", exc_info=True)
        return "", False
