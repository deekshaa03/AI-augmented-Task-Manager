import os
import httpx
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.ai/v1/models/groq-1o/outputs"  # adjust if different

async def groq_generate(prompt: str, max_tokens: int = 200):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "input": prompt,
        "max_output_tokens": max_tokens
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(GROQ_API_URL, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        # Interpret the returned structure — this depends on their API; here we assume text at some path.
        # Example: return data["outputs"][0]["content"][0]["text"]
        # You may need to adapt after checking Groq docs.
        return data
