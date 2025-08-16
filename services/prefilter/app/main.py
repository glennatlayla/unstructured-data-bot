from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

app = FastAPI(title="Prefilter Service", version="1.0.0")

@app.get("/healthz")
async def health_check():
    return JSONResponse(
        content={
            "status": "ok",
            "service": "prefilter",
            "version": "1.0.0"
        },
        status_code=200
    )

@app.get("/")
async def root():
    return {"message": "Prefilter Service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8084)
