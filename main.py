import os
import time
import jwt
import asyncio
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from livekit.agents import (
    Agent,
    AgentSession,
)
from livekit.plugins import openai, simli

load_dotenv()

logger = logging.getLogger("simli-backend")
logger.setLevel(logging.INFO)

# ENV
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

SIMLI_API_KEY = os.getenv("SIMLI_API_KEY")
SIMLI_FACE_ID = os.getenv("SIMLI_FACE_ID")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# FastAPI app
app = FastAPI()

# CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Token endpoint
@app.get("/token")
def create_token(identity: str = "user"):
    now = int(time.time())
    payload = {
        "iss": LIVEKIT_API_KEY,
        "sub": identity,
        "nbf": now,
        "exp": now + 3600,
        "video": {"roomJoin": True, "room": "simli-room"},
    }
    token = jwt.encode(payload, LIVEKIT_API_SECRET, algorithm="HS256")
    return {"token": token, "url": LIVEKIT_URL}


# Start avatar worker when server boots
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_worker())


async def run_worker():
    logger.info("Starting Simli worker...")

    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            api_key=OPENAI_API_KEY,
            model="gpt-4o-realtime-preview",
            voice="alloy"
        )
    )

    simli_avatar = simli.AvatarSession(
        simli_config=simli.SimliConfig(
            api_key=SIMLI_API_KEY,
            face_id=SIMLI_FACE_ID
        )
    )

    # Dummy context since Railway runs this statically
    class DummyRoom:
        name = "simli-room"

    await simli_avatar.start(session, room=DummyRoom())
    await session.start(
        agent=Agent(
            instructions="Je bent een vriendelijke avatar. Begroet automatisch."
        ),
        room=DummyRoom()
    )
