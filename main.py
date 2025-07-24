from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.parse_schedule import router as schedule_router

app = FastAPI(
    title="CPD-3-AI",
    description="AI Payment Schedule Generator for CPD System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(schedule_router)

if __name__ == "__main__":
    print("🧪 Testing imports...")
    print("")
    print("🧪 Testing imports...")
    import uvicorn
    print("✅ All imports successful")
    print("")
    print("")
    print("🚀 Starting server...")
    print("Hi")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

    