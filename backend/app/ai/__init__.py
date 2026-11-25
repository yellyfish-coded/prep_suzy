from app.ai.base import LLMClient, SpeechClient
from app.ai.fake import FakeLLMClient, FakeSpeechClient
from app.ai.heuristic import HeuristicLLMClient


def get_llm_client() -> LLMClient:
    # Free keyword-based reader for now. Swap for a real model in Phase 4.
    return HeuristicLLMClient()


def get_speech_client() -> SpeechClient:
    return FakeSpeechClient()   # swap in Phase 8


__all__ = ["FakeLLMClient", "FakeSpeechClient", "HeuristicLLMClient", "get_llm_client", "get_speech_client"]