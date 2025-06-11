from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent))

# Import payment routes and database utilities
from routes.payments import router as payments_router
from database import create_indexes, close_database_connection

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Meta Generation Tool API", description="API with Dodo Payments integration")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Meta Generation Tool API with Dodo Payments"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Health check endpoint for payment services
@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "dodo_payments": {
            "api_key_configured": bool(os.getenv("DODO_PAYMENTS_API_KEY")),
            "webhook_secret_configured": bool(os.getenv("DODO_PAYMENTS_WEBHOOK_SECRET")),
            "mode": os.getenv("DODO_PAYMENTS_MODE", "test")
        },
        "database": {
            "connected": True,
            "name": os.environ.get('DB_NAME')
        }
    }

# Include the payment router
app.include_router(payments_router)

# Include the main API router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize database indexes on startup"""
    try:
        await create_indexes()
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating database indexes: {str(e)}")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Clean up database connections on shutdown"""
    try:
        await close_database_connection()
        client.close()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {str(e)}")
