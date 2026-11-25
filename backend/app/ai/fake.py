class FakeLLMClient:
    def extract_resume(self, resume_text: str) -> dict:
        return {
            "skills": [{"name": "Python", "category": "language", "evidence": "Fake data"}],
            "projects": [],
            "experiences": [],
            "education": [],
        }

    def generate_questions(self, request: dict) -> list[dict]:
        count = request.get("count", 3)
        return [
            {
                "question": f"Fake question {i + 1} about {request.get('topic', 'Python')}?",
                "topic": request.get("topic", "Python"),
                "difficulty": "easy",
                "expected_points": ["point A", "point B"],
                "model_answer": "A sample model answer.",
            }
            for i in range(count)
        ]

    def evaluate_answer(self, request: dict) -> dict:
        return {"score": 3, "covered": ["point A"], "missing": ["point B"], "feedback": "Fake feedback."}


class FakeSpeechClient:
    def transcribe(self, audio_bytes: bytes, language: str = "en") -> str:
        return "This is a fake transcript."