from app.services import ml

def test_analyze_sentiment_fallback(monkeypatch):
    def boom():
        raise RuntimeError("no model")
    monkeypatch.setattr(ml, "get_classifier", boom)

    label, score = ml.analyze_sentiment("hello")
    assert label == "NEUTRAL"
    assert score == "0.0000"

