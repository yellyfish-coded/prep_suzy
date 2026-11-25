import re

from app.ai.fake import FakeLLMClient

SKILL_CATALOG: dict[str, list[str]] = {
    "language": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "PHP", "Ruby", "Kotlin",
        "Swift", "SQL", "MATLAB", "Dart", "Rust", "Bash",
    ],
    "web": [
        "React", "Next.js", "Vue", "Angular", "Node.js", "Express", "Django", "Flask",
        "FastAPI", "Spring Boot", "HTML", "CSS", "Tailwind", "REST", "GraphQL", "Laravel",
    ],
    "database": [
        "PostgreSQL", "MySQL", "MongoDB", "SQLite", "Redis", "Oracle", "Firebase", "Supabase",
    ],
    "tools": [
        "Git", "GitHub", "Docker", "Kubernetes", "Linux", "AWS", "Azure", "GCP", "Jenkins",
        "CI/CD", "Postman", "Jira", "Figma",
    ],
    "data": [
        "Pandas", "NumPy", "TensorFlow", "PyTorch", "Scikit-learn", "Machine Learning",
        "Deep Learning", "NLP", "Power BI", "Tableau", "Excel",
    ],
    "concepts": [
        "Data Structures", "Algorithms", "OOP", "Object-Oriented Programming",
        "Operating Systems", "Computer Networks", "Agile", "Scrum", "Unit Testing",
        "Microservices",
    ],
}

# alternative spellings -> catalogue name
ALIASES = {
    "Postgres": "PostgreSQL", "Nodejs": "Node.js", "NodeJS": "Node.js", "ReactJS": "React",
    "JS": "JavaScript", "Mongo": "MongoDB", "K8s": "Kubernetes", "sklearn": "Scikit-learn",
    "Tailwind CSS": "Tailwind",
}

HEADINGS = {
    "projects": {"projects", "project", "academic projects", "personal projects", "key projects"},
    "experience": {
        "experience", "work experience", "professional experience", "internships",
        "internship", "employment",
    },
    "education": {"education", "academic background", "qualifications"},
    "other": {
        "skills", "technical skills", "summary", "profile", "objective", "certifications",
        "achievements", "awards", "languages", "interests", "references",
    },
}

DEGREE_WORDS = (
    "Bachelor", "BSc", "B.Sc", "B.Tech", "BTech", "Master", "MSc", "M.Sc", "M.Tech",
    "MBA", "PhD", "Diploma", "Associate",
)
BULLETS = ("-", "•", "*", "–", "·", "▪")


def _pattern(name: str) -> re.Pattern:
    return re.compile(rf"(?<![A-Za-z0-9+#]){re.escape(name)}(?![A-Za-z0-9+#])")


_CATEGORY = {n: c for c, names in SKILL_CATALOG.items() for n in names}
_PATTERNS: list[tuple[str, str, re.Pattern]] = [
    (canonical, _CATEGORY[canonical], _pattern(canonical)) for canonical in _CATEGORY
] + [(canonical, _CATEGORY[canonical], _pattern(alias)) for alias, canonical in ALIASES.items()]


def _find_skills(text: str) -> list[tuple[str, str, str]]:
    found: dict[str, tuple[str, str]] = {}
    lines = text.splitlines()
    for name, category, pattern in _PATTERNS:
        if name in found or not pattern.search(text):
            continue
        evidence = next((ln.strip() for ln in lines if pattern.search(ln)), "")
        found[name] = (category, evidence[:200])
    return [(n, c, e) for n, (c, e) in found.items()]


def _heading_key(line: str) -> str | None:
    token = line.strip().strip(":").strip().lower()
    for key, names in HEADINGS.items():
        if token in names:
            return key
    return None


def _split_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"projects": [], "experience": [], "education": []}
    current: str | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        key = _heading_key(line)
        if key is not None:
            current = key if key in sections else None
            continue
        if current:
            sections[current].append(line)
    return sections


def _blocks(lines: list[str]) -> list[list[str]]:
    blocks: list[list[str]] = []
    for line in lines:
        is_bullet = line.startswith(BULLETS)
        if not is_bullet and len(line) <= 100:
            blocks.append([line, ""])
        elif blocks:
            text = line.lstrip("-•*–·▪ ").strip()
            blocks[-1][1] = (blocks[-1][1] + " " + text).strip()
    return blocks


class HeuristicLLMClient(FakeLLMClient):
    """Free, rule-based resume reader. Replace with a real model later."""

    def extract_resume(self, resume_text: str) -> dict:
        skills = [
            {"name": n, "category": c, "evidence": e} for n, c, e in _find_skills(resume_text)
        ][:60]
        sections = _split_sections(resume_text)

        projects = []
        for title, desc in _blocks(sections["projects"])[:15]:
            tech = ", ".join(n for n, _, _ in _find_skills(f"{title} {desc}"))
            projects.append(
                {"name": title[:150], "description": desc[:1500], "technologies": tech[:300]}
            )

        experiences = []
        for title, desc in _blocks(sections["experience"])[:15]:
            if " at " in title:
                role, company = title.split(" at ", 1)
            else:
                role, company = "", title
            experiences.append(
                {"company": company.strip()[:150], "role": role.strip()[:150], "description": desc[:1500]}
            )

        education = []
        for line in sections["education"][:10]:
            if line.startswith(BULLETS):
                continue
            degree = next((w for w in DEGREE_WORDS if w in line), "")
            education.append({"institution": line[:150], "degree": degree, "field": ""})

        return {
            "skills": skills,
            "projects": projects,
            "experiences": experiences,
            "education": education,
        }