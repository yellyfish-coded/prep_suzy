import logging

from pydantic import ValidationError

from app.ai import get_llm_client
from app.schemas.resume import ResumeAnalysis
from app.services.redaction import redact

log = logging.getLogger(__name__)

_REQUIRED_KEY = {
    "skills": "name",
    "projects": "name",
    "experiences": "company",
    "education": "institution",
}


class AnalysisError(Exception):
    pass


def _drop_blank(raw: dict) -> dict:
    cleaned = dict(raw)
    for key, required in _REQUIRED_KEY.items():
        items = raw.get(key) or []
        cleaned[key] = [i for i in items if isinstance(i, dict) and str(i.get(required, "")).strip()]
    return cleaned


def analyze(resume_text: str) -> ResumeAnalysis:
    llm = get_llm_client()
    safe_text = redact(resume_text)
    last_error: Exception | None = None

    for attempt in range(2):  # one retry on invalid model output
        try:
            raw = llm.extract_resume(safe_text)
            result = ResumeAnalysis.model_validate(_drop_blank(raw))
            break
        except (ValidationError, ValueError, TypeError) as exc:
            last_error = exc
            log.warning("Resume analysis output invalid (attempt %s)", attempt + 1)
    else:
        raise AnalysisError("Model output was invalid") from last_error

    seen: set[str] = set()
    unique = []
    for skill in result.skills:
        key = skill.name.lower()
        if key not in seen:
            seen.add(key)
            unique.append(skill)
    result.skills = unique
    return result