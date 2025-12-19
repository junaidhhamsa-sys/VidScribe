// ============================================================================
// VidScribe - Frontend JavaScript
// ============================================================================

let currentOutputName = null;
let statusCheckInterval = null;

// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const videoFileInput = document.getElementById('videoFile');
const fileNameDisplay = document.getElementById('fileName');
const fileLabel = document.querySelector('.file-label');
const outputFormatRadios = document.querySelectorAll('input[name="output_format"]');
const templateSection = document.getElementById('templateSection');
const uploadSection = document.getElementById('uploadSection');
const processingSection = document.getElementById('processingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');

const uploadBtn = document.getElementById('uploadBtn');
const downloadBtn = document.getElementById('downloadBtn');
const newVideoBtn = document.getElementById('newVideoBtn');
const retryBtn = document.getElementById('retryBtn');

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    console.log('VidScribe initialized');
});

function initializeEventListeners() {
    // File input change
    videoFileInput.addEventListener('change', handleFileSelect);

    // Form submit
    uploadForm.addEventListener('submit', handleFormSubmit);

    // Output format change
    outputFormatRadios.forEach(radio => {
        radio.addEventListener('change', handleFormatChange);
    });

    // Action buttons
    downloadBtn.addEventListener('click', handleDownload);
    newVideoBtn.addEventListener('click', resetApp);
    retryBtn.addEventListener('click', resetApp);
}


// ============================================================================
// Image Error Handling
// ============================================================================

function handleImageError(img) {
    // Fallback to logo if template preview fails to load
    img.src = '/static/images/logo.png';
    img.onerror = null; // Prevent infinite loop if logo also fails
}


// ============================================================================
// File Handling
// ============================================================================

function handleFileSelect(event) {
    const file = event.target.files[0];

    if (file) {
        // Update display
        fileNameDisplay.textContent = file.name;
        fileLabel.classList.add('has-file');

        // Show file info
        const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
        fileNameDisplay.textContent = `${file.name} (${sizeMB} MB)`;

        console.log('File selected:', file.name);
    }
}

function handleFormatChange(event) {
    const format = event.target.value;
    // Show/hide template selection based on format
    if (format === 'ppt' && templateSection) {
        templateSection.classList.remove('hidden');
    } else if (templateSection) {
        templateSection.classList.add('hidden');
    }
}

// ============================================================================
// Form Submission
// ============================================================================

async function handleFormSubmit(event) {
    event.preventDefault();

    const formData = new FormData(uploadForm);
    const file = videoFileInput.files[0];

    if (!file) {
        showError('Please select a video file');
        return;
    }

    // Disable submit button
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span>⏳ Uploading...</span>';

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            // Store output name
            currentOutputName = data.output_name;

            // Show processing section
            showProcessingSection(data.video_info);

            // Start status checking
            startStatusChecking();
        } else {
            showError(data.error || 'Upload failed');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showError('Network error. Please try again.');
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = '<span>🚀 Start Processing</span>';
    }
}

// ============================================================================
// Processing Status
// ============================================================================

function showProcessingSection(videoInfo) {
    // Hide upload section
    uploadSection.classList.add('hidden');

    // Show processing section
    processingSection.classList.remove('hidden');

    // Display video info
    const videoInfoDiv = document.getElementById('videoInfo');
    videoInfoDiv.innerHTML = `
        <p><strong>Duration:</strong> <span>${videoInfo.duration}</span></p>
        <p><strong>Resolution:</strong> <span>${videoInfo.resolution}</span></p>
        <p><strong>File Size:</strong> <span>${videoInfo.size}</span></p>
    `;
}

function startStatusChecking() {
    // Check immediately
    checkStatus();

    // Then check every 2 seconds
    statusCheckInterval = setInterval(checkStatus, 2000);
}

async function checkStatus() {
    if (!currentOutputName) return;

    try {
        const response = await fetch(`/status/${currentOutputName}`);
        const data = await response.json();

        if (response.ok) {
            updateProcessingStatus(data);

            if (data.status === 'complete') {
                stopStatusChecking();
                // Redirect to the new results page
                window.location.href = `/results/${currentOutputName}`;
            } else if (data.status === 'error') {
                stopStatusChecking();
                showError(data.message);
            }
        }
    } catch (error) {
        console.error('Status check error:', error);
    }
}

function updateProcessingStatus(data) {
    // Update progress bar
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');

    progressFill.style.width = `${data.progress}%`;
    progressText.textContent = data.message;

    // Update steps (simplified - you can enhance this)
    updateSteps(data.progress);
}

function updateSteps(progress) {
    const steps = document.querySelectorAll('.step');

    // Simple progress mapping
    const stepProgress = [0, 16, 33, 50, 66, 83, 100];

    steps.forEach((step, index) => {
        const stepIcon = step.querySelector('.step-icon');

        if (progress >= stepProgress[index + 1]) {
            step.classList.add('complete');
            step.classList.remove('active');
            stepIcon.textContent = '✓';
        } else if (progress >= stepProgress[index]) {
            step.classList.add('active');
            stepIcon.textContent = '⏳';
        }
    });
}

function stopStatusChecking() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
}

// ============================================================================
// Results Display
// ============================================================================

function showResults(results) {
    // Hide processing section
    processingSection.classList.add('hidden');

    // Show results section
    resultsSection.classList.remove('hidden');

    // Display results info
    const resultsInfo = document.getElementById('resultsInfo');
    resultsInfo.innerHTML = `
        <div class="info-item">
            <strong>Title</strong>
            <span>${truncateText(results.title, 30)}</span>
        </div>
        <div class="info-item">
            <strong>Slides Created</strong>
            <span>${results.slides_count}</span>
        </div>
        <div class="info-item">
            <strong>Language</strong>
            <span>${results.language.toUpperCase()}</span>
        </div>
        <div class="info-item">
            <strong>Processing Time</strong>
            <span>${results.processing_time.toFixed(1)}s</span>
        </div>
    `;

    // Display summary
    const summaryBox = document.getElementById('summaryBox');
    if (results.summary) {
        summaryBox.innerHTML = `
            <h3>📝 Summary</h3>
            <p>${results.summary}</p>
        `;
    } else {
        summaryBox.style.display = 'none';
    }

    // Setup download button
    if (results.output_type !== 'summary') {
        downloadBtn.style.display = 'inline-flex';
        downloadBtn.onclick = () => handleDownload(results.output_path);
    } else {
        downloadBtn.style.display = 'none';
    }
}

// ============================================================================
// Error Handling
// ============================================================================

function showError(message) {
    // Hide all sections
    uploadSection.classList.add('hidden');
    processingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');

    // Show error section
    errorSection.classList.remove('hidden');

    // Display error message
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;

    console.error('Error:', message);
}

// ============================================================================
// Download
// ============================================================================

function handleDownload() {
    if (!currentOutputName) {
        showError('No output available for download');
        return;
    }

    // Download file
    window.location.href = `/download/${currentOutputName}`;
}

// ============================================================================
// Reset Application
// ============================================================================

function resetApp() {
    // Stop status checking
    stopStatusChecking();

    // Reset current output
    currentOutputName = null;

    // Hide all sections
    processingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');

    // Show upload section
    uploadSection.classList.remove('hidden');

    // Reset form
    uploadForm.reset();
    fileNameDisplay.textContent = 'Choose video file...';
    fileLabel.classList.remove('has-file');

    // Reset template selection visibility (show by default for PPT)
    if (templateSection) {
        templateSection.classList.remove('hidden');
    }
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ============================================================================
// Utility Functions
// ============================================================================

function truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// ============================================================================
// Console Welcome Message
// ============================================================================

console.log('%c🎬 VidScribe', 'font-size: 24px; font-weight: bold; color: #2563eb;');
console.log('%cAI-Powered Video Summarization', 'font-size: 14px; color: #64748b;');
console.log('%cPowered by OpenCV, Whisper & Gemini AI', 'font-size: 12px; color: #94a3b8;');