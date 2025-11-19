from functools import lru_cache
from typing import Optional

from transformers import pipeline


@lru_cache(maxsize=1)
def get_bart_summarizer():
    # Lazy-loads and caches the summarization pipeline
    return pipeline(
        task="summarization",
        model="facebook/bart-large-cnn",
        tokenizer="facebook/bart-large-cnn",
    )


def preload_summarizer() -> None:
    """Ensure the summarizer model is loaded into memory."""
    get_bart_summarizer()


def summarize_text(text: str, max_length: int = 130, min_length: int = 30) -> Optional[str]:
    if not text or not text.strip():
        return None
    summarizer = get_bart_summarizer()
    # BART has a max token/length limit; pipeline handles chunking poorly, so truncate input
    input_text = text.strip()
    if len(input_text) > 4000:
        input_text = input_text[:4000]
    result = summarizer(
        input_text,
        max_length=max_length,
        min_length=min_length,
        do_sample=False,
        clean_up_tokenization_spaces=True,
    )
    if not result:
        return None
    return result[0].get("summary_text")


