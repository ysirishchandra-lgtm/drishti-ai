const $ = (selector) => document.querySelector(selector);
const fileInput = $('#fileInput');
const dropZone = $('#dropZone');
const filePreview = $('#filePreview');
const uploadedPreview = $('#uploadedPreview');
const analyzeButton = $('#analyzeButton');
const resultEmpty = $('#resultEmpty');
const resultContent = $('#resultContent');
const toast = $('#toast');
let currentFile = null;
let currentObjectUrl = null;
let currentImageDimensions = null;
let toastTimer = null;

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 3000);
}
function formatBytes(bytes) {
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
}
function resetChecks() {
  setCheckRow(0, 'neutral', 'Waiting for an image');
  setCheckRow(1, 'neutral', 'Basic resolution check');
}
function clearFile() {
  currentFile = null;
  currentImageDimensions = null;
  if (currentObjectUrl) URL.revokeObjectURL(currentObjectUrl);
  currentObjectUrl = null;
  fileInput.value = '';
  filePreview.classList.add('hidden');
  dropZone.classList.remove('hidden');
  analyzeButton.disabled = true;
  analyzeButton.innerHTML = 'Check image <span aria-hidden="true">→</span>';
  resetChecks();
  resetResult();
}
function handleFile(file) {
  if (!file) return;
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    showToast('Please choose a PNG, JPG, or WebP image.');
    return;
  }
  if (file.size > 15 * 1024 * 1024) {
    showToast('The image is larger than 15 MB. Choose a smaller file.');
    return;
  }
  if (currentObjectUrl) URL.revokeObjectURL(currentObjectUrl);
  currentFile = file;
  currentObjectUrl = URL.createObjectURL(file);
  currentImageDimensions = null;
  uploadedPreview.src = currentObjectUrl;
  $('#fileName').textContent = file.name;
  $('#fileSize').textContent = formatBytes(file.size);
  $('#fileDimensions').textContent = 'Reading dimensions…';
  dropZone.classList.add('hidden');
  filePreview.classList.remove('hidden');
  analyzeButton.disabled = true;
  analyzeButton.textContent = 'Checking file…';
  resetChecks();
  resetResult();

  const image = new Image();
  image.onload = () => {
    // Only basic browser-side checks; this is not a clinical image-quality assessment.
    currentImageDimensions = { width: image.naturalWidth, height: image.naturalHeight };
    $('#fileDimensions').textContent = `${image.naturalWidth} × ${image.naturalHeight} px`;
    setCheckRow(0, 'pass', `Readable ${file.type.split('/')[1].toUpperCase()} image`);
    const enoughPixels = image.naturalWidth >= 256 && image.naturalHeight >= 256;
    setCheckRow(1, enoughPixels ? 'pass' : 'warn', enoughPixels ? 'At least 256 × 256 pixels' : 'Low resolution; use at least 256 × 256 px');
    analyzeButton.disabled = false;
    analyzeButton.innerHTML = 'Check image <span aria-hidden="true">→</span>';
    showToast(enoughPixels ? 'Image loaded. Basic checks are ready.' : 'Image loaded, but its resolution is low.');
  };
  image.onerror = () => {
    $('#fileDimensions').textContent = 'Could not read image dimensions';
    setCheckRow(0, 'warn', 'Browser could not open this image');
    setCheckRow(1, 'warn', 'Dimensions unavailable');
    analyzeButton.disabled = true;
    analyzeButton.textContent = 'Image could not be opened';
    showToast('The image could not be opened. Try another file.');
  };
  image.src = currentObjectUrl;
}
function runImageCheck() {
  if (!currentFile || !currentImageDimensions) return;
  resultEmpty.classList.add('hidden');
  resultContent.classList.remove('hidden');
  $('#resultTitle').textContent = 'Basic image check complete';
  $('#resultSubtitle').textContent = 'This is not a clinical quality gate';
  $('#resultSymbol').textContent = '✓';
  $('#qualityValue').textContent = currentImageDimensions.width >= 256 && currentImageDimensions.height >= 256 ? 'Dimensions acceptable' : 'Low resolution';
  $('#qualityDescription').textContent = `${currentImageDimensions.width} × ${currentImageDimensions.height} pixels. Browser readability and minimum dimensions only.`;
  $('#qualityMeter').style.width = currentImageDimensions.width >= 256 && currentImageDimensions.height >= 256 ? '72%' : '30%';
  $('#qualityMeter').style.background = currentImageDimensions.width >= 256 && currentImageDimensions.height >= 256 ? '#21b78d' : '#d8a145';
  $('#predictionValue').textContent = 'Not available';
  $('#predictionDescription').textContent = 'No trained DR model is connected. No prediction was made from this image.';
  $('#heatmapStatus').textContent = 'Not available';
  $('#heatmapPlaceholder').innerHTML = '<div class="heatmap-icon">◎</div><p>Connect the model and explainability pipeline to display a real model-generated heatmap.</p>';
  $('#safetyNote').textContent = 'This check does not detect diabetic retinopathy or establish clinical image quality. Please do not use this prototype for healthcare decisions.';
  $('#demoStamp').classList.add('hidden');
  $('#resultBanner').style.background = '#f2fbf8';
  $('#resultBanner').style.borderColor = '#dbeee9';
  showToast('Basic checks complete. AI prediction is not connected.');
}
function showSampleDemo() {
  // A fixed, explicitly simulated result demonstrates UI states only. No uploaded image is analyzed.
  resultEmpty.classList.add('hidden');
  resultContent.classList.remove('hidden');
  $('#resultTitle').textContent = 'Sample workflow preview';
  $('#resultSubtitle').textContent = 'Static demonstration data only';
  $('#resultSymbol').textContent = 'i';
  $('#qualityValue').textContent = 'Sample status';
  $('#qualityDescription').textContent = 'Illustrative demo state. No clinical quality assessment was run.';
  $('#qualityMeter').style.width = '60%';
  $('#qualityMeter').style.background = '#9bb5ea';
  $('#predictionValue').textContent = 'Moderate DR';
  $('#predictionDescription').textContent = 'SIMULATED EXAMPLE — this is not a model prediction or a real patient result.';
  $('#heatmapStatus').textContent = 'Illustrative only';
  $('#heatmapPlaceholder').innerHTML = '<div class="heatmap-icon" style="color:#916df2">◉</div><p>Conceptual heatmap preview. No Grad-CAM computation has been performed.</p>';
  $('#safetyNote').textContent = 'DEMO ONLY: “Moderate DR” is a static placeholder used to preview the interface. It is not derived from an image, and must not be used for diagnosis or treatment.';
  $('#demoStamp').classList.remove('hidden');
  $('#resultBanner').style.background = '#fff9eb';
  $('#resultBanner').style.borderColor = '#f4e5bf';
  showToast('Sample demo opened. The result is simulated.');
  $('#workspace').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

fileInput.addEventListener('change', (event) => handleFile(event.target.files && event.target.files[0]));
analyzeButton.addEventListener('click', runImageCheck);
$('#removeFile').addEventListener('click', (event) => { event.preventDefault(); clearFile(); showToast('Selected image removed.'); });
$('#trySample').addEventListener('click', showSampleDemo);
$('#trySampleTop').addEventListener('click', showSampleDemo);
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
window.addEventListener('beforeunload', () => { if (currentObjectUrl) URL.revokeObjectURL(currentObjectUrl); });
