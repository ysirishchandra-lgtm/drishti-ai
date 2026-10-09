# DRISHTI-AI — PROJECT BOOK

**Team:** SPARK  
**Project:** DRISHTI-AI  
**Domain:** Open Innovation  
**Repository:** `drishti-ai` (branch: `main`)  
**Hackathon Timeline:** 36-Hour Sprint  
**Last Updated:** 2026-10-09  

---

## 1. Project Overview

DRISHTI-AI is an explainable AI-assisted screening support prototype built for rural and community eye-care settings across India. In vast rural regions, lack of specialized ophthalmologists delays the detection of Diabetic Retinopathy (DR), leading to irreversible vision loss. 

DRISHTI-AI provides an intuitive platform where primary healthcare workers and vision center technicians can capture or upload fundus photographs, perform real-time image usability triage, obtain AI screening predictions (when a validated model is loaded), view explainability heatmaps (Grad-CAM), and maintain organized patient screening records for timely clinical referral.

---

## 2. Problem Statement

Diabetic Retinopathy affects approximately 15–20% of diabetic patients in India. Rural screening programs suffer from:
1. Shortage of trained ophthalmologists for reading fundus images on-site.
2. High rate of unusable or degraded retinal photographs requiring costly patient recalls.
3. Lack of explainable, trustworthy AI triage tools tailored to low-bandwidth clinic environments.
4. Fragmented screening logs and referral documentation between primary clinics and tertiary eye hospitals.

DRISHTI-AI targets primary triage and referral management, functioning as a clinical decision-support prototype rather than an automated diagnosis device.

---

## 3. Team Members & Responsibilities

| Name | Role | Responsibilities | Current Focus |
|---|---|---|---|
| **Sirish** | **Team Lead, Backend & Database** | Architecture, FastAPI backend, image validation, SQLite persistence, API contracts, deployment prep, documentation | Backend foundation, validation, persistence, API |
| **Ashwidha** | **Frontend Lead** | React + Vite UI, technician dashboard, upload flows, report viewer, responsive UI | Initial frontend setup & design against contract |
| **Rudra** | **AI/ML Lead** | DR model discovery, weights verification, licensing, 5-class DR classification, Grad-CAM generation | Identifying verified model checkpoint & preprocessing pipeline |
| **Kaustub** | **Integration QA & Demo Support** | End-to-end integration testing, edge-case validation, test reports, demo script & presentation | Backend test execution, quality validation checks |

---

## 4. Architecture & Request Flow

```
[ Primary Healthcare Worker / Vision Center ]
                      │ (Retinal Fundus Image)
                      ▼
        [ React + Vite Frontend (Port 5173) ]
                      │ (Multipart Form-Data / JSON REST)
                      ▼
           [ FastAPI Backend (Port 8000) ]
        ┌─────────────┴─────────────┐
        ▼                           ▼
[ Image Validation Service ]   [ Model Service Interface ]
  - Size check (<=15MB)          - Model status inspection
  - Format check (JPEG,PNG,WebP) - Preprocessing (when loaded)
  - PIL decode & integrity       - 5-class inference (stubbed until loaded)
  - Heuristic usability checks   - Grad-CAM heatmap generator
        │                           │
        └─────────────┬─────────────┘
                      ▼
           [ SQLite Persistence ]
             - Screenings table
             - Quality metadata
             - Review / Referral status
```

### Request Flow:
1. **Upload:** User uploads fundus photo -> `POST /api/v1/screenings/upload` validates format, size, decodability, dimensions, and saves metadata.
2. **Usability Check:** Validation returns preliminary image usability flags (e.g., contrast, brightness, resolution) without claiming clinical diagnosis.
3. **Screening Analysis:** User requests analysis -> `POST /api/v1/screenings/{id}/analyze`. If a verified model is loaded, it executes inference; otherwise, returns clean `model_status: "not_configured"`.
4. **Record Tracking:** History and referral status queried via `GET /api/v1/screenings` and `GET /api/v1/screenings/{id}`.

---

## 5. Technology Stack & Technical Rationale

| Layer | Technology | Selection Rationale |
|---|---|---|
| **Backend Framework** | **FastAPI 0.115+** | High performance, native async support, automatic OpenAPI/Swagger documentation, fast iteration for 36-hr sprint |
| **ASGI Server** | **Uvicorn** | Production-ready ASGI server with fast reload support |
| **Image Processing** | **Pillow (PIL)** | Robust, memory-safe image decoding, metadata extraction, and dimension validation |
| **Validation & Serialization** | **Pydantic v2** | Strong data contracts, typed schemas, and automatic input sanitization |
| **Database** | **SQLite (via Python standard library)** | Zero-config, reliable ACID persistence, zero external daemon requirements for local prototype development |
| **Frontend Framework** | **React 18 + Vite** | Instant HMR, minimal build overhead, modern component model |
| **AI/ML Runtime (Target)** | **PyTorch / Torchvision / ONNX** | Industry standard for medical imaging and Grad-CAM explainability |
| **Testing** | **Pytest + HTTPX** | Expressive test suites, async HTTP test client, reliable CI verification |

---

## 6. Repository & Branch Information

- **Local Repository:** `D:\drishti-ai`
- **Default Branch:** `main`
- **Git Remote:** To be linked to team lead's GitHub repository. (No push performed until user provides remote URL)
- **Status:** Initialized locally with clean branch state.

---

## 7. Folder Structure

```
drishti-ai/
├── frontend/             # React + Vite client (Ashwidha)
│   └── .gitkeep
├── backend/              # FastAPI backend (Sirish)
│   ├── .venv/            # Python virtual environment (git-ignored)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py       # FastAPI application factory & routes
│   │   ├── database.py   # SQLite database engine & queries
│   │   ├── api/          # Modular API router endpoints
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       └── screenings.py
│   │   ├── services/     # Business logic & services
│   │   │   ├── __init__.py
│   │   │   ├── image_service.py # Image validation & quality heuristics
│   │   │   └── model_service.py # DR Model inference boundary
│   │   └── schemas/      # Pydantic models
│   │       ├── __init__.py
│   │       └── screening.py
│   ├── tests/            # Test suite
│   │   ├── __init__.py
│   │   └── test_api.py
│   ├── requirements.txt  # Dependencies
│   └── drishti.db        # Local SQLite database (git-ignored)
├── docs/                 # Documentation & API contracts
│   ├── architecture.md
│   └── api-contract.md
├── tests/                # System & integration tests (Kaustub)
│   └── .gitkeep
├── data/                 # Sample fundus images (git-ignored)
│   └── .gitkeep
├── models/               # Model weights (git-ignored)
│   └── .gitkeep
├── PROJECT_BOOK.md       # Live project book & milestone logs
├── README.md
└── .gitignore
```

---

## 8. Environment Setup & Execution Commands

```bash
# 1. Navigate to backend
cd backend

# 2. Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows Command Prompt:
.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 5. Run test suite
pytest tests/ -v
```

---

## 9. API Endpoint Contract

| Method | Endpoint | Description | Status |
|---|---|---|---|
| `GET` | `/health` | Service health, version, AI model status (`not_configured`) | Verified (200 OK) |
| `POST` | `/api/v1/screenings/upload` | Ingest fundus image, validate integrity & dimensions | Verified (201 Created) |
| `POST` | `/api/v1/screenings/{id}/analyze` | Run DR inference or return explicit model unavailable response | Verified (200 OK) |
| `GET` | `/api/v1/screenings/{id}` | Fetch screening record, image quality, and analysis status | Verified (200 OK) |
| `GET` | `/api/v1/screenings` | Paginated listing of historical screenings | Verified (200 OK) |

---

## 10. Image Validation Behavior

The backend implements a strict, multi-step image validation pipeline:
1. **Size Enforcement:** Maximum upload size configured to 15 MB. Rejects oversized payloads with HTTP 413.
2. **MIME & Magic Bytes Inspection:** Inspects both declared content-type and true file magic bytes. Accepts JPEG, PNG, and WebP.
3. **Decodability & PIL Verification:** Decodes image bytes using Pillow to detect corrupted or malformed payloads.
4. **Dimension Sanity:** Enforces minimum resolution (200x200 px) to prevent low-resolution garbage inputs.
5. **Heuristic Quality Checks (Non-Clinical):** Evaluates basic brightness, contrast range, and sharpness metrics. Explicitly labeled as preliminary technical heuristics, not certified clinical quality metrics.
6. **Privacy Protection:** Never commits uploaded files to git. Never returns raw local server paths or internal stack traces in client responses.

---

## 11. AI Model Status & Integration Boundary

- **Current Status:** `not_configured`
- **Target DR Classes (when verified):**
  1. Class 0: No DR
  2. Class 1: Mild
  3. Class 2: Moderate
  4. Class 3: Severe
  5. Class 4: Proliferative DR (PDR)
- **Boundary Policy:**
  - Zero fabricated predictions or synthetic confidence scores.
  - Returns `model_status: "not_configured"` and message indicating awaiting verified model weights from Rudra.
  - The model service interface in `app/services/model_service.py` provides an isolated hook for Rudra to plug in weights, preprocessing, and Grad-CAM generation without touching API routes.

---

## 12. Security & Clinical Limitations

1. **Screening Support Only:** The system is strictly a triage tool; not an autonomous diagnostic device.
2. **No Data Leakage:** Local images and databases are git-ignored to prevent accidental exposure of retinal data.
3. **CORS:** Restricted to `http://localhost:5173` and `http://127.0.0.1:5173` (Vite dev server) to prevent unauthorized origins.
4. **Input Sanitization:** Multi-part file streams are validated in-memory and buffered safely without shell command execution.
5. **Safe Error Handling:** Internal errors are logged to console and return generic HTTP 500 JSON payloads without stack traces.

---

## 13. Milestone Checklist

- [x] **Milestone 1: Project & Repository Foundation**
  - [x] Inspect workspace and initialize Git with `main` branch.
  - [x] Establish modular folder structure (`frontend`, `backend`, `docs`, `data`, `models`).
  - [x] Configure `.gitignore` for Python, Vite, databases, medical data, and models.
  - [x] Create comprehensive `README.md` and initial `PROJECT_BOOK.md`.
- [x] **Milestone 2: Backend Environment & Health Endpoint**
  - [x] Set up Python virtual environment in `backend/.venv`.
  - [x] Install FastAPI, Uvicorn, python-multipart, Pillow, Pytest, HTTPX.
  - [x] Implement `GET /health` with `not_configured` model status and CORS.
  - [x] Run smoke test verifying `GET /health` (Status 200 OK verified on live server).
- [x] **Milestone 3: Image Validation & Upload Pipeline**
  - [x] Implement modular `ImageValidationService`.
  - [x] Implement `POST /api/v1/screenings/upload`.
  - [x] Test valid images, corrupted files, unsupported formats, and oversized uploads.
- [x] **Milestone 4: API Contract & AI Boundary**
  - [x] Write `docs/architecture.md` and `docs/api-contract.md`.
  - [x] Implement `ModelService` boundary reporting `not_configured`.
  - [x] Implement `POST /api/v1/screenings/{id}/analyze`.
- [x] **Milestone 5: SQLite Persistence & Testing**
  - [x] Implement SQLite schema and queries for screenings in `app/database.py`.
  - [x] Implement `GET /api/v1/screenings/{id}` and `GET /api/v1/screenings`.
  - [x] Add and execute comprehensive automated pytest suite (14/14 tests PASSED).
  - [x] Document all results and next steps for team members.

---

## 14. Tests Executed & Actual Results

Command executed:
```bash
pytest backend/tests -v
```

Output:
```
============================= test session starts =============================
platform win32 -- Python 3.13.0rc3, pytest-9.1.1, pluggy-1.6.0 -- backend/.venv/Scripts/python.exe
rootdir: D:\drishti-ai\backend
plugins: anyio-4.15.1
collected 14 items

tests/test_api.py::test_health_endpoint PASSED                           [  7%]
tests/test_api.py::test_upload_valid_jpeg PASSED                         [ 14%]
tests/test_api.py::test_upload_valid_png PASSED                          [ 21%]
tests/test_api.py::test_upload_valid_webp PASSED                         [ 28%]
tests/test_api.py::test_reject_text_file_as_image PASSED                 [ 35%]
tests/test_api.py::test_reject_corrupted_image PASSED                    [ 42%]
tests/test_api.py::test_reject_unsupported_gif_format PASSED             [ 50%]
tests/test_api.py::test_reject_small_dimensions PASSED                   [ 57%]
tests/test_api.py::test_reject_oversized_payload PASSED                  [ 64%]
tests/test_api.py::test_analyze_when_model_not_configured PASSED         [ 71%]
tests/test_api.py::test_analyze_nonexistent_screening PASSED             [ 78%]
tests/test_api.py::test_get_screening_by_id PASSED                       [ 85%]
tests/test_api.py::test_get_nonexistent_screening PASSED                 [ 92%]
tests/test_api.py::test_list_screenings_pagination PASSED                [100%]

======================== 14 passed, 1 warning in 2.68s ========================
```

Live Server Smoke Test:
- `GET http://127.0.0.1:8000/health`: HTTP 200 OK (`{"status":"ok","project":"DRISHTI-AI","version":"0.1.0","model_status":"not_configured",...}`)
- `GET http://127.0.0.1:8000/docs`: HTTP 200 OK (Interactive Swagger UI active)

---

## 15. Blockers & Dependencies

- **Blocker 1 (AI Model):** Awaiting Rudra to identify and provide verified model weights (e.g. PyTorch/ONNX checkpoint) and preprocessing specifications.
- **Blocker 2 (Remote Repository):** Waiting for team lead (Sirish) to provide the GitHub repository remote URL for upstream pushing.
- **No blocking issues on backend or API contracts.**

---

## 16. Next Tasks & Member Ownership

1. **Ashwidha (Frontend Lead):**
   - Initialize Vite + React frontend in `frontend/`.
   - Implement technician upload form with dropzone and client-side preview.
   - Display image quality feedback and heuristic warnings.
   - Connect to `POST /api/v1/screenings/upload` and `GET /api/v1/screenings`.
2. **Rudra (AI/ML Lead):**
   - Place verified weights file inside `models/`.
   - Update `DRModelService._load_model()` and `DRModelService.predict()` in `app/services/model_service.py`.
   - Implement Grad-CAM heatmap visualization hook in `generate_gradcam()`.
3. **Kaustub (Integration QA):**
   - Add integration tests in `tests/` covering large batch uploads.
   - Test UI responsiveness and error messaging across edge cases.
   - Prepare demo walkthrough narrative for hackathon judges.

---

## 17. Dated Progress Log

- **2026-10-09 (Day 1 - Setup Phase):**
  - Inspected clean workspace `D:\drishti-ai`.
  - Initialized Git repository on `main` branch.
  - Created `.gitignore` excluding sensitive files, images, models, virtual environments, and SQLite databases.
  - Created initial documentation: `README.md`, `PROJECT_BOOK.md`.
  - Created Python virtual environment in `backend/.venv` and installed FastAPI, Uvicorn, python-multipart, Pillow, Pytest, HTTPX.
  - Implemented modular image validation service with magic bytes detection, PIL two-pass verification, dimension checks, and usability heuristics.
  - Implemented AI model boundary interface strictly returning `not_configured` without fake predictions.
  - Implemented SQLite database persistence with zero PII and no image byte storage.
  - Implemented full API v1 router (`/upload`, `/{id}/analyze`, `/{id}`, `/screenings`).
  - Added CORS configuration for `http://localhost:5173`.
  - Executed test suite with 14 automated tests; 100% passed.
  - Verified live server with `uvicorn` and confirmed `GET /health` and `GET /docs`.
