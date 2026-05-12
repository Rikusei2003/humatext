from openai import AsyncOpenAI

from app.config import settings

client = AsyncOpenAI(api_key=settings.LLM_API_KEY or "sk-placeholder", base_url=settings.LLM_BASE_URL)


async def stream_llm(system_prompt: str, user_text: str, temperature: float = 0.3):
    """Yield text chunks from LLM streaming response."""
    stream = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        temperature=temperature,
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


async def complete_llm(system_prompt: str, user_text: str, temperature: float = 0.3) -> str:
    """Non-streaming completion, returns full text."""
    response = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        temperature=temperature,
        stream=False,
    )
    return response.choices[0].message.content or ""
