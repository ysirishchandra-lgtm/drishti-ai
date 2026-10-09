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

## 3. Frontend Integration Guide (for Ashwidha)

1. **Base URL:** Set API base to `http://127.0.0.1:8000`.
2. **Uploading Images:** Use `FormData` with key name `file`:
   ```javascript
   const formData = new FormData();
   formData.append('file', selectedFile);
   const res = await axios.post('http://127.0.0.1:8000/api/v1/screenings/upload', formData, {
     headers: { 'Content-Type': 'multipart/form-data' }
   });
   ```
3. **Model Readiness:** The frontend can check `res.data.model_status`. When `not_configured`, display a banner:  
   *"AI Model Verification in Progress — Clinical Quality Review Active"*.
4. **Error Handling:** Check `error.response.data.detail` to display friendly alerts for oversized images (413) or unsupported formats (415).
