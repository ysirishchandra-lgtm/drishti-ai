# DRISHTI-AI REST API Contract (v1)

**Team:** SPARK  
**Base URL:** `http://127.0.0.1:8000`  
**Frontend Dev Server:** `http://localhost:5173`  
**Authentication:** Public prototype (Local clinic intranet mode)  
**Standard Header:** `Accept: application/json`  

---

## 1. System Endpoints

### 1.1 Health Check & Model Readiness
Check backend health, API version, and whether the AI model weights are loaded.

- **Method:** `GET`
- **Path:** `/health`
- **Response Headers:** `Content-Type: application/json`
- **Status Code:** `200 OK`

#### Response Body:
```json
{
  "status": "ok",
  "project": "DRISHTI-AI",
  "version": "0.1.0",
  "model_status": "not_configured",
  "model_name": null,
  "supported_classes": [
    "No DR",
    "Mild",
    "Moderate",
    "Severe",
    "Proliferative DR"
  ],
  "timestamp": "2026-10-09T08:50:00.000000Z"
}
```

---

## 2. Screening Endpoints

### 2.1 Upload & Ingest Retinal Fundus Image
Uploads an image, enforces size and format checks, computes preliminary usability metrics, and creates a screening record.

- **Method:** `POST`
- **Path:** `/api/v1/screenings/upload`
- **Content-Type:** `multipart/form-data`
- **Request Form Field:**
  - `file`: Binary file upload (JPEG, PNG, or WebP. Max size: 15 MB. Min dimensions: 200x200 px).

#### Success Response (`201 Created`):
```json
{
  "screening_id": "a3b84f91-7299-4674-8b5e-f0dc2a819b12",
  "created_at": "2026-10-09T08:51:12.345678Z",
  "file_name": "patient_fundus_001.jpg",
  "file_size_bytes": 1048576,
  "mime_type": "image/jpeg",
  "validation_passed": true,
  "image_quality": {
    "width": 1024,
    "height": 1024,
    "format": "JPEG",
    "channels": 3,
    "aspect_ratio": 1.0,
    "mean_brightness": 118.42,
    "contrast_std": 42.15,
    "heuristic_status": "acceptable",
    "rejection_reasons": [],
    "disclaimer": "Preliminary technical usability heuristics only. Not a clinically validated image quality evaluation."
  },
  "model_status": "not_configured",
  "human_review_status": "pending",
  "follow_up_status": "none",
  "message": "Image successfully verified and usability heuristics extracted."
}
```

#### Error Responses:
- **`400 Bad Request`** (Corrupt image or dimensions too small):
  ```json
  {
    "detail": "Uploaded file is corrupted or could not be decoded as a valid image."
  }
  ```
- **`413 Request Entity Too Large`** (Exceeds 15 MB):
  ```json
  {
    "detail": "Uploaded image exceeds maximum allowable limit of 15 MB."
  }
  ```
- **`415 Unsupported Media Type`** (Non-image / unsupported format):
  ```json
  {
    "detail": "Unsupported or unrecognized file format. Allowed formats are JPEG, PNG, and WebP."
  }
  ```

---

### 2.2 Trigger Screening Analysis
Triggers AI inference for an uploaded image. If no verified model is loaded, clearly returns `model_status: "not_configured"` without fabricating fake medical results.

- **Method:** `POST`
- **Path:** `/api/v1/screenings/{screening_id}/analyze`
- **Status Code:** `200 OK`

#### Response When Model is Not Configured (Current Baseline):
```json
{
  "screening_id": "a3b84f91-7299-4674-8b5e-f0dc2a819b12",
  "model_status": "not_configured",
  "analysis_available": false,
  "prediction": null,
  "confidence": null,
  "class_probabilities": null,
  "gradcam_available": false,
  "gradcam_url": null,
  "message": "Diabetic Retinopathy AI model is not configured. Awaiting verified model weights and evaluation from AI lead (Rudra)."
}
```

#### Response When Verified Model is Loaded (Future Contract for Rudra):
```json
{
  "screening_id": "a3b84f91-7299-4674-8b5e-f0dc2a819b12",
  "model_status": "ready",
  "analysis_available": true,
  "prediction": "Moderate",
  "confidence": 0.874,
  "class_probabilities": {
    "No DR": 0.021,
    "Mild": 0.075,
    "Moderate": 0.874,
    "Severe": 0.024,
    "Proliferative DR": 0.006
  },
  "gradcam_available": true,
  "gradcam_url": "/api/v1/screenings/a3b84f91-7299-4674-8b5e-f0dc2a819b12/gradcam",
  "message": "Inference successfully completed using verified checkpoint."
}
```

#### Error Response:
- **`404 Not Found`**:
  ```json
  {
    "detail": "Screening record 'a3b84f91-7299-4674-8b5e-f0dc2a819b12' not found."
  }
  ```

---

### 2.3 Retrieve Specific Screening Record
Fetches the persistent screening details, quality flags, and analysis history.

- **Method:** `GET`
- **Path:** `/api/v1/screenings/{screening_id}`
- **Status Code:** `200 OK`

#### Response:
```json
{
  "screening_id": "a3b84f91-7299-4674-8b5e-f0dc2a819b12",
  "created_at": "2026-10-09T08:51:12.345678Z",
  "file_name": "patient_fundus_001.jpg",
  "file_size_bytes": 1048576,
  "mime_type": "image/jpeg",
  "validation_passed": true,
  "image_quality": {
    "width": 1024,
    "height": 1024,
    "format": "JPEG",
    "channels": 3,
    "aspect_ratio": 1.0,
    "mean_brightness": 118.42,
    "contrast_std": 42.15,
    "heuristic_status": "acceptable",
    "rejection_reasons": [],
    "disclaimer": "Preliminary technical usability heuristics only. Not a clinically validated image quality evaluation."
  },
  "model_status": "not_configured",
  "analysis_available": false,
  "prediction": null,
  "confidence": null,
  "class_probabilities": null,
  "gradcam_available": false,
  "human_review_status": "pending",
  "follow_up_status": "none",
  "notes": null
}
```

---

### 2.4 List Historical Screening Records
Lists screening records with pagination, ordered newest to oldest.

- **Method:** `GET`
- **Path:** `/api/v1/screenings?page=1&page_size=20`
- **Query Parameters:**
  - `page` (optional integer, default `1`, min `1`)
  - `page_size` (optional integer, default `20`, min `1`, max `100`)
- **Status Code:** `200 OK`

#### Response:
```json
{
  "total": 1,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "screening_id": "a3b84f91-7299-4674-8b5e-f0dc2a819b12",
      "created_at": "2026-10-09T08:51:12.345678Z",
      "file_name": "patient_fundus_001.jpg",
      "file_size_bytes": 1048576,
      "mime_type": "image/jpeg",
      "validation_passed": true,
      "image_quality": {
        "width": 1024,
        "height": 1024,
        "format": "JPEG",
        "channels": 3,
        "aspect_ratio": 1.0,
        "mean_brightness": 118.42,
        "contrast_std": 42.15,
        "heuristic_status": "acceptable",
        "rejection_reasons": [],
        "disclaimer": "Preliminary technical usability heuristics only. Not a clinically validated image quality evaluation."
      },
      "model_status": "not_configured",
      "analysis_available": false,
      "prediction": null,
      "confidence": null,
      "class_probabilities": null,
      "gradcam_available": false,
      "human_review_status": "pending",
      "follow_up_status": "none",
      "notes": null
    }
  ]
}
```

---

### 2.5 Retrieve Grad-CAM Heatmap Activation Overlay
Serves the binary PNG activation heatmap overlay generated during screening analysis. Blends the original fundus photograph with a Jet colormap activation map (60% fundus / 40% heatmap).

- **Method:** `GET`
- **Path:** `/api/v1/screenings/{screening_id}/gradcam`
- **Response Header:** `Content-Type: image/png`
- **Status Code:** `200 OK`

#### Error Responses:
- **`404 Not Found`** (Screening record does not exist or Grad-CAM overlay was not generated):
  ```json
  {
    "detail": "Grad-CAM explanation heatmap is not available for screening '{id}'."
  }
  ```

---

## 3. Frontend Integration Guide (for Ashwidha)

### 3.1 Environment & Network Setup
- **Backend Base URL:** `http://127.0.0.1:8000`
- **Supported Frontend Origins (CORS Allowed):**
  - `http://localhost:5173`
  - `http://127.0.0.1:5173`

### 3.2 Frontend Quick-Start Commands (Vite + React)
In a new terminal, Ashwidha can initialize and launch her Vite frontend inside `frontend/`:
```bash
# 1. Navigate to frontend folder
cd frontend

# 2. Initialize Vite + React project (if not already done)
npm create vite@latest . -- --template react

# 3. Install dependencies
npm install
npm install axios lucide-react   # Recommended for API calls & healthcare icons

# 4. Start local development server (runs on port 5173)
npm run dev
```

### 3.3 Image Upload Specifications
- **Field Name:** Must be sent as `file` in `multipart/form-data`.
- **Accepted Formats:** JPEG (`.jpg`, `.jpeg`), PNG (`.png`), WebP (`.webp`).
- **Maximum File Size:** 15 MB (Server returns HTTP 413 `CONTENT_TOO_LARGE` if exceeded).
- **Minimum Dimensions:** 200 x 200 pixels (Server returns HTTP 400 `DIMENSIONS_TOO_SMALL` if smaller).

### 3.4 Uploading from React / Axios
```javascript
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

export async function uploadFundusImage(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post(`${API_BASE}/api/v1/screenings/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data; // Returns ScreeningUploadResponse
}
```

### 3.5 Handling Quality Heuristics in UI
When an image is uploaded, inspect `response.data.image_quality`:
- `heuristic_status === "acceptable"`: Display green badge: "Image Quality Passed (Preliminary Heuristic)".
- `heuristic_status === "borderline"`: Display yellow badge: "Illumination Warning" and list items from `rejection_reasons` (e.g. low contrast or dark image).
- `heuristic_status === "unusable"`: Display warning advising technician to recapture photograph.
- Always include disclaimer note: *"Preliminary technical usability heuristics only. Not a clinically certified quality evaluation."*

### 3.6 Handling AI Model Status (`not_configured`)
- When triggering `POST /api/v1/screenings/{screening_id}/analyze`, inspect `response.data.model_status`.
- **Current Baseline:** `model_status: "not_configured"`, `analysis_available: false`.
- **UI Presentation:** Show an info banner:
  > **AI Screening Model Verification in Progress**  
  > The deep-learning classification pipeline is currently awaiting verified clinical model weights. Technician triage and image quality checks remain fully active.
- **Strict Clinical Integrity:** Never mock or fabricate confidence percentages or DR severity stages when `model_status` is not `"ready"`.

### 3.7 Error Handling Matrix for UI Toast / Alerts
| HTTP Status | Error Detail Example | Recommended UI Message |
|---|---|---|
| `400 Bad Request` | `"Uploaded file is corrupted or could not be decoded..."` | *"The selected file is corrupted or could not be decoded. Please select a valid image."* |
| `400 Bad Request` | `"Image dimensions (150x150 px) are smaller than required minimum..."` | *"Image resolution is too low. Please upload an image at least 200x200 pixels."* |
| `413 Content Too Large` | `"Uploaded image exceeds maximum allowable limit of 15 MB."` | *"Image file size exceeds the 15 MB limit. Please compress or select a smaller image."* |
| `415 Unsupported Media Type` | `"Unsupported or unrecognized file format. Allowed formats are JPEG, PNG, and WebP."` | *"Unsupported file format. Please upload a JPEG, PNG, or WebP fundus photograph."* |
| `404 Not Found` | `"Screening record '{id}' not found."` | *"Screening session not found or expired. Please re-upload the image."* |
| `500 Server Error` | `"An internal server error occurred..."` | *"Server encountered an issue. Please verify backend connection and try again."* |
