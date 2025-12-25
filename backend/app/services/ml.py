# Lightweight ML service using Hugging Face pipeline
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from transformers import pipeline
except Exception:  # transformers is optional at import time
    pipeline = None
    logger.warning("transformers is not installed; using fallback sentiment stub.")

_classifier = None


def get_classifier():
    """
    Lazily create and cache the sentiment classifier.
    Uses a small English sentiment model by default.
    """
    global _classifier
    if _classifier is not None:
        return _classifier

    if pipeline is None:
        raise RuntimeError(
            "transformers is not available. Install it or replace analyze_sentiment with a stub."
        )

    # Small, widely used sentiment model
    model_name = "distilbert-base-uncased-finetuned-sst-2-english"
    logger.info("Loading sentiment model: %s", model_name)
    _classifier = pipeline(settings.HF_TASK, model=model_name)
    return _classifier


def analyze_sentiment(text: str) -> tuple[str, str]:
    """
    Run sentiment analysis and return (label, score_str).
    If something goes wrong, fall back to NEUTRAL.
    """
    try:
        clf = get_classifier()
        res = clf(text)[0]
        label = res.get("label", "NEUTRAL")
        score = f'{res.get("score", 0):.4f}'
        return label, score
    except Exception as exc:
        logger.error("Sentiment analysis failed: %s", exc, exc_info=True)
        return "NEUTRAL", "0.0000"
