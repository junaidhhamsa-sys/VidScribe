// JavaScript for Video Summarizer

let currentOutputName = null;

// Get elements
const uploadBox = document.getElementById('uploadBox');
const videoInput = document.getElementById('videoInput');
const uploadSection = document.getElementById('uploadSection');
const processingSection = document.getElementById('processingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const processingStatus = document.getElementById('processingStatus');
const progressFill = document.getElementById('progressFill');
const downloadBtn = document.getElementById('downloadBtn');
const newVideoBtn = document.getElementById('newVideoBtn');
const retryBtn = document.getElementById('retryBtn');

// Upload box click
uploadBox.addEventListener('click', () => {
    videoInput.click();
});

// File input change
videoInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFileUpload(file);
    }
});

// Drag and drop
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.classList.add('dragging');
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('dragging');
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.classList.remove('dragging');

    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('video/')) {
        handleFileUpload(file);
    } else {
        showError('Please drop a valid video file');
    }
});

// Handle file upload
async function handleFileUpload(file) {
    // Show processing section
    showSection('processing');

    // Create form data
    const formData = new FormData();
    formData.append('video', file);

    // Simulate progress (since we're doing sync processing)
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        progressFill.style.width = progress + '%';

        // Update status messages
        if (progress < 20) {
            processingStatus.textContent = 'Extracting keyframes...';
        } else if (progress < 40) {
            processingStatus.textContent = 'Transcribing audio with AI...';
        } else if (progress < 60) {
            processingStatus.textContent = 'Generating image captions...';
        } else if (progress < 80) {
            processingStatus.textContent = 'Creating summary...';
        } else {
            processingStatus.textContent = 'Generating PowerPoint...';
        }
    }, 500);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        clearInterval(progressInterval);
        progressFill.style.width = '100%';

        if (data.status === 'success') {
            currentOutputName = data.output_name;
            showResults(data);
        } else {
            showError(data.error || 'An error occurred during processing');
        }

    } catch (error) {
        clearInterval(progressInterval);
        showError('Network error: ' + error.message);
    }
}

// Show section
function showSection(section) {
    uploadSection.style.display = 'none';
    processingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';

    if (section === 'upload') {
        uploadSection.style.display = 'block';
    } else if (section === 'processing') {
        processingSection.style.display = 'block';
        progressFill.style.width = '0%';
    } else if (section === 'results') {
        resultsSection.style.display = 'block';
    } else if (section === 'error') {
        errorSection.style.display = 'block';
    }
}

// Show results
function showResults(data) {
    document.getElementById('keyframeCount').textContent = data.keyframe_count;
    document.getElementById('slidesCount').textContent = data.slides_count;
    document.getElementById('language').textContent = data.language.toUpperCase();
    document.getElementById('summaryText').textContent = data.summary;

    showSection('results');
}

// Show error
function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    showSection('error');
}

// Download button
downloadBtn.addEventListener('click', () => {
    if (currentOutputName) {
        window.location.href = `/download/${currentOutputName}`;
    }
});

// New video button
newVideoBtn.addEventListener('click', () => {
    currentOutputName = null;
    videoInput.value = '';
    showSection('upload');
});

// Retry button
retryBtn.addEventListener('click', () => {
    videoInput.value = '';
    showSection('upload');
});
