# DRISHTI-AI — Interactive Frontend Prototype

This is a responsive, browser-runnable website prototype based on the DRISHTI-AI mockup.

## What works now
- Responsive landing page and mobile navigation
- Fundus image file selection, drag-and-drop, preview, and removal
- Supported format and 15 MB file-size checks
- Browser-side image readability and minimum-dimension checks
- Empty state, real-image check state, and a clearly labeled static sample-demo state
- No upload request: the chosen image stays in the browser

## What is not connected yet
- No trained diabetic-retinopathy model or inference API
- No clinical-quality gate
- No Grad-CAM generation
- No database, login, patient record storage, or deployment configuration

The sample `Moderate DR` label is static placeholder data for visualizing the result UI. It is not inferred from an image and must never be used for medical decisions. The browser checks only tell whether the file can be opened and whether its pixel dimensions pass a simple threshold; they are not medical image-quality checks.

## Run locally

You can open `index.html` directly in a modern browser. For a local web server, from this folder run:

```bash
python -m http.server 8080
```

Then open `http://localhost:8080`.

## Deploy a static demo

This is a static site. Upload the project folder to a Git repository and import it into a static hosting service such as Vercel. Use the project root as the root directory; no build command is required, and the output directory is the root (`.`).

## Connecting a real model later

A backend endpoint should accept the image and return validated structured data such as:

```json
{
  "request_id": "example-id",
  "quality_gate": { "status": "pass", "reason": "..." },
  "prediction": {
    "class": "moderate",
    "probabilities": {
      "no_dr": 0.0,
      "mild": 0.0,
      "moderate": 0.0,
      "severe": 0.0,
      "pdr": 0.0
    }
  },
  "explainability": { "heatmap_url": null },
  "model_version": "your-model-version"
}
```

The values above are schema examples only—not model results. The frontend should show model version, uncertainty/quality failures, and a clear research-only disclaimer. Do not present the system as clinically validated without appropriate clinical evaluation and regulatory review.
