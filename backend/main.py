from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chronology

app = FastAPI(title="Project Stockholm API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chronology.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 