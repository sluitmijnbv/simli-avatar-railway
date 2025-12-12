import os
import logging
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    WorkerType,
    cli,
)

from livekit.plugins import openai, simli

load_dotenv()
logger = logging.getLogger("simli-avatar")
logger.setLevel(logging.INFO)


async def entrypoint(ctx: JobContext):
    """
    This is the worker entrypoint.
    It starts:
    - LiveKit agent session
    - OpenAI Realtime model
    - Simli avatar session
    """

    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model="gpt-4o-realtime-preview",
            voice="alloy"
        )
    )

    simli_api_key = os.getenv("SIMLI_API_KEY")
    simli_face_id = os.getenv("SIMLI_FACE_ID")

    simli_avatar = simli.AvatarSession(
        simli_config=simli.SimliConfig(
            api_key=simli_api_key,
            face_id=simli_face_id
        )
    )

    # Start avatar session
    await simli_avatar.start(session, room=ctx.room)

    # Start OpenAI agent logic
    await session.start(
        agent=Agent(
            instructions="You are a friendly avatar. Respond with clear, short, helpful answers."
        ),
        room=ctx.room,
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            worker_type=WorkerType.ROOM
        )
    )
