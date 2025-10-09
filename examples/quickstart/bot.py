#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Pipecat Quickstart Example.

The example runs a simple voice AI bot that you can connect to using your
browser and speak with it. You can also deploy this bot to Pipecat Cloud.

Required AI services:
- Deepgram (Speech-to-Text)
- OpenAI (LLM)
- Cartesia (Text-to-Speech)

Run the bot using::

    uv run bot.py
"""

import os
import time
import logging
import truststore

from dotenv import load_dotenv
from loguru import logger
from retriever import Retriever

# Proper SSL setup: use macOS keychain via truststore and clear conflicting env flags
try:
    truststore.inject_into_ssl()
    try:
        # Also patch requests to use system trust
        truststore.inject_into_requests()
    except Exception:
        pass
    # Remove env overrides that force custom/broken CA bundles or disable HTTPS verify
    for var in (
        'REQUESTS_CA_BUNDLE',
        'CURL_CA_BUNDLE',
        'PYTHONHTTPSVERIFY',
        'SSL_CERT_FILE',
        'HF_HUB_OFFLINE',
    ):
        os.environ.pop(var, None)
except Exception:
    # If truststore isn't available, continue; the venv already has it installed during setup
    pass

print("🚀 Starting Pipecat bot...")
print("⏳ Loading models and imports (20 seconds, first run only)\n")

logger.info("Loading Local Smart Turn Analyzer V3...")
from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3

logger.info("✅ Local Smart Turn Analyzer V3 loaded")
logger.info("Loading Silero VAD model...")
from pipecat.audio.vad.silero import SileroVADAnalyzer

logger.info("✅ Silero VAD model loaded")

from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import LLMRunFrame

logger.info("Loading pipeline components...")
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
# from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.kokoro.tts import KokoroTTSService
from pipecat.services.whisper.stt import WhisperSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.frames.frames import LLMRunFrame
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.daily.transport import DailyParams
from system_prompt import base_prompt, hindi_prompt

logger.info("✅ All components loaded successfully!")

load_dotenv(override=True)

# Initialize retriever
retriever = Retriever()

# Load transcripts at startup
TRANSCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "transcripts_base")
all_transcripts_text = """# Customer Support Transcripts

Below are raw customer support transcripts. Each transcript is clearly separated with markdown,
and wrapped inside triple backticks for clarity. Each has explicit **Start** and **End** markers.

---

"""

# Load transcripts if directory exists
if os.path.exists(TRANSCRIPTS_DIR):
    for fname in os.listdir(TRANSCRIPTS_DIR):
        if fname.endswith(".txt"):
            with open(os.path.join(TRANSCRIPTS_DIR, fname), "r") as f:
                transcript_text = f.read().strip()

                all_transcripts_text += f"## Transcript: `{fname}`\n"
                all_transcripts_text += f"---\n\n"
                all_transcripts_text += f"🔹 **Start of Transcript `{fname}`**\n\n"
                all_transcripts_text += f"```text\n{transcript_text}\n```\n\n"
                all_transcripts_text += f"🔹 **End of Transcript `{fname}`**\n\n"
                all_transcripts_text += f"---\n\n"

                logger.info(f"Loaded transcript: {fname}")

# Add global end marker
all_transcripts_text += "✅ **End of All Transcripts** ✅\n"


# Using enhanced system prompt approach with transcripts included


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    logger.info(f"Starting bot")

    stt = WhisperSTTService(model="base", local_files_only=False, audio_passthrough=False)
    
    # Create enhanced system prompt with transcripts
    enhanced_system_prompt = f"""{base_prompt}

Additional Context:
Call Transcripts for reference:
{all_transcripts_text}

Note: Use the above transcripts and your knowledge base to provide accurate, step-by-step assistance to Angel One customers."""
    
    llm = OpenAILLMService(
        model="openai-gpt-oss-120b-1-0",
        api_key="sk-B5L_6mUNpjpLXPDLPRNxwA",
        base_url="http://10.5.80.177:4000",
        params=OpenAILLMService.InputParams(temperature=0)
    )

    tts = KokoroTTSService()
    # tts = KokoroTTSService(lang_code = "h", voice = "hf_alpha")

    messages = [
        {
            "role": "system",
            "content": enhanced_system_prompt,
        },
    ]

    context = LLMContext(messages)
    context_aggregator = LLMContextAggregatorPair(context)

    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    pipeline = Pipeline(
        [
            transport.input(),  # Transport user input
            rtvi,  # RTVI processor
            stt,
            context_aggregator.user(),  # User responses
            llm,  # LLM with enhanced system prompt
            tts,  # TTS
            transport.output(),  # Transport bot output
            context_aggregator.assistant(),  # Assistant spoken responses
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        observers=[RTVIObserver(rtvi)],
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info(f"Client connected")
        # Kick off the conversation with a user message to satisfy the LLM requirement
        # The custom LLM processor will handle the context and retrieval
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info(f"Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)

    await runner.run(task)


async def bot(runner_args: RunnerArguments):
    """Main bot entry point for the bot starter."""

    transport_params = {
        "daily": lambda: DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
            turn_analyzer=LocalSmartTurnAnalyzerV3(),
        ),
        "webrtc": lambda: TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
            turn_analyzer=LocalSmartTurnAnalyzerV3(),
        ),
    }

    transport = await create_transport(runner_args, transport_params)

    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
