from fastapi import FastAPI
from app.api.floorplan import router as floorplan_router

app = FastAPI(
    title="Floor Plan Intelligence System",
    version="1.0.0",
    description="AI-powered floor plan analysis with Vastu compliance"
)

app.include_router(floorplan_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Floor Plan Intelligence System"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
# Reviewed
