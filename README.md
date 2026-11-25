# Prep Suzy - inteview assistant for students

> **AI-Powered Technical Interview & Career Readiness Platform**  
> Tailored mock interviews, resume extraction, skill verification, and real-time practice feedback.

---

##  Project Overview

**Prep Suzy** is a full-stack platform designed to help job candidates prepare for technical interviews. It processes and validates candidate resumes, extracts verified skills and experiences through an AI analysis pipeline, and uses candidate profiles to generate targeted, role-specific interview preparation.

---

## Current Implementation Status

### Completed Features

#### 1. Backend Architecture (FastAPI & Python 3.12+)
* **Database & ORM**: PostgreSQL (hosted on **Supabase**) using **SQLAlchemy 2.0** with strict typing and **Alembic** migrations (`app/db/migrations/`).
* **Object Storage**: Resume storage via **Supabase Storage** (S3-compatible) with time-limited signed download URLs.
* **Asynchronous Task Queue**: **Celery** with **Redis** broker for background resume parsing and heavy AI analysis jobs.
* **Resume Ingestion & Processing Pipeline**:
  * **File Validation**: Strict MIME/magic number checks, max 5 MB upload limits, max page limit (10 pages), and corrupt file detection.
  * **Text Extraction**: High-fidelity text extraction supporting `.pdf` (via `PyMuPDF`) and `.docx` (via `python-docx`).
  * **PII Redaction**: Automatic scrubbing of sensitive personal identifiable information (phone numbers, personal emails, physical addresses) prior to AI processing.
  * **AI Analysis Engine**: Structured entity extraction (Technical Skills, Work Experience, Projects, Education) with category classifications and resume evidence tracking. Includes heuristic and fake AI implementations ready for LLM integration.
* **API Endpoints**:
  * `GET /health`, `GET /health/db`: System and database connectivity checks.
  * `GET /api/v1/users/me`, `PATCH /api/v1/users/me`: Candidate profile management (target role, education level, experience level).
  * `POST /api/v1/resumes`: Upload and queue resume for asynchronous processing.
  * `GET /api/v1/resumes`: List user's uploaded resumes with real-time processing status.
  * `GET /api/v1/resumes/{id}`: Detailed resume metadata and extraction warnings.
  * `GET /api/v1/resumes/{id}/analysis`: Retrieve parsed skills, projects, work experience, and education.
  * `PUT /api/v1/resumes/{id}/analysis`: Save user modifications or corrections to extracted data.
  * `POST /api/v1/resumes/{id}/confirm`: Confirm and lock extracted resume data for interview tailoring.
  * `POST /api/v1/resumes/{id}/reprocess`: Trigger background re-extraction.
  * `GET /api/v1/resumes/{id}/file-url`: Secure, expiring download link for the original resume file.
  * `DELETE /api/v1/resumes/{id}`: Cascade deletion of resume record, parsed entities, and cloud storage object.
* **Core Security & Middleware**:
  * Request correlation IDs via `X-Request-ID` middleware.
  * Cache suppression (`Cache-Control: no-store`) on private candidate data.
  * Standardized JSON error response envelope with strict error codes.
  * Safe developer authentication stub (`dev_stub`) preventing mock credentials from running in production.

#### 2. Frontend Application (Next.js 15 & React 19)
* **Framework**: Next.js App Router with TypeScript and Tailwind CSS.
* **Pages & User Flows**:
  * **Dashboard (`/`)**: Main hub displaying quick status metrics, navigation, and resume progress.
  * **Resume Hub (`/resume`)**: File upload dropzone supporting drag-and-drop, real-time status badges (`uploaded`, `processing`, `needs_review`, `completed`, `failed`), and resume deletion/reprocessing actions.
  * **Resume Review & Editor (`/resume/[id]`)**: Full breakdown view of parsed data (Skills, Work Experience, Projects, Education). Candidates can inline-edit, add new items, remove incorrect items, download the source file, and confirm verified skills.
  * **Profile Settings (`/profile`)**: Update target job role, experience level, education tier, and display name.
  * **Placeholder Modules (`/practice`, `/history`, `/settings`)**: Clean coming-soon UI for upcoming interview modules.
* **Reusable UI Components**:
  * Responsive global navigation (`Nav.tsx`) with active state tracking.
  * Color-coded status indicator (`StatusBadge.tsx`).
  * Dynamic list and item editor (`FieldList.tsx`).
  * Empty, loading, and error states (`States.tsx`).
  * Strongly-typed API client (`lib/api.ts`) with custom error handling.

#### 3. DevOps & CI/CD
* **Docker Compose**: Pre-configured multi-container orchestration for `redis`, `backend` (FastAPI), and `worker` (Celery).
* **Automated CI Workflow**: GitHub Actions pipeline (`.github/workflows/ci.yml`) validating Python code styling (`ruff check`), backend tests (`pytest`), TypeScript compilation, ESLint, and frontend production builds (`npm run build`).

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, Lucide Icons |
| **Backend** | Python 3.12+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| **Database** | PostgreSQL on Supabase (with transaction/session connection pooler) |
| **Storage** | Supabase Storage (S3-compatible bucket) |
| **Background Processing** | Celery 5.4, Redis 7 |
| **Text Extraction** | PyMuPDF (`fitz`), `python-docx` |
| **DevOps / CI** | Docker Compose, GitHub Actions |

---

## 📁 Repository Structure

```text
prep_suzy/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI (lint, test, build)
├── backend/
│   ├── alembic.ini              # Alembic migration configuration
│   ├── Dockerfile               # Backend container image definition
│   ├── requirements.txt         # Pinned Python dependencies
│   ├── app/
│   │   ├── ai/                  # AI analysis & extraction (heuristic, fake, LLM)
│   │   ├── api/v1/              # FastAPI endpoints (users, resumes)
│   │   ├── core/                # Config, dependencies, logging, error handling
│   │   ├── db/                  # SQLAlchemy models, sessions, Alembic migrations
│   │   ├── repositories/        # Database access layer
│   │   ├── schemas/             # Pydantic validation schemas
│   │   ├── services/            # Extraction, redaction, and resume business logic
│   │   ├── storage/             # Supabase object storage client
│   │   └── workers/             # Celery background tasks & application setup
│   └── tests/                   # Backend pytest suite
├── frontend/
│   ├── app/                     # Next.js App Router (pages & layouts)
│   ├── components/              # Shared UI components (Nav, StatusBadge, FieldList)
│   ├── lib/                     # Typed API client & helper utilities
│   ├── package.json             # Frontend dependencies & scripts
│   └── tsconfig.json            # TypeScript configuration
├── docker-compose.yml           # Local multi-service orchestration (Redis, API, Worker)
└── README.md                    # Project documentation
```

---

## ⚙️ Getting Started Locally

### Prerequisites
* **Python 3.12+**
* **Node.js 20+** & `npm`
* **Docker & Docker Desktop** (or local Redis instance)
* Free **[Supabase](https://supabase.com)** account (for PostgreSQL database and Storage)

---

### 1. Environment Configuration

Create a `.env` file in the root directory:

```env
# Application Environment
APP_ENV=development
AUTH_MODE=dev_stub
DEV_USER_ID=00000000-0000-0000-0000-000000000001
FRONTEND_ORIGIN=http://localhost:3000

# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql+psycopg://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres

# Supabase Storage
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_SERVICE_KEY=[YOUR_SUPABASE_SERVICE_ROLE_KEY]
SUPABASE_STORAGE_BUCKET=resumes

# Redis Broker (for Celery)
REDIS_URL=redis://localhost:6379/0
```

---

### 2. Backend Setup

```powershell
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate          # On Windows
# source venv/bin/activate       # On Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed initial dev user
python -m app.db.seed

# Start the development API server
uvicorn app.main:app --reload --port 8000
```
API Documentation will be live at: `http://localhost:8000/docs`

---

### 3. Background Worker Setup (Celery)

Ensure Redis is running (via Docker or local service):
```powershell
docker run -d -p 6379:6379 redis:7
```

In a separate terminal, start the Celery worker:
```powershell
cd backend
.\venv\Scripts\activate
celery -A app.workers.celery_app.celery worker --loglevel=info -P solo
```

---

### 4. Frontend Setup

```powershell
# Navigate to frontend
cd frontend

# Install packages
npm install

# Start Next.js development server
npm run dev
```
Open your browser at: `http://localhost:3000`

---

### Running Entirely with Docker Compose

If you have Docker Desktop running:
```powershell
docker compose up -d --build
```
This automatically boots Redis, the FastAPI backend, and the Celery background worker.

---

## 🔮 Upcoming Roadmap

- [ ] **Phase 11: Real Authentication** — Transition from `dev_stub` to Supabase Auth (OAuth, magic links, JWT bearer validation).
- [ ] **Interactive Mock Interview Engine** — Generate dynamic behavioral and technical interview questions based on confirmed resume skills and target role.
- [ ] **Real-time Practice Simulation** — Conversational interview sessions with live audio/speech-to-text or interactive chat.
- [ ] **Scoring & Performance Analytics** — Detailed interview scoring rubrics, answer evaluations, and personalized improvement tips.
