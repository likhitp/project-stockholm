# Case Chronology Tool

A Streamlit-based application that helps legal professionals automatically extract and organize case events in chronological order from various document types.

## Features

- Upload multiple documents (PDF, text files)
- Extract text content and events automatically
- Generate chronological event timelines with AI analysis
- Download results in markdown format
- Comprehensive error handling and validation

## Local Setup

1. Clone the repository
2. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```
GOOGLE_API_KEY=your_gemini_api_key_here
HELICONE_API_KEY=your_helicone_api_key_here
```

## Running Locally

1. Activate the virtual environment:
```bash
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Deployment

### Streamlit Cloud (Recommended)
1. Push your code to GitHub
2. Visit [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Add the required environment variables:
   - GOOGLE_API_KEY
   - HELICONE_API_KEY
5. Deploy

### Alternative Deployment Options
- Heroku
- Azure App Service
- Google Cloud Run

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

## Usage

1. Upload your case documents using the file upload interface
2. Enter a brief description of the case
3. Click "Generate Chronology" to process the documents
4. Review the generated chronology
5. Download the chronology in markdown format

## Dependencies

- streamlit==1.32.0 (UI framework)
- google-generativeai==0.3.2 (Gemini API)
- python-dotenv==1.0.1 (Environment management)
- helicone==1.0.13 (API monitoring)
- PyPDF2==3.0.1 (PDF processing)
- fpdf2==2.7.8 (PDF generation)
- Pillow==10.2.0 (Image processing)
- dateparser==1.1.8 (Date parsing)

## Note

This is version 1.0 of the Case Chronology Tool. OCR functionality for scanned documents will be implemented in future updates. 