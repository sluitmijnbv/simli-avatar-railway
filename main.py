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
    JobContext,
    WorkerOptions,
    WorkerType,
    cli,
)
from livekit.plugins import openai, simli

# ----------------------------------
# Load environment
# ----------------------------------
load_dotenv()
logger = logging.getLogger("simli-backend")
logger.setLevel(logging.INFO)

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

SIMLI_API_KEY = os.getenv("SIMLI_API_KEY")
SIMLI_FACE_ID = os.getenv("SIMLI_FACE_ID")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# ----------------------------------
# FastAPI app
# ----------------------------------
app = FastAPI()

# -------------------------------
# CORS FIX — ALLOW ANY ORIGIN
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # ← FIX: laat file:// en elke website toe
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# TOKEN ENDPOINT — Browser calls this to join room
# -------------------------------------------------
@app.get("/token")
def create_token(identity: str = "web-user"):
    now = int(time.time())

    payload = {
        "iss": LIVEKIT_API_KEY,
        "sub": identity,
        "nbf": now,
        "exp": now + 3600,
        "video": {
            "roomJoin": True,
            "room": "simli-room"
        }
    }

    token = jwt.encode(payload, LIVEKIT_API_SECRET, algorithm="HS256")

    return {"token": token, "url": LIVEKIT_URL}


# ----------------------------------------
# BACKGROUND TASK (LiveKit Worker Startup)
# ----------------------------------------
@app.on_event("startup")
async def on_startup():
    asyncio.create_task(start_worker())


async def start_worker():
    logger.info("Starting LiveKit + Simli worker...")

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

    # Fake room context — WorkerType.ROOM auto-joins actual room
    class DummyRoom:
        name = "simli-room"

    ctx = JobContext(room=DummyRoom())

    await simli_avatar.start(session, room=ctx.room)

    await session.start(
        agent=Agent(
            instructions="Je bent een vriendelijke AI avatar. "
                         "Begroet automatisch de gebruiker zodra hij binnenkomt."
        ),
        room=ctx.room,
    )


# -------------------------------------------------------
# CLI WORKER RUNNER — Railway uses this in the Procfile
# -------------------------------------------------------
if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=start_worker,
            worker_type=WorkerType.ROOM
        )
    )
