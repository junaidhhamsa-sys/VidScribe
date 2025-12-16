// Results Page JavaScript - Google Slides Style Interactions

// State Management
let currentSlide = 1;
let totalSlides = 6; // Will be updated from presentation data
let selectedTemplate = 'professional';
let slidesData = [];

// DOM Elements
const slidesList = document.getElementById('slidesList');
const slideCanvas = document.getElementById('slideCanvas');
const slideCounter = document.getElementById('slideCounter');
const prevSlideBtn = document.getElementById('prevSlide');
const nextSlideBtn = document.getElementById('nextSlide');
const downloadBtn = document.getElementById('downloadBtn');
const presentBtn = document.getElementById('presentBtn');
const templateCards = document.querySelectorAll('.template-card');
const tabButtons = document.querySelectorAll('.tab-btn');
const closeTemplatePanel = document.getElementById('closeTemplatePanel');

// Initialize
document.addEventListener('DOMContentLoaded', function () {
  loadPresentationData();
  initSlideNavigation();
  initTemplateSelection();
  initButtons();
  updateSlideCounter();
  updateSlideDisplay(1); // Show first slide
});

// Load presentation data from window object
function loadPresentationData() {
  if (window.presentationData) {
    slidesData = window.presentationData.slides || [];
    totalSlides = window.presentationData.totalSlides || slidesData.length || 6;
    selectedTemplate = window.presentationData.selectedTemplate || 'professional';

    console.log('Loaded presentation:', {
      slides: slidesData.length,
      template: selectedTemplate
    });
  }
}

// Slide Navigation
function initSlideNavigation() {
  // Slide thumbnail click
  const thumbnails = document.querySelectorAll('.slide-thumbnail');
  thumbnails.forEach((thumbnail, index) => {
    thumbnail.addEventListener('click', function () {
      goToSlide(index + 1);
    });
  });

  // Previous/Next buttons
  prevSlideBtn.addEventListener('click', function () {
    if (currentSlide > 1) {
      goToSlide(currentSlide - 1);
    }
  });

  nextSlideBtn.addEventListener('click', function () {
    if (currentSlide < totalSlides) {
      goToSlide(currentSlide + 1);
    }
  });

  // Keyboard navigation
  document.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') {
      prevSlideBtn.click();
    } else if (e.key === 'ArrowRight') {
      nextSlideBtn.click();
    }
  });
}

function goToSlide(slideNumber) {
  if (slideNumber < 1 || slideNumber > totalSlides) return;

  currentSlide = slideNumber;

  // Update thumbnail selection
  const thumbnails = document.querySelectorAll('.slide-thumbnail');
  thumbnails.forEach((thumb, index) => {
    if (index + 1 === slideNumber) {
      thumb.classList.add('active');
    } else {
      thumb.classList.remove('active');
    }
  });

  // Update slide canvas with real content
  updateSlideDisplay(slideNumber);

  // Update counter
  updateSlideCounter();

  // Update button states
  updateNavigationButtons();

  // Scroll thumbnail into view
  const activeThumbnail = thumbnails[slideNumber - 1];
  if (activeThumbnail) {
    activeThumbnail.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function updateSlideDisplay(slideNumber) {
  // Get slide data (slides are 0-indexed in array, but 1-indexed for display)
  const slideIndex = slideNumber - 1;
  const slide = slidesData[slideIndex];

  if (slide) {
    // Display actual slide content
    const contentLines = (slide.content || '').split('\n').filter(line => line.trim());
    const bulletPoints = contentLines.map(line => {
      const cleanLine = line.replace(/^[-•*]\s*/, '').trim();
      return `<li>${escapeHtml(cleanLine)}</li>`;
    }).join('');

    // Build HTML with optional keyframe image
    let slideHTML = `\u003cdiv class="slide-content" style="padding: 40px 60px;"\u003e`;

    // Add keyframe image if available
    if (slide.keyframe_path) {
      let imagePath = slide.keyframe_path;

      // Handle different path formats
      if (imagePath.includes('/temp/')) {
        // Extract path after /temp/
        const tempParts = imagePath.split('/temp/');
        imagePath = tempParts[tempParts.length - 1];
      } else if (imagePath.includes('/saved_results/')) {
        // Extract path after /saved_results/
        const savedParts = imagePath.split('/saved_results/');
        imagePath = savedParts[savedParts.length - 1];
      }

      slideHTML += `
        \u003cdiv style="text-align: center; margin-bottom: 30px;"\u003e
          \u003cimg src="/temp/${imagePath}" 
               alt="Slide ${slideNumber} keyframe" 
               style="max-width: 60%; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"
               onerror="this.style.display='none'"\u003e
        \u003c/div\u003e
      `;
    }

    // Add title and content
    slideHTML += `
      \u003ch2 style="font-size: 36px; margin-bottom: 30px; color: #202124;"\u003e${escapeHtml(slide.title || 'Slide ' + slideNumber)}\u003c/h2\u003e
      ${bulletPoints ? `\u003cul style="text-align: left; font-size: 18px; line-height: 1.8; color: #5f6368; list-style-position: inside;"\u003e${bulletPoints}\u003c/ul\u003e` : '\u003cp style="font-size: 18px; color: #5f6368;"\u003eNo content\u003c/p\u003e'}
    \u003c/div\u003e`;

    slideCanvas.innerHTML = slideHTML;
  } else {
    // Fallback placeholder
    slideCanvas.innerHTML = `
      \u003cdiv class="slide-content"\u003e
        \u003ch2\u003eSlide ${slideNumber}\u003c/h2\u003e
        \u003cp\u003eSlide content will be displayed here\u003c/p\u003e
      \u003c/div\u003e
    `;
  }
}

function updateSlideCounter() {
  slideCounter.textContent = `${currentSlide} / ${totalSlides}`;
}

function updateNavigationButtons() {
  prevSlideBtn.disabled = currentSlide === 1;
  nextSlideBtn.disabled = currentSlide === totalSlides;
}

// Template Selection
function initTemplateSelection() {
  templateCards.forEach(card => {
    card.addEventListener('click', function () {
      const templateId = this.dataset.template;
      selectTemplate(templateId);
    });
  });

  // Tab switching (custom tab is disabled)
  tabButtons.forEach(button => {
    button.addEventListener('click', function () {
      if (this.classList.contains('disabled')) return;

      const tab = this.dataset.tab;
      switchTab(tab);
    });
  });
}

function selectTemplate(templateId) {
  selectedTemplate = templateId;

  // Update card selection
  templateCards.forEach(card => {
    if (card.dataset.template === templateId) {
      card.classList.add('selected');
    } else {
      card.classList.remove('selected');
    }
  });

  // Trigger template change (will integrate with backend later)
  console.log('Template changed to:', templateId);

  // TODO: Send request to regenerate presentation with new template
  // showTemplateChangeNotification(templateId);
}

function switchTab(tab) {
  // Update tab buttons
  tabButtons.forEach(button => {
    if (button.dataset.tab === tab) {
      button.classList.add('active');
    } else {
      button.classList.remove('active');
    }
  });

  // Update content visibility
  const defaultContent = document.getElementById('defaultTemplates');
  const customContent = document.getElementById('customTemplates');

  if (tab === 'default') {
    defaultContent.classList.remove('hidden');
    customContent.classList.add('hidden');
  } else if (tab === 'custom') {
    defaultContent.classList.add('hidden');
    customContent.classList.remove('hidden');
  }
}

// Button Actions
function initButtons() {
  downloadBtn.addEventListener('click', handleDownload);
  presentBtn.addEventListener('click', handlePresent);

  // Close template panel (for mobile)
  if (closeTemplatePanel) {
    closeTemplatePanel.addEventListener('click', function () {
      document.querySelector('.template-panel').classList.remove('open');
    });
  }
}

function handleDownload() {
  // TODO: Implement download functionality
  console.log('Download presentation');

  // Placeholder - will integrate with backend
  const jobId = getJobIdFromUrl();
  if (jobId) {
    window.location.href = `/download/${jobId}`;
  } else {
    alert('Download functionality will be available after processing');
  }
}

function handlePresent() {
  // Enter presentation mode (fullscreen)
  console.log('Present mode');

  const canvas = slideCanvas;
  if (canvas.requestFullscreen) {
    canvas.requestFullscreen();
  } else if (canvas.webkitRequestFullscreen) {
    canvas.webkitRequestFullscreen();
  } else if (canvas.mozRequestFullScreen) {
    canvas.mozRequestFullScreen();
  } else if (canvas.msRequestFullscreen) {
    canvas.msRequestFullscreen();
  }

  // Add fullscreen controls
  document.addEventListener('fullscreenchange', handleFullscreenChange);
}

function handleFullscreenChange() {
  if (!document.fullscreenElement) {
    // Exited fullscreen
    console.log('Exited presentation mode');
  }
}

// Utility Functions
function getJobIdFromUrl() {
  const pathParts = window.location.pathname.split('/');
  return pathParts[pathParts.length - 1];
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Mobile Menu Toggles
function toggleSlidesPanel() {
  const panel = document.querySelector('.slides-panel');
  panel.classList.toggle('open');
}

function toggleTemplatePanel() {
  const panel = document.querySelector('.template-panel');
  panel.classList.toggle('open');
}

// Export functions for external use
window.resultsPage = {
  goToSlide,
  selectTemplate,
  toggleSlidesPanel,
  toggleTemplatePanel
};
