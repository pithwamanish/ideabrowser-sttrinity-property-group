from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Idea Board API", description="API for the Idea Board application")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class Idea(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str = Field(..., max_length=280)
    upvotes: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class IdeaCreate(BaseModel):
    text: str = Field(..., max_length=280, min_length=1)

class IdeaResponse(BaseModel):
    id: str
    text: str
    upvotes: int
    created_at: datetime

# Helper function to prepare data for MongoDB
def prepare_for_mongo(data):
    if isinstance(data.get('created_at'), datetime):
        data['created_at'] = data['created_at'].isoformat()
    return data

def parse_from_mongo(item):
    if isinstance(item.get('created_at'), str):
        item['created_at'] = datetime.fromisoformat(item['created_at'])
    return item

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Idea Board API is running!"}

# Existing status check endpoints
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

# New Idea Board endpoints
@api_router.get("/ideas", response_model=List[IdeaResponse])
async def get_ideas():
    """Get all ideas sorted by upvotes (descending) then by creation time (newest first)"""
    ideas = await db.ideas.find().sort([("upvotes", -1), ("created_at", -1)]).to_list(1000)
    return [IdeaResponse(**parse_from_mongo(idea)) for idea in ideas]

@api_router.post("/ideas", response_model=IdeaResponse)
async def create_idea(idea_input: IdeaCreate):
    """Create a new idea"""
    idea_dict = idea_input.dict()
    idea_obj = Idea(**idea_dict)
    idea_data = prepare_for_mongo(idea_obj.dict())
    await db.ideas.insert_one(idea_data)
    return IdeaResponse(**idea_obj.dict())

@api_router.patch("/ideas/{idea_id}/upvote", response_model=IdeaResponse)
async def upvote_idea(idea_id: str):
    """Increment the upvote count for an idea"""
    # Find and update the idea
    result = await db.ideas.find_one_and_update(
        {"id": idea_id},
        {"$inc": {"upvotes": 1}},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    return IdeaResponse(**parse_from_mongo(result))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
