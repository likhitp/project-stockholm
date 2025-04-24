# Project Stockholm

A powerful tool for generating chronologies from legal documents using AI. This project uses Google's Gemini AI to extract events from documents and create comprehensive chronological summaries.

## Features

- Upload multiple documents (PDF, text files)
- Extract text content and events automatically
- Generate chronological event timelines with AI analysis
- Download results in markdown format
- Comprehensive error handling and validation

## Note

This project is designed to assist legal professionals in creating chronologies but should not be relied upon as the sole source of truth. Always verify the generated chronologies against the source documents.

## Usage

1. Upload one or more documents (PDF or text files)
2. Provide a brief case description (optional but recommended)
3. Click "Generate Chronology"
4. Review the generated chronology
5. Download the chronology in Markdown format

## Project Structure

```
project-stockholm/
├── backend/              # FastAPI backend service
│   ├── src/             # Core business logic
│   ├── routers/         # API endpoints
│   ├── models/          # Pydantic models
│   ├── utils/           # Utility functions
│   └── tests/           # Backend tests
├── frontend/            # Streamlit frontend service
│   ├── main.py         # Streamlit application
│   └── utils/          # Frontend utilities
└── docker-compose.yml   # Docker compose configuration
```

## Prerequisites

- Docker and Docker Compose
- Google Gemini API key (get it from [Google AI Studio](https://makersuite.google.com/app/apikey))

## Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/project-stockholm.git
   cd project-stockholm
   ```

2. Create your environment file:
   ```bash
   cp .env.template .env
   ```

3. Edit `.env` and add your API keys:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   HELICONE_API_KEY=your_helicone_api_key_here  # Optional
   ```

4. Build and run the services:
   ```bash
   # Regular mode (see logs in terminal)
   docker compose up --build

   # Detached mode (run in background)
   docker compose up --build -d

   # To view logs in detached mode
   docker compose logs -f

   # To stop the services
   docker compose down
   ```

5. Access the application:
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development

The project uses Poetry for dependency management in both frontend and backend services. Key technologies:

- Backend:
  - FastAPI for the API framework
  - Pydantic for data validation
  - Google Generative AI for LLM processing
  - PyPDF2 for PDF processing

- Frontend:
  - Streamlit for the user interface
  - Requests for API communication

## Documentation Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Google Gemini AI Documentation](https://ai.google.dev/docs)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Environment Variables

Required environment variables:
- `GOOGLE_API_KEY`: Gemini API key for LLM capabilities
- `HELICONE_API_KEY`: Helicone API key for monitoring

## Monitoring and Analytics

The application uses Helicone for monitoring API usage and performance:
1. Visit [Helicone Dashboard](https://www.helicone.ai)
2. Log in to view:
   - API usage metrics
   - Error rates
   - Response times
   - Cost tracking



## Note

This is version 1.0 of the Case Chronology Tool. OCR functionality for scanned documents will be implemented in future updates. 