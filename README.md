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
├── frontend/             # Original clean, non-3D frontend (Ashwidha)
│   ├── index.html        # Semantic structure, navigation & screening workspace
│   ├── styles.css        # Clean responsive styling & design tokens
│   ├── app.js            # Client-side validation, preview, & sample workflow
│   ├── README.md         # Frontend guide & integration specifications
│   └── PROJECT_BOOK.md   # Frontend prototype log
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

## 4. Running the Application Locally

You can run the application either as a **standalone frontend** or as a **unified FastAPI service** (FastAPI serves both the API and the static frontend).

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Modern web browser (Chrome, Firefox, Edge, Safari)

---

### Option A: Standalone Frontend (Port 8080)

Run the static web server directly from the `frontend` folder:

```bash
python -m http.server 8080 --directory frontend
```
- Open [http://127.0.0.1:8080](http://127.0.0.1:8080) in your browser.
- You can also open `frontend/index.html` directly in any modern browser without a server.

---

### Option B: Unified Server via FastAPI (Port 8000)

Start the FastAPI application. It automatically mounts and serves the `frontend` directory at the root URL `/` alongside the API routes:

```bash
cd backend
.venv\Scripts\activate      # On Windows PowerShell: .venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
- **Unified Web Application:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **API Swagger Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check Endpoint:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 5. Automated Testing

Run the automated test suite:
```bash
backend\.venv\Scripts\python -m pytest backend/tests
```
All 20 unit and integration tests validate health checks, real fundus image uploads, technical usability heuristics, corrupt image rejections, and honest unavailable model reporting.

---

## 6. API Endpoints Overview

| Method | Endpoint | Description | Status |
|---|---|---|---|
| `GET` | `/health` | Service health, version, and AI model readiness check | Available |
| `POST` | `/api/v1/screenings/upload` | Upload & decode retinal image, run preliminary usability checks | Available |
| `POST` | `/api/v1/screenings/{screening_id}/analyze` | Trigger DR inference pipeline or report model unavailable status | Available |
| `GET` | `/api/v1/screenings/{screening_id}` | Retrieve screening record, quality flags, and analysis result | Available |
| `GET` | `/api/v1/screenings` | List historical screening records with pagination | Available |

See [`docs/api-contract.md`](docs/api-contract.md) for full request/response schemas.

---

## 7. Current Project Status & Model Boundary

- **Image Ingestion & Usability Heuristics:** Fully operational. Checks file size, magic bytes, Pillow decode, dimensions, mean brightness, and contrast std.
- **Trained AI Model:** **Not yet developed.** When analysis is triggered, the system reports `model_status: "not_configured"` honestly without fabricating predictions or confidence values.
- **Explainability (Grad-CAM):** The interface is pre-wired to display side-by-side heatmaps once verified PyTorch/ONNX model weights and convolutional hooks are connected by the AI lead (Rudra).
