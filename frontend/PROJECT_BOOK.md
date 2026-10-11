# DRISHTI-AI Frontend — Engineering Log

**Lead:** Ashwidha (Frontend Lead, Team SPARK)

---

## Milestone 1: Interactive Technician Workspace Prototype
- Created semantic HTML5 structure in `index.html`.
- Designed responsive layout, healthcare color tokens, and interactive cards in `styles.css`.
- Built client-side drag-and-drop, image preview, and basic file dimension validation in `app.js`.

---

## Milestone 2: Full-Stack FastAPI & Grad-CAM Integration
- Configured dynamic API base resolution supporting unified serving (`/`), local standalone dev (`http://127.0.0.1:8000`), and configurable endpoints.
- Integrated `/health` status polling: displays real-time **Backend online** and **Model ready (5-class)** pills.
- Connected image upload to `POST /api/v1/screenings/upload`.
- Implemented deep-learning inference trigger via `POST /api/v1/screenings/{id}/analyze`.
- Rendered 5-class severity stage, confidence percentage, and horizontal probability distribution bars.
- Integrated Grad-CAM explainability viewer: renders side-by-side fundus scan alongside the blended Jet colormap activation heatmap overlay from `GET /api/v1/screenings/{id}/gradcam`.
- Connected screening history table: dynamically fetches and renders past screenings from `GET /api/v1/screenings`.
