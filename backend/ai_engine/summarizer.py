"""Text summarization with a BART model via transformers.

The first call may download model weights. To avoid import-time overhead,
the pipeline is instantiated lazily on first use.
"""

from typing import Optional

from transformers import pipeline

_summarizer = None  # lazy singleton


def _get_pipeline():
    global _summarizer
    if _summarizer is None:
        _summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    return _summarizer


def summarize_text(text: str, max_length: int = 120, min_length: int = 30) -> str:
    """Summarize input text and return the summary string."""
    if not text or not text.strip():
        raise ValueError("Empty text provided for summarization")
    summarizer = _get_pipeline()
    result = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return result[0]["summary_text"]

