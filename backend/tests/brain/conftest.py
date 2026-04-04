"""
Brain test fixtures.

Injects a lightweight sentence_transformers stub into sys.modules so that
tests can run in CI environments where the real package is not installed.
The stub is only registered when sentence_transformers is absent; it does not
shadow a real installation.
"""

import sys
import types


def _make_sentence_transformers_stub() -> types.ModuleType:
    """Build a minimal sentence_transformers module with a SentenceTransformer stub."""

    class _FakeSentenceTransformer:
        """Minimal SentenceTransformer that returns constant-dimension embeddings."""

        def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
            self._model_name = model_name

        def encode(self, texts, convert_to_numpy: bool = True):
            """Return a list of fixed-length float vectors (one per text)."""
            return [[0.1, 0.2, 0.3, 0.4, 0.5] for _ in texts]

    stub = types.ModuleType("sentence_transformers")
    stub.SentenceTransformer = _FakeSentenceTransformer
    return stub


# Register the stub once, at import time, only when the real package is absent.
if "sentence_transformers" not in sys.modules:
    sys.modules["sentence_transformers"] = _make_sentence_transformers_stub()
