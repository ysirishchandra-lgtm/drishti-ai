# DRISHTI-AI System Architecture

**Team:** SPARK  
**Project:** DRISHTI-AI  
**Domain:** Open Innovation — Explainable AI Retinal Screening Prototype for Rural India  
**Version:** 0.1.0  

---

## 1. Executive Summary

DRISHTI-AI is engineered to address the critical shortage of ophthalmologists in rural Indian primary care settings. It provides an explainable AI-assisted screening support platform capable of:
1. Ingesting retinal fundus images from low-cost fundus cameras and smartphones.
2. Running technical usability checks (resolution, format, decodability, basic illumination heuristics) before submission.
3. Interfacing with a 5-class diabetic retinopathy classification model (when verified weights are loaded).
4. Generating visual explainability maps (Grad-CAM) to foster trust among healthcare workers.
5. Maintaining persistent, structured screening logs to streamline secondary ophthalmologist tele-consultation and referrals.

---

## 2. System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PRIMARY HEALTHCARE WORKER / CLINIC                   │
│          Captures or uploads retinal fundus photograph via UI          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   FRONTEND TIER (React 18 + Vite)                      │
│                  Maintained by Ashwidha (Port 5173)                    │
│                                                                        │
│  - Image Upload & Preview Interface                                   │
│  - Technician Usability Warnings & Guidance                           │
│  - Screening Result Viewer & Grad-CAM Visualizer                      │
│  - Patient Screening History Table                                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP REST / Multipart
                                    │ CORS Allowed: http://localhost:5173
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   BACKEND API TIER (FastAPI + ASGI)                    │
│                   Maintained by Sirish (Port 8000)                     │
│                                                                        │
│  ┌───────────────────────┐         ┌────────────────────────────────┐  │
│  │   FastAPI Router      │         │   Image Validation Service     │  │
│  │   - GET /health       ├────────►│   - Binary magic-byte inspect  │  │
│  │   - POST /upload      │         │   - Pillow safe decode verify  │  │
│  │   - POST /analyze     │         │   - Size & dimension bounds    │  │
│  │   - GET /screenings   │         │   - Brightness/contrast metrics│  │
│  └───────────┬───────────┘         └────────────────────────────────┘  │
│              │                                                         │
│              ├─────────────────────────────────────────┐               │
│              ▼                                         ▼               │
│  ┌───────────────────────────────┐     ┌────────────────────────────┐  │
│  │   SQLite Persistence Layer    │     │   AI Model Service Boundary│  │
│  │   - screening_id (UUID4)      │     │   Maintained by Rudra      │  │
│  │   - quality heuristics        │     │                            │  │
│  │   - model_status & results    │     │   - Checks weights state   │  │
│  │   - human review & referral   │     │   - 5-class DR inference   │  │
│  │   (No raw image bytes in DB)  │     │   - Grad-CAM heatmap gen   │  │
│  └───────────────────────────────┘     └────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Boundaries & Team Ownership

The repository is modularized to ensure all four team members can make progress in parallel without Git merge conflicts:

### 3.1 Sirish — Team Lead, Backend & Database
- **Scope:** `backend/app/main.py`, `backend/app/api/`, `backend/app/database.py`, `backend/app/services/image_service.py`.
- **Deliverables:** Stable REST endpoints, multi-stage image verification, SQLite schema, error handling, CORS security.

### 3.2 Ashwidha — Frontend Lead
- **Scope:** `frontend/` directory.
- **Contract:** Builds against `docs/api-contract.md`. Relies on mockable contract fields (`model_status: "not_configured"` handled gracefully).
- **Communication:** Consumes `http://127.0.0.1:8000` via Axios/Fetch with standard JSON response formats.

### 3.3 Rudra — AI/ML Lead
- **Scope:** `backend/app/services/model_service.py` and `models/` directory.
- **Contract:** Inherits `AbstractDRModelService`. Loads weights into memory, implements `predict()`, and returns class probabilities matching target classes:
  - Class 0: No DR
  - Class 1: Mild
  - Class 2: Moderate
  - Class 3: Severe
  - Class 4: Proliferative DR (PDR)
- **Zero Fabrication Rule:** Until verified weights are loaded, status is strictly `not_configured`.

### 3.4 Kaustub — Integration QA & Demo Lead
- **Scope:** `backend/tests/`, `tests/` directory, and test execution reports.
- **Deliverables:** Validates edge cases (oversized files, corrupted bytes, non-images), tracks regression runs with `pytest`, designs demo walkthrough script.

---

## 4. Multi-Stage Image Validation Pipeline

To protect the server and provide actionable feedback to healthcare workers:
1. **Size Guard:** 15 MB hard limit enforced before memory saturation.
2. **True Format Detection:** Inspects binary magic numbers (e.g. `\xff\xd8\xff` for JPEG, `\x89PNG` for PNG, `RIFF...WEBP`). User-supplied MIME types and file extensions are never trusted blindly.
3. **Pillow Two-Pass Integrity Check:**
   - First pass: `img.verify()` validates structural headers.
   - Second pass: `img.load()` unpacks pixel buffers to detect truncated streams.
4. **Dimension Sanity:** Enforces minimum 200x200 px and maximum 10,000x10,000 px.
5. **Preliminary Usability Metrics (Non-Clinical Heuristics):**
   - Mean brightness evaluated over grayscale projection (<15 flagged as underexposed; >240 flagged as washed out).
   - Pixel standard deviation (<10 flagged as low contrast).
   - Explicit disclaimer included: *Preliminary technical usability heuristics only. Not a clinically validated image quality evaluation.*

---

## 5. Security & Privacy by Design

- **HIPAA / Indian Health Data Compliance:**
  - Raw patient images are never written to source control (`.gitignore` enforces isolation of `data/`, `uploads/`, `*.db`).
  - Personal identifiable information (PII) such as patient names or Aadhaar numbers are intentionally excluded from early prototype tables.
  - Opaque UUID4 identifiers (`screening_id`) are used for all tracking.
- **Information Leakage Prevention:**
  - Global FastAPI exception handlers intercept unexpected exceptions, logging details internally while returning generic JSON responses without stack traces or absolute server paths.
- **CORS Lockdown:**
  - Strict whitelist configured for local Vite development (`http://localhost:5173`, `http://127.0.0.1:5173`).
