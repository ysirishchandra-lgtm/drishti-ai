# DRISHTI-AI

**Explainable AI-based Diabetic Retinopathy Screening Support for Rural India**  
**Team:** SPARK | **Domain:** Open Innovation | **Hackathon Edition:** 36-Hour Prototype

> ⚠️ **IMPORTANT CLINICAL & REGULATORY DISCLAIMER**  
> DRISHTI-AI is an experimental screening-support prototype designed to triage retinal fundus photographs and facilitate healthcare worker workflows. It is **NOT** a certified medical device, does **NOT** provide a definitive medical diagnosis, and **MUST NEVER** replace clinical evaluation by a certified ophthalmologist or trained eye care specialist.

---

## 1. Project Overview

Diabetic Retinopathy (DR) is a leading cause of preventable blindness in India, particularly in rural and underserved areas where ophthalmologists are scarce. DRISHTI-AI empowers community health workers and primary vision centers to:
1. Validate retinal fundus photograph quality and basic usability before submission.
2. Interface with an AI-based diabetic retinopathy classification model (when a verified model is loaded).
3. Display explainability maps (Grad-CAM) to support clinical review.
4. Record structured screening records, referral flags, and human-in-the-loop validation logs.

---

## 2. Team SPARK & Roles

| Member | Role | Core Responsibilities |
|---|---|---|
| **Sirish** | **Team Lead, Backend & Database** | FastAPI backend, image ingestion/validation, SQLite persistence, API contracts, infrastructure & integration lead |
| **Ashwidha** | **Frontend Lead** | React + Vite UI, technician dashboard, image upload flow, screening reports, responsive design |
| **Rudra** | **AI/ML Lead** | DR model discovery, weights verification, licensing, 5-class DR inference, Grad-CAM generation |
| **Kaustub** | **Integration QA & Demo** | E2E test verification, cross-component testing, edge cases, screening history validation, demo presentation |

---

## 3. Architecture & Modular Boundaries

The repository is structured to enable parallel, independent development across all four members:

```
drishti-ai/
├── frontend/             # React + Vite application (Ashwidha)
├── backend/              # FastAPI REST backend (Sirish)
│   ├── app/
│   │   ├── api/          # Route handlers (v1 endpoints)
│   │   ├── services/     # Image validation & model service interface
│   │   ├── schemas/      # Pydantic data schemas
│   │   └── database.py   # SQLite persistence layer
│   ├── tests/            # Backend unit & integration test suite
│   ├── uploads/          # Temporary local staging for uploads (git-ignored)
│   └── requirements.txt  # Python backend dependencies
├── docs/                 # Architectural specifications & API contracts
│   ├── architecture.md
│   └── api-contract.md
├── tests/                # System & end-to-end integration tests (Kaustub)
├── data/                 # Sample datasets & test fundus images (git-ignored)
├── models/               # Model weights & checkpoints (git-ignored)
├── PROJECT_BOOK.md       # Central live engineering log & milestone tracking
└── README.md
```

---

## 4. Getting Started (Backend)

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Git

### 1. Set Up Python Virtual Environment
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows Command Prompt:
.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run FastAPI Backend Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Interactive API Documentation
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Service Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 5. API Endpoints Overview

| Method | Endpoint | Description | Status |
|---|---|---|---|
| `GET` | `/health` | Service health, version, and AI model readiness check | Available |
| `POST` | `/api/v1/screenings/upload` | Upload & decode retinal image, run preliminary usability checks | Available |
| `POST` | `/api/v1/screenings/{screening_id}/analyze` | Trigger DR inference pipeline or report model unavailable status | Available |
| `GET` | `/api/v1/screenings/{screening_id}` | Retrieve screening record, quality flags, and analysis result | Available |
| `GET` | `/api/v1/screenings` | List historical screening records with pagination | Available |

See [`docs/api-contract.md`](docs/api-contract.md) for full request/response schemas.

---

## 6. Development Guidelines for the Team

- **Frontend (Ashwidha):** Connect to `http://127.0.0.1:8000` with CORS preconfigured for `http://localhost:5173`.
- **AI/ML (Rudra):** Implement `app/services/model_service.py` following the documented abstract interface. Never return synthetic predictions when a verified model is absent.
- **QA (Kaustub):** Run tests using `pytest backend/tests` and monitor edge-case handling for corrupted, oversized, and non-image files.
