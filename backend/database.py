"""
Database configuration and utilities for Dodo Payments
"""
import os
from typing import Dict
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

# Global database client
_db_client: AsyncIOMotorClient = None
_database = None

async def get_database_client() -> AsyncIOMotorClient:
    """Get or create MongoDB client"""
    global _db_client
    if _db_client is None:
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        _db_client = AsyncIOMotorClient(mongo_url)
    return _db_client

async def get_database():
    """Get database instance"""
    global _database
    if _database is None:
        client = await get_database_client()
        db_name = os.getenv("DB_NAME", "test_database")
        _database = client[db_name]
    return _database

async def get_database_collections() -> Dict[str, AsyncIOMotorCollection]:
    """Get all collections needed for payments"""
    db = await get_database()
    return {
        "payments": db.payments,
        "subscriptions": db.subscriptions,
        "customers": db.customers,
        "webhook_events": db.webhook_events
    }

async def create_indexes():
    """Create necessary indexes for payment collections"""
    db = await get_database()
    
    # Payment indexes
    await db.payments.create_index("payment_id", unique=True)
    await db.payments.create_index("user_id")
    await db.payments.create_index("customer_id")
    await db.payments.create_index("status")
    await db.payments.create_index("created_at")
    
    # Subscription indexes
    await db.subscriptions.create_index("subscription_id", unique=True)
    await db.subscriptions.create_index("user_id")
    await db.subscriptions.create_index("customer_id")
    await db.subscriptions.create_index("status")
    await db.subscriptions.create_index("created_at")
    
    # Webhook events indexes
    await db.webhook_events.create_index("event_id", unique=True)
    await db.webhook_events.create_index("type")
    await db.webhook_events.create_index("created_at")

async def close_database_connection():
    """Close database connection"""
    global _db_client, _database
    if _db_client:
        _db_client.close()
        _db_client = None
        _database = None
