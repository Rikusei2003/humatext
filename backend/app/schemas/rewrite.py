from pydantic import BaseModel


class RewriteRequest(BaseModel):
    card_key: str
    mode: str  # "polish" or "enhance"
    source_language: str = "zh"
    input_text: str
