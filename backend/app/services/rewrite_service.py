import json
import re
import uuid
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.llm_service import stream_llm
from app.services.card_service import consume, get_card
from app.models.rewrite import RewriteJob
from app.utils.prompts import ENHANCE_ROUND1, POLISH_EN, POLISH_ZH


def count_words(text: str, lang: str) -> int:
    cn = len(re.findall(r"[一-鿿㐀-䶿]", text))
    en = len(re.findall(r"[a-zA-Z]+", text))
    return cn + en


async def rewrite_stream(
    db: AsyncSession,
    card_key: str,
    mode: str,
    lang: str,
    input_text: str,
) -> AsyncGenerator[str, None]:
    if not input_text.strip():
        yield f"event: error\ndata: {json.dumps({'code': 'EMPTY_INPUT', 'message': '请输入文本'})}\n\n"
        return

    card = await get_card(db, card_key)
    if not card:
        yield f"event: error\ndata: {json.dumps({'code': 'INVALID_CARD', 'message': '兑换码无效'})}\n\n"
        return
    if not card.is_active:
        yield f"event: error\ndata: {json.dumps({'code': 'CARD_FROZEN', 'message': '兑换码已失效'})}\n\n"
        return
    if card.usage_count >= card.usage_limit:
        yield f"event: error\ndata: {json.dumps({'code': 'LIMIT_REACHED', 'message': f'次数已用完（{card.usage_count}/{card.usage_limit}），请联系购买'})}\n\n"
        return

    wc = count_words(input_text, lang)
    job_id = str(uuid.uuid4())

    yield f"event: meta\ndata: {json.dumps({'job_id': job_id, 'word_count': wc, 'mode': mode})}\n\n"

    output_text = ""
    try:
        if mode == "polish":
            prompt = POLISH_ZH if lang == "zh" else POLISH_EN
            async for chunk in stream_llm(prompt, input_text, 0.3):
                output_text += chunk
                yield f"event: chunk\ndata: {json.dumps({'text': chunk})}\n\n"
        elif mode == "enhance":
            yield f"event: meta\ndata: {json.dumps({'phase': 'round1', 'message': '表达层改写中...'})}\n\n"
            async for chunk in stream_llm(ENHANCE_ROUND1, input_text, 0.6):
                output_text += chunk
                yield f"event: chunk\ndata: {json.dumps({'text': chunk, 'phase': 'round1'})}\n\n"

        # Consume usage + save history on success
        await consume(db, card.id)
        job = RewriteJob(
            id=uuid.UUID(job_id), card_key_id=card.id, mode=mode,
            source_language=lang, input_text=input_text,
            output_text=output_text, word_count=wc, status="completed",
        )
        db.add(job)
        await db.commit()

        remaining = max(0, card.usage_limit - card.usage_count - 1)
        yield f"event: done\ndata: {json.dumps({'job_id': job_id, 'total_words': wc, 'remaining': remaining})}\n\n"
    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'code': 'LLM_ERROR', 'message': str(e)})}\n\n"
