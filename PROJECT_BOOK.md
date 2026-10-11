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

| Name | Role | Core Responsibilities | Final Project Focus |
|---|---|---|---|
| **Sirish** | **Team Lead, Backend & Database** | FastAPI backend architecture, image validation service, SQLite persistence layer, REST endpoints, Grad-CAM pipeline integration, repository polish | Backend foundation, validation, persistence, Grad-CAM integration |
| **Ashwidha** | **Frontend Lead** | Responsive UI/UX layout, landing page, technician screening workspace, file upload flow, probability charts, client error handling | Responsive HTML5/CSS3/JS UI, live backend connectivity |
| **Rudra** | **AI/ML Lead** | DR model discovery, 5-class EfficientNetB0 training in `DRISHTI_1.ipynb`, model artifact export (`RetinaExplain_AI_v2_final.keras`), Grad-CAM layer configuration | Trained model artifact, 5-class weights, Grad-CAM architecture |
| **Kaustub** | **Integration QA & Testing** | Comprehensive automated test suite (26 pytest tests), cross-component verification, dataset split audit, demo walkthrough verification | End-to-end test validation, API contract & frontend integration testing |

---

## 4. Architecture & Request Flow

```
[ Primary Healthcare Worker / Vision Center ]
                      │ (Retinal Fundus Image)
                      ▼
         [ Frontend Dashboard (Port 8000 / 8080) ]
         (HTML5, CSS3, Vanilla JS, Drag-and-Drop)
                      │ (Multipart Form-Data / JSON REST)
                      ▼
            [ FastAPI Backend (Port 8000) ]
         ┌─────────────┴─────────────┐
         ▼                           ▼
[ Image Validation Service ]   [ Model Service (Singleton) ]
  - Size check (<=15MB)          - Input preprocessing ((224,224,3) float32)
  - Magic bytes & PIL decode     - EfficientNetB0 5-class forward pass
  - Min dimensions (200x200 px)  - Softmax probabilities calculation
  - Brightness & contrast checks - Grad-CAM engine (tf.GradientTape on top_activation)
         │                           │
         └─────────────┬─────────────┘
                       ▼
            [ SQLite Persistence ]
              - screenings table
              - Quality metadata & heuristic flags
              - 5-class predictions & confidence
              - Grad-CAM heatmap overlay path
```

### Request Flow:
1. **Upload:** User uploads fundus photo -> `POST /api/v1/screenings/upload` validates format, size, decodability, dimensions, and saves metadata.
2. **Usability Check:** Validation returns preliminary image usability flags (e.g., contrast, brightness, resolution) without claiming clinical diagnosis.
3. **Screening Analysis:** User requests analysis -> `POST /api/v1/screenings/{id}/analyze`. Executes verified EfficientNetB0 inference, computes Grad-CAM heatmap overlay via `tf.GradientTape`, and updates database record.
4. **Grad-CAM Overlay:** Frontend retrieves PNG heatmap overlay via `GET /api/v1/screenings/{id}/gradcam` for clinical explainability.
5. **Record Tracking:** History and referral status queried via `GET /api/v1/screenings` and `GET /api/v1/screenings/{id}`.

---

## 5. Technology Stack & Technical Rationale

| Layer | Technology | Selection Rationale |
|---|---|---|
| **Backend Framework** | **FastAPI 0.115+** | High performance, native async support, automatic OpenAPI/Swagger documentation, fast iteration for 36-hr sprint |
| **ASGI Server** | **Uvicorn** | Production-ready ASGI server with fast reload support |
| **Image Processing** | **Pillow (PIL 10.4+)** | Robust, memory-safe image decoding, metadata extraction, and dimension validation |
| **Validation & Serialization** | **Pydantic v2** | Strong data contracts, typed schemas, and automatic input sanitization |
| **Database** | **SQLite (Python stdlib)** | Zero-config, reliable ACID persistence, zero external daemon requirements for local prototype development |
| **Frontend** | **HTML5, CSS3, Vanilla JS** | Lightweight, zero-build-step client, robust cross-browser compatibility, minimal footprint |
| **AI/ML Runtime** | **TensorFlow 2.16+ / Keras 3.0+** | EfficientNetB0 convolutional neural network, `tf.GradientTape` for Grad-CAM explainability |
| **Testing** | **Pytest + HTTPX** | Expressive test suites, async HTTP test client, reliable CI verification (26 tests passing) |

---

## 6. Repository & Branch Information

- **Local Repository:** `D:\drishti-ai`
- **Default Branch:** `main`
- **Git Remote:** `https://github.com/ysirishchandra-lgtm/drishti-ai.git` (origin/main)
- **Status:** Initialized, linked, and pushed upstream (`411e6be`).

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
- **Resolved:** GitHub remote repository linked and pushed to `origin/main`.
- **Zero blocking issues on backend, database, or API contracts. Development setup is verified ready for frontend.**

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
  - Initialized `datasets/aptos2019/` directory structure and added `datasets/` safeguard to `.gitignore`.
  - Conducted Phase 1 dataset preflight checks (disk space: 563 GB free, verified Git exclusion).
  - Installed Kaggle CLI in `backend/.venv` and verified OAuth authentication and APTOS 2019 access.
  - Successfully downloaded and verified `datasets/aptos2019/train.csv` (3,662 rows; Grade 0: 1805, Grade 1: 370, Grade 2: 999, Grade 3: 193, Grade 4: 295).
  - Downloaded official competition archive `aptos2019-blindness-detection.zip` (10,215,289,875 bytes).
  - Passed ZIP archive CRC integrity test (`testzip()` 0 errors).
  - Selectively extracted all 3,662 training images into `datasets/aptos2019/train_images/` (skipped 1,928 unlabelled test images).
  - Verified 1-to-1 label-to-image matching (3,662/3,662 IDs match, 0 missing, 0 unmatched).
  - Completed PIL image readability audit: 3,662/3,662 verified readable (0 corrupt files).
  - Completed dataset integrity audit: identified 123 duplicate image groups (251 images), with 30 groups possessing inter-rater conflicting diagnostic labels.
  - Documented dataset readiness and deduplication requirements for Rudra's train/val split.
  - Phase 5: Independently verified duplicate audit via MD5 and SHA-256 byte hashing (3,534 unique hashes, 123 duplicate groups, 251 images, 30 conflicting groups with 62 images).
  - Confirmed patient-level IDs are absent from APTOS `train.csv`; documented that patient-level cross-eye leakage cannot be ruled out from metadata alone.
  - Generated reproducible audit report: `datasets/aptos2019/duplicates_audit.csv`.
  - Built group-leakage-free, stratified dataset manifest: `datasets/aptos2019/dataset_manifest.csv` (Train: 2932, Val: 369, Test: 361) preserving natural class distribution.
  - Generated class-wise manifests in `datasets/aptos2019/classes/class_0.csv` to `class_4.csv` without duplicating multi-gigabyte image files.
  - Formulated class-balanced training strategy (class-weighted loss + WeightedRandomSampler + training-only geometric/color jitter augmentation; unaugmented evaluation sets).
  - Phase 6: Executed comprehensive manifest verification with 100% PASS across all 9 integrity checks.
  - Formulated clean evaluation manifest (`datasets/aptos2019/dataset_manifest_clean_eval.csv`) quarantining 62 conflicting images (Clean Train: 2883, Clean Val: 362, Clean Test: 355).
  - Created physical class-wise image organization under `datasets/aptos2019/classwise_images/` without altering or deleting originals:
    - `class_0_no_dr`: 1,801 images
    - `class_1_mild`: 360 images
    - `class_2_moderate`: 976 images
    - `class_3_severe`: 180 images
    - `class_4_proliferative_dr`: 283 images
    - `unresolved_conflicting_labels`: 62 images (isolated quarantine for ambiguous ground truth).
  - Byte-verified all 3,662 placed images against sources with 0 errors. All datasets confirmed Git-ignored.
  - Acquired official OIA-DDR dataset (13,673 raw images across train, valid, test) from official Google Drive source.
  - Reconstructed 14.10 GB archive from 10 split parts and verified archive CRC32 integrity with 0 errors.
  - Conducted cryptographic SHA-256 deduplication: discovered 13,573 unique images, 97 concordant duplicate groups (197 files), and 0 conflicting label groups.
  - Organized `datasets/ddr/cleaned_all/` with 13,573 unique images (Class 0: 6166, Class 1: 630, Class 2: 4477, Class 3: 236, Class 4: 913, Unresolved/Ungradable: 1151).
  - Constructed exact class-balanced dataset `datasets/ddr/balanced/` with 236 unique images per class (total: 1,180 images) sequentially numbered `1.jpg` to `236.jpg` using seed 42.
  - Generated complete manifests: `dataset_manifest.csv`, `duplicate_audit.csv`, and `balanced_manifest.csv`. All datasets confirmed Git-ignored.
  - Conducted DDR Balanced Dataset Split Integrity Audit:
    - Analyzed split origins of the 1,180 balanced images: 578 from Official Train (49.0%), 245 from Official Valid (20.8%), 357 from Official Test (30.3%).
    - Detected critical split leakage risk: Grade 3 (236 images in balanced) consumes 100% of all Grade 3s across Train (118), Valid (47), and Test (71).
    - Established strict split integrity rule: `balanced/` must NOT be used directly as a training pool; generated `balanced_split_manifest.csv` and `cleaned_official_split_manifest.csv`.
    - Formulated leak-free split recommendation: maximum clean balanced training subset strictly within Official Train is 118 images/class (590 total), or full-train training (6,260 images) using WeightedRandomSampler.
- **2026-10-10 (Day 2 - 5-Class 500/Class Expansion Phase):**
  - Evaluated existing image inventory across APTOS (177 unique clean Grade 3) and DDR (236 unique clean Grade 3); identified a 87-image deficit to reach 500 genuine Severe DR (Grade 3) images without artificial duplication or synthetic data.
  - Ingested official IDRiD Disease Grading dataset (516 images) under CC BY 4.0 license via Kaggle CLI.
  - Performed cryptographic SHA-256 deduplication and cross-dataset collision audit across 17,851 candidate images; identified zero cross-dataset collisions.
  - Audited IDRiD internal duplicates: identified 6 duplicate groups, successfully quarantined 3 discordant duplicate groups (including cross-split discordant pair `train IDRiD_118 (Grade 0)` vs `test IDRiD_064 (Grade 3)`) and excluded redundant concordant duplicates.
  - Ingested and audited Messidor-2 benchmark (1,744 images, 75 Grade 3) as verified reserve dataset.
  - Constructed final balanced dataset in `D:\drishti-ai\datasets\balanced_5class_2500\`:
    - `class_0_no_dr`: Exactly 500 images (APTOS: 250, DDR: 250)
    - `class_1_mild`: Exactly 500 images (APTOS: 250, DDR: 250)
    - `class_2_moderate`: Exactly 500 images (APTOS: 250, DDR: 250)
    - `class_3_severe`: Exactly 500 images (APTOS: 177, DDR: 236, IDRiD: 87)
    - `class_4_proliferative_dr`: Exactly 500 images (APTOS: 250, DDR: 250)
    - Total: Exactly 2,500 unique, genuine fundus images.
  - Implemented sequential numbering `1.ext` to `500.ext` within each class folder while preserving original filenames in manifest.
  - Preserved official train, validation, and test splits (Train: 1,886 [75.4%], Valid: 247 [9.9%], Test: 367 [14.7%]); zero leakage from validation/test into training.
  - Generated complete documentation and manifests:
    - `balanced_2500_manifest.csv` (2,500 rows with full clinical, source URL, license, split, and SHA-256 metadata)
    - `duplicate_audit.csv` (1,164 quarantined images, including DDR Grade 5 ungradables, APTOS discordant duplicates, and IDRiD conflicting pairs)
    - `source_dataset_summary.csv`
    - `class_count_summary.csv`
    - `docs/split_integrity_report.md` (and co-located in dataset folder)
    - `docs/dataset_audit_report.md` (and co-located in dataset folder)
  - Executed automated PIL two-pass verification on all 2,500 images: 100% verified readable, 0 corrupt files.
  - Preserved original datasets and existing manifests without alteration; confirmed all datasets remain Git-ignored.
- **2026-10-10 (Day 2 - Frontend & Backend Integration Milestone):**
  - Inspected complete workspace and located `drishti-ai-prototype (1).zip`.
  - Extracted prototype into `frontend/` safely without modifying existing backend assets or datasets.
  - Verified existing DRISHTI-AI backend (`FastAPI 0.115+`, SQLite persistence, image validation heuristics).
  - Confirmed AI classification model and Grad-CAM explainability modules have not been developed yet.
  - Expanded CORS allowed origins in `backend/app/main.py` to include `localhost:8080`, `localhost:5173`, `localhost:3000`, `localhost:8000`.
  - Mounted static frontend files in FastAPI at `/` for seamless single-port deployment while supporting standalone dev server.
  - Integrated `frontend/app.js` with live backend APIs:
    - Real-time `GET /health` monitoring with pulsing connectivity badge (`🟢 Backend: Connected (v0.1.0)`).
    - `POST /api/v1/screenings/upload` with progress bar, file validation, and error banner with retry controls.
    - `POST /api/v1/screenings/{id}/analyze` returning honest `model_status: "not_configured"` without fake predictions.
  - Connected technical usability heuristics (`width`, `height`, `channels`, `mean_brightness`, `contrast_std`, `heuristic_status`) with prominent non-clinical disclaimer.
  - Implemented 5-class DR architecture in the UI (`No DR`, `Mild`, `Moderate`, `Severe`, `Proliferative DR`) ready for future model weights.
  - Implemented Grad-CAM placeholder and pre-wired side-by-side comparison container for future activation maps.
  - Created automated test suite `backend/tests/test_frontend_integration.py`; achieved 21/21 passing tests (100% pass rate).
  - Executed live end-to-end HTTP integration tests with real APTOS fundus image (`002c21358ce6.png`) and verified upload (201 Created) and analysis (200 OK, honest unconfigured state).
  - Verified edge case rejections: corrupt files (400), sub-200px dimensions (400), non-image files (415).
  - Verified standalone frontend server on port 8080 and visual browser rendering.

---

## 18. Frontend & Backend Integration Details

### Architecture & Network Flow:
```
[ User Browser / Technician Dashboard ]
         │ (Port 8080 Standalone HTTP or Port 8000 Mounted)
         ▼
[ Vanilla JS Frontend: app.js + styles.css + index.html ]
         │
         ├─── GET /health ──────────────► [ Health Check & Status Pill ]
         │
         ├─── POST /api/v1/screenings/upload (Multipart)
         │    │
         │    ▼
         │    [ FastAPI Ingestion ]
         │    ├── ImageValidationService (Magic bytes, Pillow, Heuristics)
         │    └── SQLite DB (Persistent screening record)
         │
         └─── POST /api/v1/screenings/{id}/analyze
              │
              ▼
              [ Model Service Boundary (model_service.py) ]
              └── Status: 'not_configured' -> Honest Unavailable Message
```

### API Endpoints Connected:
1. `GET /health`:
   - Response: `{"status": "ok", "project": "DRISHTI-AI", "version": "0.1.0", "model_status": "not_configured", "supported_classes": ["No DR", "Mild", "Moderate", "Severe", "Proliferative DR"], "timestamp": "..."}`
   - UI Mapping: Header badge `🟢 Backend: Connected (v0.1.0)` + Model status pill `Model: Awaiting Weights`.
2. `POST /api/v1/screenings/upload`:
   - Request: `multipart/form-data` with `file: <binary>`.
   - Response: `ScreeningUploadResponse` with `screening_id`, `image_quality` heuristics, `model_status: "not_configured"`.
   - UI Mapping: Checklist items, technical heuristics table, resolution, illumination brightness, and contrast metrics.
3. `POST /api/v1/screenings/{screening_id}/analyze`:
   - Response: `ScreeningAnalyzeResponse` with `model_status: "not_configured"`, `analysis_available: false`, `prediction: null`, `gradcam_available: false`.
   - UI Mapping: Honest "Awaiting Model Weights" state, 5-class distribution list, and Grad-CAM explanation placeholder.

### Files Modified & Created:
- `backend/app/main.py`: Updated CORS allowed origins (`8080`, `5173`, `3000`, `8000`) and mounted frontend static directory at `/`.
- `frontend/index.html`: Added backend status badge, upload progress bar, error banner, 5-class distribution breakdown, and Grad-CAM comparison container.
- `frontend/styles.css`: Added styles for connectivity badge, progress animation, error alerts, heuristics table, and 5-class probability meters.
- `frontend/app.js`: Re-architected for genuine REST API communication with FastAPI, error handling, retry controls, and honest model states.
- `backend/tests/test_frontend_integration.py`: Created end-to-end integration test suite covering asset serving, CORS, real image uploads, and analysis triggers.

### Execution & Test Evidence:
1. **Automated Test Suite:**
   ```bash
   backend\.venv\Scripts\python -m pytest backend/tests
   # Result: 21 passed in 4.66s
   ```
2. **Live Backend Server Execution:**
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   # Result: Started on http://127.0.0.1:8000, database schema initialized.
   ```
3. **Live Fundus Image Upload Verification:**
   - Sample image: `datasets/aptos2019/classwise_images/class_0_no_dr/002c21358ce6.png`
   - Upload Status: `201 Created`
   - Screening ID: `30faa20b-4c1e-418c-968f-b78df4c5c10d`
   - Heuristics: Resolution `1050x1050 px`, Mean Brightness `85.5`, Contrast Std `46.5`, Heuristic Status `acceptable`.
4. **Live Inference Trigger Verification:**
   - Analysis Status: `200 OK`
   - Payload: `analysis_available: false`, `prediction: null`, `model_status: "not_configured"`.
   - Message: `"Diabetic Retinopathy AI model is not configured. Awaiting verified model weights and evaluation from AI lead (Rudra)."`
5. **Live Edge Case Validation:**
   - Non-image upload (`fake.jpg`): `HTTP 415 Unsupported Media Type`
   - Corrupted image bytes: `HTTP 400 Bad Request`
   - Sub-minimum dimensions (`100x100 px`): `HTTP 400 Bad Request`
6. **Frontend Server Execution:**
   - Command: `python -m http.server 8080 --directory frontend`
   - Browser Verification: Landing page rendered with `🟢 Backend: Connected (v0.1.0)`, interactive workspace operational.

### Missing Components & Recommended Integration Steps:
1. **Trained DR Model:**
   - Place verified weights (PyTorch `.pth` or ONNX `.onnx`) in `models/`.
   - Implement `_load_model()` and `predict()` in `backend/app/services/model_service.py`.
   - Verify class probabilities align with target 5 classes: `No DR`, `Mild`, `Moderate`, `Severe`, `Proliferative DR`.
2. **Clinical Image-Quality Gate:**
   - Integrate dedicated quality classifier (e.g. EyePACS quality model or MCF) to evaluate optic disc / macula visibility and gradeability beyond simple illumination heuristics.
3. **Grad-CAM Explainability Pipeline:**
   - Hook into the final convolutional layer of the trained model in `model_service.py:generate_gradcam()`.
   - Return JPEG bytes for overlay visualization beside original fundus photograph.

---

## 19. React + Vite + TypeScript 3D Frontend Migration Milestone

### Goal & Motivation:
Upgrade the DRISHTI-AI hackathon frontend from static prototype assets into a modern, modular **React 18 + Vite 5 + TypeScript** single-page application integrating the enhanced 3D visual language from `drishti-ai-3d-frontend.zip`, Three.js interactive WebGL fundus rendering, and componentized state management.

### Component Architecture (`frontend/src/`):
- `types/api.ts`: Typed TypeScript contracts for backend schemas (`HealthResponse`, `ImageQualityMetrics`, `ScreeningUploadResponse`, `ScreeningAnalyzeResponse`, `ScreeningRecord`).
- `services/apiService.ts`: Centralized, typed API client supporting both relative Vite proxy development and direct backend access.
- `components/Navbar.tsx`: Sticky glassmorphic navigation with live backend polling indicator (`🟢 Backend: Connected (v0.1.0)` / `🔴 Offline`) and responsive mobile menu.
- `components/Hero.tsx`: High-impact landing presentation embedding the interactive 3D RetinaViewer and primary triage action triggers.
- `components/RetinaViewer.tsx`: Interactive Three.js WebGL canvas rendering a 3D hemispherical eye fundus cup, procedural vascular branching, optic disc glow, orbital rotation, mouse/touch drag controls, and a toggleable explainability layer. Fully accessible with fallback for touch devices and `prefers-reduced-motion`.
- `components/FeatureCards.tsx`: 4 core product capability cards with CSS 3D perspective mouse tilt and elevated z-space icon geometry.
- `components/Workflow.tsx`: 5-stage clinical decision support pipeline presentation (Upload &rarr; Quality Heuristics &rarr; AI Analysis &rarr; Explainability &rarr; Clinical Review).
- `components/UploadPanel.tsx`: Interactive fundus photograph intake panel with drag-and-drop, client-side sanity checks (JPEG, PNG, WebP &le;15 MB, min 200&times;200 px), upload progress bar, error banner with retry controls, and live checklist indicators.
- `components/ResultsPanel.tsx`: Structured results dashboard presenting genuine technical usability heuristics (dimensions, illumination brightness, contrast standard deviation, aspect ratio, heuristic status), honest "Awaiting Model Weights" state, 5-class distribution breakdown, and pre-wired side-by-side Grad-CAM comparison container.
- `components/Footer.tsx`: Branding, team attribution, and prominent research disclaimer.

### 3D Visual & Interactive Features:
1. **Three.js Interactive Fundus Mesh:** 3D retinal backwall with procedural gradient shader texture, optic disc highlight, and 3D Bezier tube vasculature.
2. **Interactive Rotation & Orbit:** Users can drag or swipe to rotate the 3D retinal model in real-time.
3. **Perspective Mouse Tilt:** Panels and feature cards smoothly tilt in 3D perspective based on mouse position with cubic-bezier damping.
4. **Scroll Reveal Animations:** IntersectionObserver triggers 3D entry transitions as sections enter the viewport.
5. **Accessibility & Reduced Motion:** Touch devices and users with `prefers-reduced-motion` receive a graceful static presentation without jarring animations.

### Verification & Test Evidence:
1. **TypeScript & Bundler Build:**
   ```bash
   npm run build
   # Result: tsc && vite build -> 0 errors, built in 5.92s (dist/ generated)
   ```
2. **Backend & Bundle Test Suite:**
   ```bash
   backend\.venv\Scripts\python -m pytest backend/tests
   # Result: 20 passed in 4.92s
   ```
3. **Vite Development Server Execution:**
   - Started on `http://127.0.0.1:5173/` with proxy to backend port 8000. Verified HTTP 200.
4. **Unified FastAPI Serving Execution:**
   - FastAPI mounts `frontend/dist/` at root `/`. Verified HTTP 200 on `http://127.0.0.1:8000/`.

---

## 20. Frontend Replacement with Original Clean Prototype & 3D Implementation Removal

### Goal & Motivation:
Replace the experimental React/Vite/Three.js 3D frontend with the original, clean, non-3D frontend from `drishti-ai-prototype (1).zip`. Restore the intended lightweight, accessible prototype interface without Three.js, WebGL canvases, or 3D animations, while preserving the repository's backend, datasets, test coverage, and historical engineering logs.

### Scope of Changes:
1. **Frontend Backup:**
   - Full backup of the previous frontend directory created outside the repository before any file deletions (`scratch/backup_frontend/`).
2. **ZIP Extraction & Placement:**
   - Source archive: `drishti-ai-prototype (1).zip` (SHA256 verified).
   - Extracted and deployed to `frontend/`:
     - `frontend/index.html` (Semantic structure, hero illustration, workflow, upload & results panels)
     - `frontend/styles.css` (Clean CSS design system, responsive breakpoints, cards, status badges)
     - `frontend/app.js` (Client-side file intake, validation, preview, simulated demo workflow)
     - `frontend/README.md` (Frontend documentation and integration guide)
     - `frontend/PROJECT_BOOK.md` (Frontend prototype history)
3. **Deletions & 3D Implementation Cleanup:**
   - Removed all discarded 3D-specific directories and files:
     - `frontend/src/` (including `RetinaViewer.tsx`, `Hero.tsx`, `FeatureCards.tsx`, `Workflow.tsx`, `UploadPanel.tsx`, `ResultsPanel.tsx`, etc.)
     - `frontend/node_modules/`
     - `frontend/dist/`
     - `frontend/legacy-vanilla/`
     - `frontend/package.json`
     - `frontend/package-lock.json`
     - `frontend/tsconfig.json`
     - `frontend/tsconfig.node.json`
     - `frontend/vite.config.ts`
4. **Audit for 3D Code and Dependencies:**
   - Comprehensive audit across `frontend/` searching for `three`, `webgl`, `orbit`, `canvas`, `3d`, `fiber`, `camera`, `scene`, `geometry`, `shader`.
   - Results: **0 matches** found in the frontend deliverable.
   - Retinal graphic is an ordinary 2D SVG vector illustration with soft gradients, explicitly labeled "Illustration" and "Explainability concept · Not generated by a trained model".

### Verification & Testing Evidence:
1. **File Integrity Verification:**
   - SHA256 hashes of all 5 frontend files match the source ZIP archive with 100% fidelity.
2. **JavaScript Syntax Verification:**
   - Executed `node -c frontend/app.js` -> 0 syntax errors.
3. **Static Asset Resolution:**
   - `index.html` links correctly resolved to `styles.css` and `app.js`.
   - All section anchor IDs (`#home`, `#how-it-works`, `#features`, `#workspace`, `#integration`, `#main`) verified present.
4. **Standalone Server Execution:**
   - Ran `python -m http.server 8080 --directory frontend`.
   - Verified HTTP 200 on `http://127.0.0.1:8080/`, `styles.css` (21310 bytes), and `app.js` (9285 bytes).
5. **FastAPI Unified Static Mount:**
   - `backend/app/main.py` static mount verified serving `frontend/index.html` directly at root `/`.
6. **Backend & Integration Automated Test Suite:**
   - Ran `pytest backend/tests`: **20 passed in 3.36s** (`test_api.py` and `test_frontend_integration.py`).
7. **Medical AI Honesty Verification:**
   - Reconfirmed that diabetic retinopathy classification model is **not yet developed**.
   - Live upload checks perform browser-side dimension checks, showing honest `Model not connected` and `Not available` states without fabricating confidence numbers or lesion detections.
   - Sample flow explicitly stamped `SIMULATED DEMO` with prominent disclaimers.

### Next Steps for Model & Explainability Integration:
1. AI lead (Rudra) delivers validated DR classification model weights (5-class: No DR, Mild, Moderate, Severe, Proliferative DR).
2. Wire `_load_model()` in `backend/app/services/model_service.py`.
3. Connect Grad-CAM hook to the final convolutional layer of the trained architecture.
4. Update frontend to consume real predictions from `POST /api/v1/screenings/{id}/analyze`.

---

## 21. Temporary Starter Frontend Removal for Ashwidha Handoff

### Goal & Motivation:
Remove the five starter prototype frontend files from `frontend/` via standard Git deletion so that Ashwidha (Frontend Lead) has a clean slate to commit and push her standalone frontend repository/code without merge conflicts or clobbering.

### Scope & Preservation:
1. **Frontend Files Removed via Git Deletion:**
   - `frontend/index.html`
   - `frontend/styles.css`
   - `frontend/app.js`
   - `frontend/README.md`
   - `frontend/PROJECT_BOOK.md`
   - Preserved `frontend/.gitkeep` so the `frontend/` directory remains tracked and ready for Ashwidha's push.
2. **Model Assets Strictly Preserved:**
   - `models/DRISHTI_1.ipynb` (Rudra's model development notebook, 5,539,474 bytes)
   - `models/RetinaExplain_AI_v2_final.keras` (Rudra's trained model artifact, 17,112,541 bytes)
   - Zero changes made to `models/`.
3. **Backend & Architecture Intact:**
   - FastAPI application, SQLite database, services, and API endpoints preserved.
   - `backend/tests/test_api.py`: 14/14 core API and validation tests passed.
   - Frontend static serving tests in `test_frontend_integration.py` return expected HTTP 404 while frontend assets are intentionally absent, awaiting Ashwidha's incoming build.
4. **Standalone Reference Package:**
   - Clean starter frontend deliverable preserved in `drishti-ai-normal-frontend.zip` for Ashwidha's reference if needed.

---

## 22. Milestone: Full-Stack Integration Complete (Frontend, FastAPI, SQLite, Keras 3 Model & Grad-CAM)

### Overview & Objectives Achieved:
Successfully unified the full DRISHTI-AI application into a cohesive, locally runnable medical AI screening-support system:
1. **Ashwidha's Frontend:** Preserved clean HTML5/CSS3/Vanilla JS interface (no 3D/Three.js overhead), connected all API endpoints, added real-time backend and model readiness indicators, 5-class probability visualization, genuine Grad-CAM heatmap viewer, and interactive SQLite session history table.
2. **FastAPI Backend:** Expanded endpoints to safely store uploaded images locally under path-traversal-guarded UUID filenames, invoke real model inference, persist results, and serve Grad-CAM overlays via `GET /api/v1/screenings/{screening_id}/gradcam`.
3. **SQLite Database:** Enhanced `database.py` with `update_screening_analysis()` to persist predicted class, confidence, JSON-serialized class probabilities, and Grad-CAM availability directly against existing records without row duplication.
4. **Keras Model Service:** Verified and loaded `models/RetinaExplain_AI_v2_final.keras` once on startup with `compile=False`.
5. **Grad-CAM Explainability:** Implemented genuine activation mapping using `tf.GradientTape` on the backbone `top_activation` convolutional layer, overlaying a Jet colormap on the original RGB fundus image.
6. **Automated & E2E Testing:** Expanded test suite from 20 to 26 passing tests with zero regressions; validated with real dataset fundus images from APTOS 2019.

### 1. Python Environment & Dependency Verification
- **Python Runtime:** Python 3.13.0rc3 (`backend\.venv\Scripts\python.exe`)
- **Key Installed Packages:**
  - `tensorflow==2.21.0`
  - `keras==3.15.1`
  - `numpy==2.5.3`
  - `h5py==3.14.0`
  - `pillow==12.1.1`
  - `fastapi==0.115.12`
  - `uvicorn==0.34.0`
  - `pytest==9.1.1`
- **Dependency Tracking:** Updated `backend/requirements.txt` with compatible versions.

### 2. Model Audit & Architecture Verification
- **Artifact:** `models/RetinaExplain_AI_v2_final.keras` (17,112,541 bytes)
- **Source Notebook:** `models/DRISHTI_1.ipynb`
- **Architecture Details:**
  - Backbone: `efficientnetb0` (ImageNet pre-trained)
  - Head: `GlobalAveragePooling2D` -> `Dropout(0.3)` -> `Dense(5, activation="softmax")`
  - Input Shape: `(1, 224, 224, 3)` RGB float32
  - Preprocessing Rule: EfficientNetB0 incorporates internal rescaling/normalization layers. Input values must remain in `[0, 255]` float32 range (do not divide by 255 twice).
  - Target Classes (Verified Index Order from Notebook):
    - `0: No DR` (`class_0_no_dr`)
    - `1: Mild` (`class_1_mild`)
    - `2: Moderate` (`class_2_moderate`)
    - `3: Severe` (`class_3_severe`)
    - `4: Proliferative DR` (`class_4_proliferative_dr`)
  - Reported Experimental Metrics: 73.31% Test Accuracy, 73.97% Validation Accuracy (treated strictly as experimental prototype metric, not proof of clinical efficacy).

### 3. Grad-CAM Implementation Architecture
- **Target Convolutional Layer:** `top_activation` (the final activation stage of the EfficientNetB0 backbone before global average pooling).
- **Submodel Extraction:** Created a functional submodel `keras.Model(inputs=backbone.input, outputs=top_conv.output)` chained through the classification head layers (`gap`, `dropout`, `dense`) inside `tf.GradientTape`.
- **Computation Pipeline:**
  1. Record forward pass and extract feature maps $A^k$ and predicted class score $y^c$.
  2. Compute gradients $\frac{\partial y^c}{\partial A^k}$.
  3. Global average pool gradients to obtain neuron importance weights $\alpha_k^c$.
  4. Compute weighted sum $\sum_k \alpha_k^c A^k$, apply ReLU, and normalize to $[0, 1]$.
  5. Upsample 2D heatmap to original input resolution using bilinear interpolation.
  6. Map through Jet colormap and blend 60/40 alpha with the original RGB fundus image.
  7. Encode as standard PNG bytes and cache in local storage alongside the screening ID.

### 4. Storage & SQLite Persistence Architecture
- **Storage Service (`backend/app/services/image_service.py`):**
  - Configurable directory via `DRISHTI_UPLOAD_DIR` (defaults to `backend/uploads`).
  - Strict path-traversal protection: Filenames are derived strictly from screening UUID (`<screening_id>.<ext>` and `<screening_id>_gradcam.png`). Client-supplied filenames are never used as filesystem paths.
  - Automatic rollback/cleanup: Partial upload files are removed if database insertion fails.
- **Database Service (`backend/app/database.py`):**
  - Retains existing schema in `screenings` table.
  - Added `update_screening_analysis(screening_id, prediction, confidence, class_probabilities_json, gradcam_available)` to record inference results without creating duplicate rows.

### 5. API Endpoints Contract
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System status, model status (`ready`), model name, supported classes |
| `POST` | `/api/v1/screenings/upload` | Multipart image upload, technical usability validation, safe disk caching, SQLite record creation |
| `POST` | `/api/v1/screenings/{screening_id}/analyze` | Triggers model inference, Grad-CAM generation, and SQLite record update |
| `GET` | `/api/v1/screenings/{screening_id}/gradcam` | Serves genuine Grad-CAM PNG heatmap overlay |
| `GET` | `/api/v1/screenings/{screening_id}` | Retrieves full screening record including prediction and usability flags |
| `GET` | `/api/v1/screenings?page=1&page_size=20` | Paginated listing of all historical screenings |

### 6. Automated Testing Results
- **Pytest Suite (`backend/tests`):** **26 passed in 22.68s**
  - `backend/tests/test_api.py` (15 tests): Health check, image validation, upload flows, model unavailable handling, corrupt input rejection.
  - `backend/tests/test_frontend_integration.py` (6 tests): Frontend index serving, styles, JavaScript, API base connectivity, CORS headers.
  - `backend/tests/test_model_service.py` (5 tests): Real model loading, preprocessing, 5-class output validation, genuine Grad-CAM generation, and missing image error handling.
- **Real E2E Dataset Validation:**
  - Tested with `datasets/aptos2019/classwise_images/class_0_no_dr/002c21358ce6.png`:
    - Prediction: `No DR` (74.89% confidence)
    - Grad-CAM: Generated PNG overlay (988,073 bytes)
  - Tested with `datasets/aptos2019/classwise_images/class_4_proliferative_dr/001639a390f0.png`:
    - Prediction: `Moderate` (47.86%) / `Proliferative DR` (39.86%), `No DR` (0.53%)
    - Grad-CAM: Generated PNG overlay successfully

### 7. Local Startup Commands (Windows PowerShell)
```powershell
# Option 1: Unified Application (Serves Frontend + API on Port 8000)
cd D:\drishti-ai
.\backend\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend

# Option 2: Standalone Static Dev Server (Port 8080) with Backend on Port 8000
# Terminal 1 (Backend):
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend
# Terminal 2 (Frontend):
python -m http.server 8080 --directory frontend
```

### 8. Clinical & Regulatory Guardrails
- **Honest Metrics:** Test accuracy is documented as 73.31% (experimental prototype).
- **Mandatory Disclaimer:** Displayed prominently on both frontend and backend documentation stating DRISHTI-AI is for research/triage support only and is not a certified medical device.
- **Usability Heuristics:** Stamped as preliminary technical checks, not clinically certified image quality assurance.

---

## 23. Milestone: Final Live Integration Verification & E2E Validation (Phases 1–12)

### 1. Final Inspection & Environment Audit (Phases 1 & 2)
- **Workspace:** `D:\drishti-ai` (branch: `main`).
- **Verified Backups & Model Files:**
  - `models/DRISHTI_1.ipynb` (5,539,474 bytes)
  - `models/RetinaExplain_AI_v2_final.keras` (17,112,541 bytes)
  - Preserved `.bak` files: `database.py.bak`, `model_service.py.bak`, `screenings.py.bak`, `app.js.bak`, `index.html.bak` (safely ignored by `.gitignore`).
- **Runtime Environment:**
  - Python: `3.13.0rc3`
  - TensorFlow: `2.21.0`
  - Keras: `3.15.1`
  - NumPy: `2.5.3`
  - Pillow: `12.3.0`
  - FastAPI: `0.143.0`
  - Uvicorn: `0.54.0`
  - Pytest: `9.1.1`
- **Model Architecture & Mapping:**
  - Input: `(None, 224, 224, 3)` RGB float32 in range `[0, 255]`.
  - Output: `(None, 5)` softmax probabilities.
  - Verified class order: `0: No DR`, `1: Mild`, `2: Moderate`, `3: Severe`, `4: Proliferative DR`.

### 2. Live Application Startup (Phase 3)
- Launched unified service: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend`.
- Verified endpoints:
  - `http://127.0.0.1:8000/` -> HTTP 200 (served Ashwidha's frontend `index.html`).
  - `http://127.0.0.1:8000/health` -> HTTP 200 (`model_status: "ready"`).
  - `http://127.0.0.1:8000/docs` -> HTTP 200 (Swagger OpenAPI UI).

### 3. Frontend Browser Verification (Phase 4)
- **UI & Layout:** Original clean, non-3D interface loaded without errors.
- **Status Indicators:** "Backend online" and "Model ready (5-class)" badges dynamically rendered.
- **Responsiveness:** Tested and verified across desktop (1280x800) and mobile (375x812) viewports.
- **Console Inspection:** 0 JavaScript or CSS console errors detected.

### 4. Real Live End-to-End Test Results (Phases 5–8)
Tested against live running server with real dataset images from `datasets/aptos2019/classwise_images/`:
- **Image 1 (`class_0_no_dr/002c21358ce6.png`):**
  - `POST /api/v1/screenings/upload` -> HTTP 201 (`screening_id: "bf54b9cc-714a-4c34-bc02-1c130b9b532e"`).
  - Usability heuristics extracted: Width: 1050, Height: 1050, Mean brightness: 85.5, Contrast: 46.5, Status: `acceptable`.
  - Local disk storage: `backend/uploads/bf54b9cc-714a-4c34-bc02-1c130b9b532e.png` (975,218 bytes).
  - SQLite persistence: Row created in `screenings` table with `validation_passed = 1`.
  - `POST /api/v1/screenings/bf54b9cc-714a-4c34-bc02-1c130b9b532e/analyze` -> HTTP 200.
    - Prediction: `No DR` (74.89% confidence).
    - Probabilities: No DR (0.7489), Mild (0.1784), Moderate (0.0555), Severe (0.0125), Proliferative DR (0.0047).
  - `GET /api/v1/screenings/bf54b9cc-714a-4c34-bc02-1c130b9b532e/gradcam` -> HTTP 200 (`image/png`, 988,073 bytes, dimensions 1050x1050 matching original).
- **Image 2 (`class_4_proliferative_dr/001639a390f0.png`):**
  - `POST /api/v1/screenings/upload` -> HTTP 201 (`screening_id: "df330b7e-edfb-49f7-9453-d9865f7cac9d"`).
  - `POST /api/v1/screenings/df330b7e-edfb-49f7-9453-d9865f7cac9d/analyze` -> HTTP 200.
    - Prediction: `Moderate` (47.86%) / `Proliferative DR` (39.86%), `No DR` (0.53%).
  - `GET /api/v1/screenings/df330b7e-edfb-49f7-9453-d9865f7cac9d/gradcam` -> HTTP 200 (`image/png`, 2,955,274 bytes, dimensions 3216x2136 matching original).
- **Idempotency & History:**
  - Repeated analysis of same screening ID updated record in place without duplicate row creation.
  - `GET /api/v1/screenings?page=1&page_size=20` correctly returned all screenings in pagination.
  - Unknown UUID returned HTTP 404; non-image upload returned HTTP 415.

### 5. Automated Pytest Suite Results (Phase 9)
Ran verbose pytest command: `.\backend\.venv\Scripts\python.exe -m pytest backend\tests -v`
- **Result:** **26 passed in 67.01s (0:01:07)** with 0 failures:
  - `backend/tests/test_api.py`: 15 passed
  - `backend/tests/test_frontend_integration.py`: 6 passed
  - `backend/tests/test_model_service.py`: 5 passed

### 6. Git Review & Strict Non-Commit Compliance (Phase 12)
- Working tree checked with `git status`.
- Zero staged files, zero commits created, zero pushes.
- All integration and test verification changes kept local for review.




