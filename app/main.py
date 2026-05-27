import os
import logging
import redis
import asyncpg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

# ── Logging Setup ──────────────────────────────────────────────────────────────
# Logs go to stdout so Docker can capture them with `docker logs`
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── App Init ───────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Webvory DevOps Assignment API",
    description="Production-ready FastAPI with PostgreSQL, Redis, NGINX",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DB & Cache Connections ─────────────────────────────────────────────────────
DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/appdb")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

db_pool = None
redis_client = None


@app.on_event("startup")
async def startup():
    global db_pool, redis_client
    logger.info("🚀 Starting up application...")
    try:
        db_pool = await asyncpg.create_pool(DB_URL)
        await db_pool.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        logger.info("✅ PostgreSQL connected")
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")

    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")


@app.on_event("shutdown")
async def shutdown():
    if db_pool:
        await db_pool.close()
    logger.info("🛑 Application shut down")


# ── Models ─────────────────────────────────────────────────────────────────────
class MessageCreate(BaseModel):
    content: str


# ── Routes ─────────────────────────────────────────────────────────────────────

# Health check — this is what NGINX and CI/CD use to verify the app is alive
@app.get("/health")
async def health_check():
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "postgres": "unknown",
        "redis": "unknown",
    }
    try:
        await db_pool.fetchval("SELECT 1")
        status["postgres"] = "connected"
    except Exception:
        status["postgres"] = "disconnected"
        status["status"] = "degraded"

    try:
        redis_client.ping()
        status["redis"] = "connected"
    except Exception:
        status["redis"] = "disconnected"
        status["status"] = "degraded"

    logger.info(f"Health check: {status['status']}")
    return status


@app.get("/")
async def root():
    return {
        "message": "Webvory DevOps Assignment — API is running!",
        "docs": "/docs",
        "health": "/health",
    }


@app.post("/messages")
async def create_message(msg: MessageCreate):
    try:
        # Save to PostgreSQL
        row = await db_pool.fetchrow(
            "INSERT INTO messages (content) VALUES ($1) RETURNING id, content, created_at",
            msg.content,
        )
        # Cache latest message count in Redis
        redis_client.incr("message_count")
        logger.info(f"New message created: id={row['id']}")
        return {"id": row["id"], "content": row["content"], "created_at": str(row["created_at"])}
    except Exception as e:
        logger.error(f"Error creating message: {e}")
        raise HTTPException(status_code=500, detail="Could not save message")


@app.get("/messages")
async def get_messages():
    try:
        # Try Redis cache first
        cached_count = redis_client.get("message_count")
        rows = await db_pool.fetch("SELECT * FROM messages ORDER BY created_at DESC LIMIT 50")
        return {
            "count": cached_count or len(rows),
            "messages": [dict(r) for r in rows],
        }
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch messages")
