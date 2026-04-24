# llm/tts.py
from openai import AsyncOpenAI
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def text_to_speech(text, output_path="daily_report.mp3"):
    response = await client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=text
    )
    response.stream_to_file(output_path)
    return output_path