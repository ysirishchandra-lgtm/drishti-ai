// DRISHTI-AI Full-Stack Frontend Integration
// Connects Ashwidha's UI to FastAPI backend, SQLite persistence, Keras model, and Grad-CAM

function getApiBase() {
  if (typeof window === 'undefined') return null;

  // 1. Explicit window runtime variable (configured via window.DRISHTI_API_BASE)
  if (window.DRISHTI_API_BASE) {
    return String(window.DRISHTI_API_BASE).replace(/\/+$/, '');
  }

  // 2. Query param override (?api_base=https://...)
  try {
    const params = new URLSearchParams(window.location.search);
    const paramBase = params.get('api_base') || params.get('backend_url');
    if (paramBase) {
      localStorage.setItem('drishti_api_base', paramBase);
      return paramBase.replace(/\/+$/, '');
    }
  } catch (e) {}

  // 3. Persistent localStorage configuration
  try {
    const stored = localStorage.getItem('drishti_api_base');
    if (stored) return stored.replace(/\/+$/, '');
  } catch (e) {}

  // 4. Local development detection (only on localhost, 127.0.0.1, or 0.0.0.0)
  const isLocalHost = window.location.hostname === 'localhost' ||
                      window.location.hostname === '127.0.0.1' ||
                      window.location.hostname === '0.0.0.0';

  if (isLocalHost) {
    if (window.location.port !== '8000') {
      return `http://${window.location.hostname}:8000`;
    }
    return window.location.origin;
  }

  // 5. In static cloud deployments (e.g. Vercel), do NOT default to 127.0.0.1
  // Return null to avoid mixed-content or unroutable connection errors
  return null;
}

const API_BASE = getApiBase();

const $ = (selector) => document.querySelector(selector);
const fileInput = $('#fileInput');
const dropZone = $('#dropZone');
const filePreview = $('#filePreview');
const uploadedPreview = $('#uploadedPreview');
const analyzeButton = $('#analyzeButton');
const runInferenceBtn = $('#runInferenceBtn');
const resultEmpty = $('#resultEmpty');
const resultContent = $('#resultContent');
const toast = $('#toast');

let currentFile = null;
let currentObjectUrl = null;
let currentImageDimensions = null;
let currentScreeningId = null;
let toastTimer = null;

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 3500);
}

function formatBytes(bytes) {
  if (!bytes) return '0 B';
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function setCheckRow(index, status, message) {
  const row = document.querySelectorAll('.check-row')[index];
  if (!row) return;
  const indicator = row.querySelector('.check-indicator');
  const small = row.querySelector('small');
  const state = row.querySelector('.check-state');
  indicator.className = `check-indicator ${status}`;
  indicator.textContent = status === 'pass' ? '✓' : status === 'warn' ? '!' : String(index + 1);
  small.textContent = message;
  state.textContent = status === 'pass' ? 'Passed' : status === 'warn' ? 'Review' : 'Pending';
  state.style.color = status === 'pass' ? '#0d9877' : status === 'warn' ? '#b47715' : '';
}

function resetResult() {
  resultEmpty.classList.remove('hidden');
  resultContent.classList.add('hidden');
  $('#demoStamp').classList.add('hidden');
  $('#resultBanner').style.background = '';
  $('#resultBanner').style.borderColor = '';
  $('#probabilitiesBox').classList.add('hidden');
  $('#probBarsList').innerHTML = '';
  $('#gradcamView').classList.add('hidden');
  $('#heatmapPlaceholder').classList.remove('hidden');
  $('#heatmapStatus').textContent = 'Not available';
  $('#heatmapStatus').className = 'not-connected';
  if (runInferenceBtn) runInferenceBtn.classList.add('hidden');
}

function resetChecks() {
  setCheckRow(0, 'neutral', 'Waiting for an image');
  setCheckRow(1, 'neutral', 'Basic resolution check (min 200x200 px)');
  setCheckRow(2, 'neutral', 'Illumination & contrast validation');
}

function clearFile() {
  currentFile = null;
  currentImageDimensions = null;
  currentScreeningId = null;
  if (currentObjectUrl) URL.revokeObjectURL(currentObjectUrl);
  currentObjectUrl = null;
  fileInput.value = '';
  filePreview.classList.add('hidden');
  dropZone.classList.remove('hidden');
  analyzeButton.disabled = true;
  analyzeButton.innerHTML = 'Upload & Validate Image <span aria-hidden="true">→</span>';
  if (runInferenceBtn) runInferenceBtn.classList.add('hidden');
  resetChecks();
  resetResult();
}

// -------------------------------------------------------------
// Backend Health & Connectivity Check
// -------------------------------------------------------------
async function checkBackendHealth() {
  const statusPill = $('#backendStatusPill');
  const dot = $('#backendDot');
  const text = $('#backendStatusText');
  const modelPill = $('#modelReadinessPill');
  const modelDot = $('#modelDot');
  const modelText = $('#modelStatusText');

  // When deployed as static frontend without configured public backend endpoint
  if (!API_BASE) {
    statusPill.className = 'status-pill not-connected';
    statusPill.style.background = '#fffbf2';
    statusPill.style.borderColor = '#f4e0ba';
    statusPill.style.color = '#996812';
    dot.style.background = '#d3a54b';
    dot.style.boxShadow = '0 0 0 3px rgba(211, 165, 75, 0.15)';
    text.textContent = 'Backend unconfigured';

    modelPill.className = 'status-pill not-connected';
    modelPill.style.background = '#fffbf2';
    modelPill.style.borderColor = '#f4e0ba';
    modelPill.style.color = '#996812';
    modelDot.style.background = '#d3a54b';
    modelDot.style.boxShadow = '0 0 0 3px rgba(211, 165, 75, 0.15)';
    modelText.textContent = 'Awaiting cloud backend';

    const refText = $('#screeningRefText');
    if (refText) {
      refText.textContent = 'Static frontend preview active. Connect FastAPI endpoint for live inference.';
    }
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/health`, { method: 'GET' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (data.status === 'ok') {
      statusPill.className = 'status-pill';
      statusPill.style.background = '#f0faf6';
      statusPill.style.borderColor = '#c0ecd9';
      statusPill.style.color = '#0b795c';
      dot.style.background = '#27b99b';
      dot.style.boxShadow = '0 0 0 3px rgba(39, 185, 155, 0.15)';
      text.textContent = 'Backend online';

      if (data.model_status === 'ready') {
        modelPill.className = 'status-pill';
        modelPill.style.background = '#f0faf6';
        modelPill.style.borderColor = '#c0ecd9';
        modelPill.style.color = '#0b795c';
        modelDot.style.background = '#27b99b';
        modelDot.style.boxShadow = '0 0 0 3px rgba(39, 185, 155, 0.15)';
        modelText.textContent = 'Model ready (5-class)';
        $('#emptyAiDot').style.background = '#27b99b';
        $('#emptyCamDot').style.background = '#27b99b';
        $('#emptyAiText').textContent = 'Ready';
        $('#emptyCamText').textContent = 'Ready';
      } else {
        modelPill.className = 'status-pill not-connected';
        modelPill.style.background = '#fffbf2';
        modelPill.style.borderColor = '#f4e0ba';
        modelPill.style.color = '#996812';
        modelDot.style.background = '#d3a54b';
        modelDot.style.boxShadow = '0 0 0 3px rgba(211, 165, 75, 0.15)';
        modelText.textContent = data.model_status === 'error' ? 'Model error' : 'Model not configured';
        $('#emptyAiText').textContent = 'Not configured';
        $('#emptyCamText').textContent = 'Not configured';
      }
    }
  } catch (err) {
    statusPill.className = 'status-pill';
    statusPill.style.background = '#fff5f6';
    statusPill.style.borderColor = '#fcd2d8';
    statusPill.style.color = '#c52243';
    dot.style.background = '#e54e70';
    dot.style.boxShadow = '0 0 0 3px rgba(229, 78, 112, 0.15)';
    text.textContent = 'Backend offline';

    modelPill.className = 'status-pill not-connected';
    modelPill.style.background = '#fff5f6';
    modelPill.style.borderColor = '#fcd2d8';
    modelPill.style.color = '#c52243';
    modelDot.style.background = '#e54e70';
    modelDot.style.boxShadow = '0 0 0 3px rgba(229, 78, 112, 0.15)';
    modelText.textContent = 'Disconnected';
    console.warn('Backend connection failed:', err);
  }
}

// -------------------------------------------------------------
// File Selection & Local Pre-Validation
// -------------------------------------------------------------
function handleFile(file) {
  if (!file) return;
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    showToast('Please choose a valid PNG, JPG, or WebP fundus image.');
    return;
  }
  if (file.size > 15 * 1024 * 1024) {
    showToast('Image file exceeds the 15 MB limit. Please select a smaller image.');
    return;
  }

  if (currentObjectUrl) URL.revokeObjectURL(currentObjectUrl);
  currentFile = file;
  currentScreeningId = null;
  currentObjectUrl = URL.createObjectURL(file);
  currentImageDimensions = null;
  uploadedPreview.src = currentObjectUrl;

  $('#fileName').textContent = file.name;
  $('#fileSize').textContent = formatBytes(file.size);
  $('#fileDimensions').textContent = 'Verifying image…';

  dropZone.classList.add('hidden');
  filePreview.classList.remove('hidden');
  analyzeButton.disabled = true;
  analyzeButton.textContent = 'Checking image…';
  if (runInferenceBtn) runInferenceBtn.classList.add('hidden');
  resetChecks();
  resetResult();

  const image = new Image();
  image.onload = () => {
    currentImageDimensions = { width: image.naturalWidth, height: image.naturalHeight };
    $('#fileDimensions').textContent = `${image.naturalWidth} × ${image.naturalHeight} px`;
    setCheckRow(0, 'pass', `Format verified: ${file.type.split('/')[1].toUpperCase()} (${formatBytes(file.size)})`);
    const enoughPixels = image.naturalWidth >= 200 && image.naturalHeight >= 200;
    setCheckRow(1, enoughPixels ? 'pass' : 'warn', enoughPixels ? `${image.naturalWidth} × ${image.naturalHeight} px (pass)` : 'Low resolution (< 200x200 px)');
    analyzeButton.disabled = false;
    analyzeButton.innerHTML = 'Upload & Validate Image <span aria-hidden="true">→</span>';
    showToast(enoughPixels ? 'Image selected. Click to upload and validate.' : 'Image resolution low (<200px).');
  };
  image.onerror = () => {
    $('#fileDimensions').textContent = 'Could not decode image';
    setCheckRow(0, 'warn', 'Browser could not decode file');
    setCheckRow(1, 'warn', 'Invalid image data');
    analyzeButton.disabled = true;
    analyzeButton.textContent = 'Image could not be opened';
    showToast('The selected file could not be decoded. Try another file.');
  };
  image.src = currentObjectUrl;
}

// -------------------------------------------------------------
// Step 1: Upload & Technical Validation
// -------------------------------------------------------------
async function uploadAndValidate() {
  if (!currentFile) return;

  if (!API_BASE) {
    showToast('Live backend service is not configured for this deployment. Click "View sample demo" to explore.');
    return;
  }

  analyzeButton.disabled = true;
  analyzeButton.innerHTML = 'Uploading to server… <span class="pulse-dot"></span>';

  const formData = new FormData();
  formData.append('file', currentFile);

  try {
    const res = await fetch(`${API_BASE}/api/v1/screenings/upload`, {
      method: 'POST',
      body: formData,
    });

    const data = await res.json();
    if (!res.ok) {
      const errorMsg = data.detail || 'Upload failed.';
      showToast(`Error: ${errorMsg}`);
      analyzeButton.disabled = false;
      analyzeButton.innerHTML = 'Retry Upload <span aria-hidden="true">→</span>';
      return;
    }

    // Capture persistent screening reference ID
    currentScreeningId = data.screening_id;

    // Display technical quality checks in checklist
    setCheckRow(0, 'pass', `${data.image_quality.format} image (${formatBytes(data.file_size_bytes)})`);
    setCheckRow(1, 'pass', `Resolution: ${data.image_quality.width} × ${data.image_quality.height} px`);
    const isQualityAcceptable = data.image_quality.heuristic_status === 'acceptable';
    setCheckRow(2, isQualityAcceptable ? 'pass' : 'warn', `Heuristics: ${data.image_quality.heuristic_status.toUpperCase()} (mean: ${data.image_quality.mean_brightness})`);

    // Reveal Result View
    resultEmpty.classList.add('hidden');
    resultContent.classList.remove('hidden');
    $('#resultTitle').textContent = 'Image Verified & Usability Extracted';
    $('#resultSubtitle').textContent = `Screening ID: ${currentScreeningId.substring(0, 8)}… (SQLite Persisted)`;
    $('#resultSymbol').textContent = '✓';
    $('#qualityValue').textContent = data.image_quality.heuristic_status.toUpperCase();
    $('#qualityDescription').textContent = data.message;
    $('#qualityMeter').style.width = isQualityAcceptable ? '85%' : '40%';
    $('#qualityMeter').style.background = isQualityAcceptable ? '#21b78d' : '#d8a145';

    $('#predictionValue').textContent = 'Pending Analysis';
    $('#predictionDescription').textContent = 'Click "Run AI Analysis" below to execute deep learning model.';

    $('#screeningRefText').textContent = `Screening ID ${currentScreeningId} registered in SQLite. Ready for model inference.`;

    analyzeButton.innerHTML = 'Image Uploaded ✓';
    analyzeButton.disabled = true;
    if (runInferenceBtn) {
      runInferenceBtn.classList.remove('hidden');
      runInferenceBtn.disabled = false;
    }

    showToast('Image uploaded and verified! You can now run AI analysis.');
    loadScreeningHistory();

  } catch (err) {
    console.error('Upload request failed:', err);
    showToast('Network error: Unable to reach DRISHTI-AI backend.');
    analyzeButton.disabled = false;
    analyzeButton.innerHTML = 'Retry Upload <span aria-hidden="true">→</span>';
  }
}

// -------------------------------------------------------------
// Step 2: Trigger AI Model Analysis & Grad-CAM
// -------------------------------------------------------------
async function runAiAnalysis() {
  if (!API_BASE) {
    showToast('Live AI inference requires a connected backend service.');
    return;
  }

  if (!currentScreeningId) {
    showToast('Please upload an image first.');
    return;
  }

  if (runInferenceBtn) {
    runInferenceBtn.disabled = true;
    runInferenceBtn.innerHTML = 'Running Model & Grad-CAM… <span class="pulse-dot"></span>';
  }

  try {
    const res = await fetch(`${API_BASE}/api/v1/screenings/${currentScreeningId}/analyze`, {
      method: 'POST',
    });
    const data = await res.json();

    if (!res.ok) {
      const errDetail = data.detail || 'Inference execution failed.';
      showToast(`Error: ${errDetail}`);
      if (runInferenceBtn) {
        runInferenceBtn.disabled = false;
        runInferenceBtn.innerHTML = 'Retry AI Analysis <span aria-hidden="true">⚡</span>';
      }
      return;
    }

    if (!data.analysis_available) {
      $('#predictionValue').textContent = 'Model Unavailable';
      $('#predictionDescription').textContent = data.message || 'Model weights not configured.';
      $('#heatmapStatus').textContent = 'Not configured';
      $('#heatmapMessage').textContent = 'Awaiting model weights configuration.';
      showToast('AI Model is not configured. Clinical review active.');
      if (runInferenceBtn) {
        runInferenceBtn.disabled = true;
        runInferenceBtn.textContent = 'Model Not Configured';
      }
      return;
    }

    // Real Model Prediction
    const predStage = data.prediction || 'Unknown';
    const confPct = (data.confidence * 100).toFixed(1);
    $('#predictionValue').textContent = `${predStage} (${confPct}%)`;
    $('#predictionDescription').textContent = `Verified model inference completed. Confidence: ${confPct}%. Requires clinical ophthalmologist review.`;

    // Render Stage Probability Distribution
    if (data.class_probabilities) {
      $('#probabilitiesBox').classList.remove('hidden');
      const probList = $('#probBarsList');
      probList.innerHTML = '';
      for (const [clsName, prob] of Object.entries(data.class_probabilities)) {
        const pct = (prob * 100).toFixed(1);
        const isTarget = clsName === predStage;
        const row = document.createElement('div');
        row.className = 'prob-row';
        row.innerHTML = `
          <span class="prob-name" style="${isTarget ? 'font-weight:800; color:#1e63f2;' : ''}">${clsName}</span>
          <div class="prob-track"><div class="prob-fill" style="width:${pct}%; ${isTarget ? 'background:#1e63f2;' : 'background:#97b3ed;'}"></div></div>
          <span class="prob-val">${pct}%</span>
        `;
        probList.appendChild(row);
      }
    }

    // Handle Genuine Grad-CAM
    if (data.gradcam_available && data.gradcam_url) {
      $('#heatmapStatus').textContent = 'Genuine Heatmap';
      $('#heatmapStatus').className = 'status-pill';
      $('#heatmapStatus').style.background = '#eefbf6';
      $('#heatmapStatus').style.color = '#0b795c';
      $('#heatmapPlaceholder').classList.add('hidden');
      $('#gradcamView').classList.remove('hidden');
      $('#gradcamImg').src = `${API_BASE}${data.gradcam_url}?t=${Date.now()}`;
    } else {
      $('#heatmapStatus').textContent = 'Unavailable';
      $('#heatmapPlaceholder').classList.remove('hidden');
      $('#gradcamView').classList.add('hidden');
      $('#heatmapMessage').textContent = 'Grad-CAM explainability was not generated for this image.';
    }

    if (runInferenceBtn) {
      runInferenceBtn.innerHTML = 'Analysis Complete ✓';
      runInferenceBtn.disabled = true;
    }

    showToast(`Inference complete: ${predStage} (${confPct}%)`);
    loadScreeningHistory();

  } catch (err) {
    console.error('Analysis trigger failed:', err);
    showToast('Failed to connect to analysis service.');
    if (runInferenceBtn) {
      runInferenceBtn.disabled = false;
      runInferenceBtn.innerHTML = 'Retry AI Analysis <span aria-hidden="true">⚡</span>';
    }
  }
}

// -------------------------------------------------------------
// Step 3: Screening History from SQLite
// -------------------------------------------------------------
async function loadScreeningHistory() {
  const container = $('#historyListContainer');
  if (!container) return;

  if (!API_BASE) {
    container.innerHTML = '<p style="font-size:11px; color:#8291aa; margin:0;">Screening history requires a connected FastAPI backend.</p>';
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/v1/screenings?page=1&page_size=8`, { method: 'GET' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (!data.items || data.items.length === 0) {
      container.innerHTML = '<p style="font-size:11px; color:#8291aa; margin:0;">No screening sessions recorded yet. Upload an image to create one.</p>';
      return;
    }

    let html = '';
    data.items.forEach((item) => {
      const dateStr = new Date(item.created_at).toLocaleString();
      const hasAnalysis = item.analysis_available && item.prediction;
      const badgeClass = hasAnalysis ? 'badge-ready' : 'badge-warn';
      const statusText = hasAnalysis ? `${item.prediction} (${(item.confidence * 100).toFixed(0)}%)` : 'Triage / Pending';

      html += `
        <div class="history-item">
          <div class="history-main">
            <strong>${item.file_name} <span class="badge ${badgeClass}">${statusText}</span></strong>
            <span class="history-meta">ID: ${item.screening_id.substring(0, 8)}… · ${dateStr} · ${item.image_quality.width}x${item.image_quality.height} px (${item.image_quality.heuristic_status})</span>
          </div>
          <div>
            ${item.gradcam_available ? `<span style="font-size:10px; font-weight:700; color:#0b9e8c;">Grad-CAM ✓</span>` : ''}
          </div>
        </div>
      `;
    });
    container.innerHTML = html;

  } catch (err) {
    container.innerHTML = '<p style="font-size:11px; color:#e54e70; margin:0;">Unable to fetch history from SQLite backend.</p>';
  }
}

// -------------------------------------------------------------
// Simulated Demo Flow (Clearly Labeled as Simulated)
// -------------------------------------------------------------
function showSampleDemo() {
  resultEmpty.classList.add('hidden');
  resultContent.classList.remove('hidden');
  $('#resultTitle').textContent = 'Sample workflow preview';
  $('#resultSubtitle').textContent = 'Static demonstration data only (SIMULATED)';
  $('#resultSymbol').textContent = 'i';
  $('#qualityValue').textContent = 'Sample status';
  $('#qualityDescription').textContent = 'Illustrative demo state. No clinical quality assessment was run.';
  $('#qualityMeter').style.width = '60%';
  $('#qualityMeter').style.background = '#9bb5ea';
  $('#predictionValue').textContent = 'Moderate DR (Simulated)';
  $('#predictionDescription').textContent = 'SIMULATED DEMO: This is a static UI walkthrough demonstrating visual layout.';

  $('#probabilitiesBox').classList.remove('hidden');
  $('#probBarsList').innerHTML = `
    <div class="prob-row"><span class="prob-name">No DR</span><div class="prob-track"><div class="prob-fill" style="width:5%;"></div></div><span class="prob-val">5.0%</span></div>
    <div class="prob-row"><span class="prob-name">Mild</span><div class="prob-track"><div class="prob-fill" style="width:12%;"></div></div><span class="prob-val">12.0%</span></div>
    <div class="prob-row"><span class="prob-name" style="font-weight:800; color:#1e63f2;">Moderate</span><div class="prob-track"><div class="prob-fill" style="width:71%; background:#1e63f2;"></div></div><span class="prob-val">71.0%</span></div>
    <div class="prob-row"><span class="prob-name">Severe</span><div class="prob-track"><div class="prob-fill" style="width:8%;"></div></div><span class="prob-val">8.0%</span></div>
    <div class="prob-row"><span class="prob-name">Proliferative DR</span><div class="prob-track"><div class="prob-fill" style="width:4%;"></div></div><span class="prob-val">4.0%</span></div>
  `;

  $('#heatmapStatus').textContent = 'Illustrative demo';
  $('#heatmapPlaceholder').innerHTML = '<div class="heatmap-icon" style="color:#916df2">◉</div><p>Conceptual heatmap preview. Run actual model inference on an uploaded image for genuine Grad-CAM.</p>';
  $('#gradcamView').classList.add('hidden');
  $('#safetyNote').textContent = 'DEMO ONLY: “Moderate DR” is a static placeholder used to preview the interface. It is not derived from an image, and must not be used for diagnosis or treatment.';
  $('#demoStamp').classList.remove('hidden');
  $('#resultBanner').style.background = '#fff9eb';
  $('#resultBanner').style.borderColor = '#f4e5bf';
  showToast('Sample demo opened. The result is simulated.');
  $('#workspace').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// -------------------------------------------------------------
// Event Listeners
// -------------------------------------------------------------
fileInput.addEventListener('change', (event) => handleFile(event.target.files && event.target.files[0]));
analyzeButton.addEventListener('click', uploadAndValidate);
if (runInferenceBtn) runInferenceBtn.addEventListener('click', runAiAnalysis);

$('#removeFile').addEventListener('click', (event) => {
  event.preventDefault();
  clearFile();
  showToast('Selected image removed.');
});

$('#trySample').addEventListener('click', showSampleDemo);
$('#trySampleTop').addEventListener('click', showSampleDemo);

const refreshBtn = $('#refreshHistoryBtn');
if (refreshBtn) refreshBtn.addEventListener('click', () => {
  loadScreeningHistory();
  showToast('Screening history refreshed.');
});

dropZone.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); fileInput.click(); }
});
['dragenter', 'dragover'].forEach((type) => dropZone.addEventListener(type, (event) => { event.preventDefault(); dropZone.classList.add('dragover'); }));
['dragleave', 'drop'].forEach((type) => dropZone.addEventListener(type, (event) => { event.preventDefault(); dropZone.classList.remove('dragover'); }));
dropZone.addEventListener('drop', (event) => handleFile(event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files[0]));

const menuToggle = $('#menuToggle');
const mainNav = $('#mainNav');
menuToggle.addEventListener('click', () => {
  const opened = mainNav.classList.toggle('open');
  menuToggle.setAttribute('aria-expanded', String(opened));
});
mainNav.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
  mainNav.classList.remove('open');
  menuToggle.setAttribute('aria-expanded', 'false');
}));

window.addEventListener('beforeunload', () => {
  if (currentObjectUrl) URL.revokeObjectURL(currentObjectUrl);
});

// -------------------------------------------------------------
// Cinematic Hero Image & Fullscreen Video Lightbox Modal
// -------------------------------------------------------------
function initCinematicVideoModal() {
  const modal = $('#videoModal');
  const video = $('#modalVideoPlayer');
  const openHotspotBtn = $('#openFullscreenVideoBtn');
  const heroMediaWrap = $('#heroMediaWrap');
  const watchTopBtn = $('#watchIntroTopBtn');
  const closeBtn = $('#closeVideoModalBtn');
  const backdrop = $('#videoModalBackdrop');
  const playPauseBtn = $('#modalPlayPauseBtn');
  const soundBtn = $('#modalSoundBtn');
  const soundLabel = $('#modalSoundLabel');
  const replayBtn = $('#modalReplayBtn');
  const fsToggleBtn = $('#modalFullscreenToggleBtn');
  const progressBar = $('#modalProgressBar');
  const progressWrap = $('#modalProgressWrap');
  const timeDisplay = $('#modalTimeDisplay');

  if (!modal || !video) return;

  function formatTime(seconds) {
    if (isNaN(seconds) || seconds < 0) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  }

  function updatePlayPauseIcons(isPlaying) {
    if (!playPauseBtn) return;
    const pauseIcon = playPauseBtn.querySelector('.icon-pause');
    const playIcon = playPauseBtn.querySelector('.icon-play');
    if (isPlaying) {
      if (pauseIcon) pauseIcon.classList.remove('hidden');
      if (playIcon) playIcon.classList.add('hidden');
      playPauseBtn.setAttribute('aria-label', 'Pause video');
      playPauseBtn.setAttribute('title', 'Pause (Space)');
    } else {
      if (pauseIcon) pauseIcon.classList.add('hidden');
      if (playIcon) playIcon.classList.remove('hidden');
      playPauseBtn.setAttribute('aria-label', 'Play video');
      playPauseBtn.setAttribute('title', 'Play (Space)');
    }
  }

  function updateSoundIcons(isMuted) {
    if (!soundBtn) return;
    const unmutedIcon = soundBtn.querySelector('.sound-icon-unmuted');
    const mutedIcon = soundBtn.querySelector('.sound-icon-muted');
    if (isMuted) {
      if (unmutedIcon) unmutedIcon.classList.add('hidden');
      if (mutedIcon) mutedIcon.classList.remove('hidden');
      if (soundLabel) soundLabel.textContent = 'Muted';
      soundBtn.setAttribute('aria-label', 'Enable sound');
      soundBtn.setAttribute('title', 'Enable sound');
    } else {
      if (unmutedIcon) unmutedIcon.classList.remove('hidden');
      if (mutedIcon) mutedIcon.classList.add('hidden');
      if (soundLabel) soundLabel.textContent = 'Sound';
      soundBtn.setAttribute('aria-label', 'Mute audio');
      soundBtn.setAttribute('title', 'Mute audio');
    }
  }

  function openVideoModal() {
    modal.removeAttribute('hidden');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Start playback unmuted if possible (user gesture)
    video.currentTime = 0;
    video.muted = false;
    updateSoundIcons(false);

    const playPromise = video.play();
    if (playPromise !== undefined) {
      playPromise.then(() => {
        updatePlayPauseIcons(true);
      }).catch(() => {
        // Fallback to muted if browser autoplay policy restricts unmuted audio
        video.muted = true;
        updateSoundIcons(true);
        video.play().catch(() => {});
        updatePlayPauseIcons(true);
      });
    }

    // Try native fullscreen if available on stage
    const stage = modal.querySelector('.video-modal-stage') || modal;
    if (stage.requestFullscreen) {
      stage.requestFullscreen().catch(() => {});
    } else if (stage.webkitRequestFullscreen) {
      stage.webkitRequestFullscreen();
    }

    showToast('Playing DRISHTI-AI cinematic intro.');
  }

  function closeVideoModal() {
    if (document.fullscreenElement) {
      document.exitFullscreen().catch(() => {});
    }
    video.pause();
    modal.classList.remove('active');
    modal.setAttribute('hidden', '');
    document.body.style.overflow = '';
    updatePlayPauseIcons(false);
  }

  // Open triggers
  if (openHotspotBtn) openHotspotBtn.addEventListener('click', (e) => { e.stopPropagation(); openVideoModal(); });
  if (heroMediaWrap) {
    heroMediaWrap.addEventListener('click', openVideoModal);
    heroMediaWrap.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openVideoModal(); }
    });
  }
  if (watchTopBtn) watchTopBtn.addEventListener('click', openVideoModal);

  // Close triggers
  if (closeBtn) closeBtn.addEventListener('click', closeVideoModal);
  if (backdrop) backdrop.addEventListener('click', closeVideoModal);

  // Play/Pause button
  if (playPauseBtn) {
    playPauseBtn.addEventListener('click', () => {
      if (video.paused || video.ended) {
        if (video.ended) video.currentTime = 0;
        video.play();
        updatePlayPauseIcons(true);
      } else {
        video.pause();
        updatePlayPauseIcons(false);
      }
    });
  }

  // Sound toggle button
  if (soundBtn) {
    soundBtn.addEventListener('click', () => {
      video.muted = !video.muted;
      updateSoundIcons(video.muted);
      showToast(video.muted ? 'Audio muted.' : 'Audio enabled.');
    });
  }

  // Replay button
  if (replayBtn) {
    replayBtn.addEventListener('click', () => {
      video.currentTime = 0;
      video.play();
      updatePlayPauseIcons(true);
      showToast('Replaying trailer.');
    });
  }

  // Native Fullscreen toggle button
  if (fsToggleBtn) {
    fsToggleBtn.addEventListener('click', () => {
      const stage = modal.querySelector('.video-modal-stage') || modal;
      if (!document.fullscreenElement) {
        if (stage.requestFullscreen) stage.requestFullscreen().catch(() => {});
      } else {
        if (document.exitFullscreen) document.exitFullscreen().catch(() => {});
      }
    });
  }

  // Time & progress updates
  video.addEventListener('timeupdate', () => {
    const cur = video.currentTime || 0;
    const dur = video.duration || 10;
    const pct = dur > 0 ? (cur / dur) * 100 : 0;
    if (progressBar) progressBar.style.width = `${pct}%`;
    if (timeDisplay) timeDisplay.textContent = `${formatTime(cur)} / ${formatTime(dur)}`;
    if (progressWrap) progressWrap.setAttribute('aria-valuenow', String(Math.round(cur)));
  });

  // Retain final frame on video end (no auto-loop)
  video.addEventListener('ended', () => {
    updatePlayPauseIcons(false);
  });

  // Progress bar scrubbing / seeking
  if (progressWrap) {
    progressWrap.addEventListener('click', (e) => {
      const rect = progressWrap.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const pct = Math.max(0, Math.min(1, clickX / rect.width));
      const dur = video.duration || 10;
      video.currentTime = pct * dur;
    });
  }

  // Keyboard navigation when modal is active
  window.addEventListener('keydown', (e) => {
    if (modal.hasAttribute('hidden')) return;
    if (e.key === 'Escape') {
      e.preventDefault();
      closeVideoModal();
    } else if (e.key === ' ' && document.activeElement.tagName !== 'BUTTON') {
      e.preventDefault();
      if (video.paused) { video.play(); updatePlayPauseIcons(true); }
      else { video.pause(); updatePlayPauseIcons(false); }
    } else if (e.key === 'm' || e.key === 'M') {
      e.preventDefault();
      video.muted = !video.muted;
      updateSoundIcons(video.muted);
    }
  });
}

// Run initial health check, video modal setup, and history fetch on startup
initCinematicVideoModal();
checkBackendHealth();
loadScreeningHistory();

