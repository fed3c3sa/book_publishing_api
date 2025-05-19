// Updated main.js to correctly connect to backend like Streamlit
document.addEventListener('DOMContentLoaded', function() {
    // Initialize particles background
    initParticles();
    
    // Form submission handling
    const bookForm = document.getElementById('book-form');
    if (bookForm) {
        bookForm.addEventListener('submit', handleFormSubmit);
    }
    
    // Book navigation controls
    setupBookControls();
});

// Initialize particles background with enhanced visibility
function initParticles() {
    const particlesContainer = document.querySelector('.particles-container');
    if (!particlesContainer) return;
    
    // Create particles - increased number for more visibility
    for (let i = 0; i < 80; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        // Random position
        const posX = Math.random() * 100;
        const posY = Math.random() * 100;
        
        // Larger size for more visibility
        const size = Math.random() * 8 + 2;
        
        // Higher opacity for more visibility
        const opacity = Math.random() * 0.7 + 0.2;
        
        // Random color (blue hues)
        const hue = Math.random() * 40 + 190; // 190-230 is blue range
        
        // Apply styles
        particle.style.left = `${posX}%`;
        particle.style.top = `${posY}%`;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.opacity = opacity;
        particle.style.backgroundColor = `hsl(${hue}, 80%, 65%)`;
        
        // Add animation with random duration
        const duration = Math.random() * 15 + 8; // Slightly faster
        particle.style.animation = `float ${duration}s infinite ease-in-out`;
        
        // Add glow effect for more visibility
        particle.style.boxShadow = `0 0 ${size * 1.5}px hsl(${hue}, 80%, 65%)`;
        
        // Append to container
        particlesContainer.appendChild(particle);
    }
}

// Handle form submission - updated to match Streamlit workflow
async function handleFormSubmit(event) {
    event.preventDefault();
    
    // Get form data
    const formData = new FormData(event.target);
    const bookData = {
        book_idea: formData.get('book-idea'),
        title: formData.get('title'),
        main_genre: formData.get('genre'),
        writing_style: formData.get('writing-style'),
        image_style: formData.get('image-style'),
        enable_trend_finder: document.getElementById('trend-finder').checked,
        enable_style_imitator: document.getElementById('style-imitator').checked,
        style_imitator_example_text: document.getElementById('style-imitator-text').value,
        enable_translator: document.getElementById('translator').checked,
        target_language: document.getElementById('target-language').value
    };
    
    // Minimize form and show progress
    minimizeForm();
    showProgress();
    
    try {
        // Start the book generation process
        const response = await fetch('/api/generate-book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(bookData)
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        const projectId = data.project_id;
        
        // Poll for status updates
        await pollBookStatus(projectId);
        
    } catch (error) {
        console.error('Error generating book:', error);
        showError('An error occurred while generating your book. Please try again.');
        resetForm();
    }
}

// Poll for book generation status
async function pollBookStatus(projectId) {
    const maxAttempts = 300; // 5 minutes at 1-second intervals
    let attempts = 0;
    
    const statusInterval = setInterval(async () => {
        attempts++;
        
        if (attempts > maxAttempts) {
            clearInterval(statusInterval);
            showError('Book generation is taking longer than expected. Please check back later.');
            return;
        }
        
        try {
            const response = await fetch(`/api/book-status?project_id=${projectId}`);
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Update progress
            updateProgress(data.progress, data.current_stage);
            
            // Check if complete or failed
            if (data.status === 'completed') {
                clearInterval(statusInterval);
                hideProgress();
                await showBookResults(projectId);
            } else if (data.status === 'failed') {
                clearInterval(statusInterval);
                showError(`Book generation failed: ${data.error}`);
                resetForm();
            }
            
        } catch (error) {
            console.error('Error checking book status:', error);
        }
    }, 1000); // Check every second
}

// Update progress indicators
function updateProgress(percent, status) {
    const progressBar = document.querySelector('.progress-bar');
    const progressPercentage = document.querySelector('.progress-percentage');
    const progressStatus = document.querySelector('.progress-status');
    
    progressBar.style.width = `${percent}%`;
    progressPercentage.textContent = `${percent}%`;
    progressStatus.textContent = status;
}

// Show book results after generation is complete
async function showBookResults(projectId) {
    try {
        const response = await fetch(`/api/book-preview?project_id=${projectId}`);
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Show success message
        const successMessage = document.createElement('div');
        successMessage.classList.add('success-message');
        successMessage.innerHTML = `
            <div class="success-icon">✓</div>
            <div class="success-text">Book generation completed successfully!</div>
        `;
        document.querySelector('.container').prepend(successMessage);
        
        // Create results container
        const resultsContainer = document.createElement('div');
        resultsContainer.classList.add('results-container');
        
        // Add download button
        const downloadButton = document.createElement('a');
        downloadButton.classList.add('btn', 'download-btn');
        downloadButton.href = `/download-pdf/${projectId}`;
        downloadButton.textContent = 'Download Book (PDF)';
        resultsContainer.appendChild(downloadButton);
        
        // Add book preview
        const previewContainer = document.createElement('div');
        previewContainer.classList.add('book-preview-container');
        previewContainer.classList.add('active');
        
        // Book preview title
        const previewTitle = document.createElement('h2');
        previewTitle.textContent = 'Your Book Preview';
        previewContainer.appendChild(previewTitle);
        
        // Book element for turn.js
        const bookElement = document.createElement('div');
        bookElement.classList.add('book');
        previewContainer.appendChild(bookElement);
        
        // Book controls
        const bookControls = document.createElement('div');
        bookControls.classList.add('book-controls');
        bookControls.innerHTML = `
            <button class="book-control-btn prev-page">Previous Page</button>
            <button class="book-control-btn next-page">Next Page</button>
        `;
        previewContainer.appendChild(bookControls);
        
        // Purchase overlay
        const purchaseOverlay = document.createElement('div');
        purchaseOverlay.classList.add('purchase-overlay');
        purchaseOverlay.innerHTML = `
            <div class="purchase-message">
                <h3>Want to see more?</h3>
                <p>Purchase the full book to unlock all pages!</p>
            </div>
            <button class="btn purchase-btn">Purchase Now</button>
        `;
        previewContainer.appendChild(purchaseOverlay);
        
        // Add expandable sections for additional outputs
        const expandableSection = document.createElement('div');
        expandableSection.classList.add('expandable-sections');
        
        // Book plan expander
        const bookPlanExpander = document.createElement('div');
        bookPlanExpander.classList.add('expander');
        bookPlanExpander.innerHTML = `
            <div class="expander-header">
                <h3>Book Plan</h3>
                <span class="expander-icon">+</span>
            </div>
            <div class="expander-content">
                <pre class="code-block" id="book-plan-content">Loading...</pre>
            </div>
        `;
        expandableSection.appendChild(bookPlanExpander);
        
        // Story summary expander
        const storySummaryExpander = document.createElement('div');
        storySummaryExpander.classList.add('expander');
        storySummaryExpander.innerHTML = `
            <div class="expander-header">
                <h3>Story Summary</h3>
                <span class="expander-icon">+</span>
            </div>
            <div class="expander-content">
                <pre class="code-block" id="story-summary-content">Loading...</pre>
            </div>
        `;
        expandableSection.appendChild(storySummaryExpander);
        
        // Image log expander
        const imageLogExpander = document.createElement('div');
        imageLogExpander.classList.add('expander');
        imageLogExpander.innerHTML = `
            <div class="expander-header">
                <h3>Image Log</h3>
                <span class="expander-icon">+</span>
            </div>
            <div class="expander-content">
                <pre class="code-block" id="image-log-content">Loading...</pre>
            </div>
        `;
        expandableSection.appendChild(imageLogExpander);
        
        // Add all elements to the page
        resultsContainer.appendChild(previewContainer);
        resultsContainer.appendChild(expandableSection);
        document.querySelector('.container').appendChild(resultsContainer);
        
        // Initialize book preview
        initEnhancedBookPreview({
            title: data.title,
            coverImage: data.cover_image,
            pdfPath: data.pdf_path
        });
        
        // Set up expanders
        setupExpanders();
        
        // Load expander content
        loadExpanderContent('book-plan-content', `/view-book-plan/${projectId}`);
        loadExpanderContent('story-summary-content', `/view-story-summary/${projectId}`);
        loadExpanderContent('image-log-content', `/view-image-log/${projectId}`);
        
        // Remove success message after a few seconds
        setTimeout(() => {
            successMessage.remove();
        }, 5000);
        
    } catch (error) {
        console.error('Error showing book results:', error);
        showError('An error occurred while retrieving your book. Please try again.');
    }
}

// Load content for expanders
async function loadExpanderContent(elementId, url) {
    try {
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const content = await response.text();
        document.getElementById(elementId).textContent = content;
        
    } catch (error) {
        console.error(`Error loading content from ${url}:`, error);
        document.getElementById(elementId).textContent = 'Error loading content';
    }
}

// Set up expandable sections
function setupExpanders() {
    const expanders = document.querySelectorAll('.expander-header');
    
    expanders.forEach(expander => {
        expander.addEventListener('click', () => {
            const content = expander.nextElementSibling;
            const icon = expander.querySelector('.expander-icon');
            
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
                icon.textContent = '+';
            } else {
                content.style.maxHeight = content.scrollHeight + 'px';
                icon.textContent = '-';
            }
        });
    });
}

// Minimize the form after submission
function minimizeForm() {
    const formContainer = document.querySelector('.form-container');
    formContainer.classList.add('minimized');
    
    // Create a summary of the submission
    const summary = document.createElement('div');
    summary.classList.add('form-summary');
    
    const title = document.querySelector('#title').value || 'Untitled Book';
    const idea = document.querySelector('#book-idea').value;
    const shortIdea = idea.length > 50 ? idea.substring(0, 50) + '...' : idea;
    
    summary.innerHTML = `<strong>${title}</strong>: ${shortIdea}`;
    
    // Clear form content and add summary
    formContainer.innerHTML = '';
    formContainer.appendChild(summary);
}

// Show progress indicators
function showProgress() {
    const progressContainer = document.querySelector('.progress-container');
    progressContainer.classList.add('active');
}

// Hide progress indicators
function hideProgress() {
    const progressContainer = document.querySelector('.progress-container');
    progressContainer.classList.remove('active');
}

// Show error message
function showError(message) {
    const errorContainer = document.createElement('div');
    errorContainer.classList.add('error-message');
    errorContainer.textContent = message;
    
    document.querySelector('.container').prepend(errorContainer);
    
    // Remove after a few seconds
    setTimeout(() => {
        errorContainer.remove();
    }, 5000);
}

// Reset form to initial state
function resetForm() {
    const formContainer = document.querySelector('.form-container');
    formContainer.classList.remove('minimized');
    
    // Reload the page to reset everything
    location.reload();
}

// Set up book navigation controls
function setupBookControls() {
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('prev-page')) {
            $('.book').turn('previous');
        } else if (e.target.classList.contains('next-page')) {
            // Check if user is trying to access restricted pages
            const currentPage = $('.book').turn('page');
            if (currentPage >= 4 && !window.bookPurchased) {
                showPurchaseOverlay();
                return;
            }
            $('.book').turn('next');
        } else if (e.target.classList.contains('purchase-btn')) {
            handlePurchase();
        }
    });
}

// Show purchase overlay
function showPurchaseOverlay() {
    const overlay = document.querySelector('.purchase-overlay');
    if (overlay) {
        overlay.classList.add('active');
    }
}

// Handle purchase action
function handlePurchase() {
    // Set purchased flag
    window.bookPurchased = true;
    
    // Hide overlay
    const overlay = document.querySelector('.purchase-overlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
    
    // Show success message
    const successMessage = document.createElement('div');
    successMessage.classList.add('success-message');
    successMessage.textContent = 'Purchase successful! You now have access to the full book.';
    document.querySelector('.book-preview-container').prepend(successMessage);
    
    // Remove message after a few seconds
    setTimeout(() => {
        successMessage.remove();
    }, 5000);
}

// Add CSS animation for particles
const style = document.createElement('style');
style.textContent = `
@keyframes float {
    0%, 100% {
        transform: translateY(0) translateX(0);
    }
    25% {
        transform: translateY(-20px) translateX(10px);
    }
    50% {
        transform: translateY(-35px) translateX(-15px);
    }
    75% {
        transform: translateY(-20px) translateX(15px);
    }
}

.particle {
    position: absolute;
    border-radius: 50%;
    pointer-events: none;
}

.expander {
    margin-bottom: 1rem;
    border-radius: 5px;
    overflow: hidden;
    background-color: var(--bg-secondary);
}

.expander-header {
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    background-color: rgba(41, 182, 246, 0.1);
}

.expander-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
    padding: 0 1rem;
}

.expander-content.active {
    max-height: 500px;
    padding: 1rem;
}

.code-block {
    background-color: rgba(0, 0, 0, 0.2);
    padding: 1rem;
    border-radius: 5px;
    overflow: auto;
    max-height: 300px;
    font-family: monospace;
    white-space: pre-wrap;
}

.results-container {
    margin-top: 2rem;
}

.download-btn {
    display: block;
    margin: 1rem auto;
    text-align: center;
    text-decoration: none;
}
`;
document.head.appendChild(style);
