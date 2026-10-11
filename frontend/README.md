# DRISHTI-AI — Frontend Application

**Responsive Technician Screening Interface for Diabetic Retinopathy Triage**  
**Lead:** Ashwidha (Frontend Lead, Team SPARK)

---

## Overview

The DRISHTI-AI frontend is a lightweight, responsive web application designed for primary healthcare workers and vision center technicians in rural India. It provides a distraction-free, accessible interface for capturing/uploading fundus photographs, inspecting automated usability heuristics, triggering deep learning inference, visualizing Grad-CAM explainability heatmaps, and exploring previous screening records.

---

## Implemented Features

- **Responsive Landing & Workspace:** Optimized for desktop screens and tablet/mobile viewports.
- **Fundus Image Drag-and-Drop:** Intuitive file drop-zone supporting JPEG, PNG, and WebP formats up to 15 MB.
- **Client & Server Usability Checks:** Live feedback on image decodability, minimum resolution (>=200×200 px), brightness, and contrast.
- **Real-Time Backend & Model Health Indicators:** Live status badges in the top navigation tracking backend connectivity and 5-class model readiness (`ready`).
- **5-Class Prediction & Confidence Display:** Visualizes predicted DR stage (*No DR*, *Mild*, *Moderate*, *Severe*, *Proliferative DR*) along with granular probability distribution bars.
- **Side-by-Side Grad-CAM Explainability:** Renders a genuine Jet colormap activation heatmap overlay atop the original fundus photograph.
- **SQLite Screening History:** Dynamically renders historical screening records retrieved via `GET /api/v1/screenings`.
- **Graceful Fallback Mode:** When running without a live backend configured, clearly informs the operator with a non-connected indicator rather than failing silently.

---

## Running Locally

### Option 1: Unified via FastAPI (Recommended)
When you start the FastAPI backend, it automatically serves this frontend at the root URL:
```powershell
# From repository root:
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

### Option 2: Standalone Static Server
You can also serve the frontend independently:
```powershell
# From repository root:
python -m http.server 8080 --directory frontend
```
Open [http://127.0.0.1:8080](http://127.0.0.1:8080). The client automatically connects to the FastAPI backend running on port 8000 via CORS.

---

## File Structure

```
frontend/
├── index.html                   # Semantic markup, navigation, hero, screening workspace
├── styles.css                   # Custom responsive styles, design tokens, color palette
├── app.js                       # Asynchronous API integration, drag-and-drop, UI state handling
├── eye-hero-poster.jpg          # Visual asset for hero banner
├── drishti-hero-cinematic.jpg   # High-resolution clinical illustration
├── assets/
│   ├── drishti-hero-cinematic.jpg
│   └── drishti-intro.mp4        # Hackathon intro video walkthrough
├── README.md                    # This file
└── PROJECT_BOOK.md              # Frontend engineering notes
```

---

## Clinical Notice
This frontend interface is part of an experimental screening-support research prototype. It does not provide clinical diagnosis and is intended solely for demonstration and research evaluation.
