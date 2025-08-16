from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

app = FastAPI(title="Enhanced AI Pipeline", version="2.0.0")

@app.get("/healthz")
async def health_check():
    return JSONResponse(
        content={
            "status": "ok",
            "service": "enhanced-ai-pipeline",
            "version": "2.0.0",
            "features": [
                "hierarchical_metadata",
                "intelligent_chunking", 
                "enhanced_summarization",
                "advanced_classification",
                "multi_level_caching"
            ],
            "mode": "development",
            "note": "AI dependencies commented out for local testing"
        },
        status_code=200
    )

@app.get("/")
async def root():
    return {"message": "Enhanced AI Pipeline Service (Development Mode)"}

@app.get("/features")
async def get_features():
    return {
        "available_features": [
            "basic_endpoints",
            "health_checks",
            "service_status"
        ],
        "production_features": [
            "langchain_integration",
            "azure_openai",
            "intelligent_chunking",
            "enhanced_summarization",
            "advanced_classification"
        ],
        "status": "development_mode"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085)
