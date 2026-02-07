"""
Financial Compliance Auditor - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import audit, history, files, health

app = FastAPI(
    title="Financial Compliance Auditor API",
    description="AI-powered compliance auditor for financial documents",
    version="1.0.0"
)

# CORS - Allow all origins for hackathon
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(audit.router, prefix="/api", tags=["Audit"])
app.include_router(history.router, prefix="/api", tags=["History"])
app.include_router(files.router, prefix="/api", tags=["Files"])


@app.get("/")
async def root():
    return {"message": "Financial Compliance Auditor API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
