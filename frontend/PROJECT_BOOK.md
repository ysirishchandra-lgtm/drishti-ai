# DRISHTI-AI Project Book

## Step 1 — Interactive frontend prototype

**Goal:** Turn the static landing-page idea into a responsive, runnable website skeleton.

**Files created:**
- `index.html` — semantic page structure, navigation, landing page, workflow, upload panel, and results panel.
- `styles.css` — responsive layout, typography, colors, cards, uploader, results states, and mobile navigation styles.
- `app.js` — local file handling, preview, basic dimension checks, sample-demo state, result state, drag-and-drop, and menu behavior.
- `README.md` — run/deploy notes and integration plan.

**What works:**
- Select or drop PNG/JPG/WebP files up to 15 MB.
- Preview and remove the selected image.
- Check browser image readability and whether dimensions are at least 256 × 256 pixels.
- Display an explicit “model not connected” state rather than making predictions about an uploaded image.
- Open a separate static sample flow labelled “SIMULATED DEMO.”

**Important limitations:** No trained model, clinical image-quality gate, API, database, or Grad-CAM implementation is included. The sample result is static UI demonstration data only.

**How to run:** Open `index.html` in a modern browser, or run `python -m http.server 8080` from this directory and visit `http://localhost:8080`.

**Next step:** Connect the actual DR model/backend and wire its validated response into the result panel. Add tests and end-to-end validation before presenting this as a working screening system.
