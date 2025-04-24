from fastapi import APIRouter, HTTPException

from models.schemas import ChronologyRequest, ChronologyResponse
from src.chronology_generator import generate_chronology_table
from src.llm_processor import LLMProcessor

router = APIRouter(prefix="/chronology", tags=["chronology"])


@router.post("/generate", response_model=ChronologyResponse)
async def generate_chronology(request: ChronologyRequest):
    try:
        # Initialize LLM processor
        processor = LLMProcessor()

        all_events = []

        # Process each document
        for text, doc_name in zip(request.documents_text, request.document_names):
            if not text.strip():
                continue

            # Extract events
            events = await processor.extract_events(text, doc_name)
            if events:
                all_events.extend(events)

        if not all_events:
            raise HTTPException(
                status_code=400, detail="No events could be extracted from any of the documents."
            )

        # Create chronology
        chronology = await processor.create_chronology(all_events, request.case_description)

        # Format chronology as markdown
        markdown_output = processor.format_chronology(chronology)

        return ChronologyResponse(events=all_events, markdown_output=markdown_output)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred while processing the documents: {str(e)}"
        )
