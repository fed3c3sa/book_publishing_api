// Multi-layer moving background and PDF book viewer implementation

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the multi-layer background
    initBackgroundLayers();
    
    // Initialize PDF book modal functionality
    initPdfBookModal();
});

// Initialize background layers with the provided images
function initBackgroundLayers() {
    // Create background container if it doesn't exist
    let backgroundContainer = document.querySelector('.background-container');
    if (!backgroundContainer) {
        backgroundContainer = document.createElement('div');
        backgroundContainer.classList.add('background-container');
        document.body.appendChild(backgroundContainer);
    }
    
    // Create background layer
    const backgroundLayer = document.createElement('div');
    backgroundLayer.classList.add('background-layer');
    backgroundContainer.appendChild(backgroundLayer);
    
    // List of image filenames
    const imageFiles = [
        'generated_image_956983.png',
        'generated_image_922544.png',
        'generated_image_451ca8.png',
        'generated_image_2974c5.png',
        'generated_image_b1aa64.png',
        'generated_image_6c298c.png',
        'generated_image_5f5680.png'
    ];
    
    // Add each image to the background layer
    imageFiles.forEach((filename, index) => {
        const img = document.createElement('img');
        img.src = `static/images/${filename}`;
        img.alt = `Background decoration ${index + 1}`;
        img.classList.add('background-image');
        
        // Add some randomness to initial positions
        const randomTop = Math.random() * 70 + 10; // 10% to 80%
        const randomLeft = Math.random() * 70 + 10; // 10% to 80%
        
        img.style.top = `${randomTop}%`;
        img.style.left = `${randomLeft}%`;
        
        backgroundLayer.appendChild(img);
    });
    
    // Add subtle movement on mouse move for parallax effect
    document.addEventListener('mousemove', function(e) {
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;
        
        const images = document.querySelectorAll('.background-image');
        images.forEach((img, index) => {
            // Different movement factors for each layer
            const moveFactor = 15 + (index * 5); // Increasing movement for deeper layers
            const moveX = (mouseX - 0.5) * moveFactor;
            const moveY = (mouseY - 0.5) * moveFactor;
            
            // Apply subtle transform in addition to the animation
            img.style.transform = `translate(${moveX}px, ${moveY}px)`;
        });
    });
}

// Initialize the PDF book modal
function initPdfBookModal() {
    // Create modal container
    const modal = document.createElement('div');
    modal.classList.add('book-modal');
    
    // Create modal content
    modal.innerHTML = `
        <div class="book-modal-content">
            <div class="book-modal-close">&times;</div>
            <div class="pdf-book">
                <div class="pdf-loading">
                    <div class="spinner"></div>
                    <div>Loading your book...</div>
                </div>
            </div>
            <div class="page-turner left">
                <div class="page-curl"></div>
            </div>
            <div class="page-turner right">
                <div class="page-curl"></div>
            </div>
            <div class="page-number-display">Page <span class="current-page">1</span> of <span class="total-pages">0</span></div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Set up event listeners for the modal
    const closeButton = modal.querySelector('.book-modal-close');
    closeButton.addEventListener('click', function() {
        modal.classList.remove('active');
    });
    
    // Close modal on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            modal.classList.remove('active');
        }
    });
    
    // Prevent clicks inside modal from closing it
    modal.querySelector('.book-modal-content').addEventListener('click', function(e) {
        e.stopPropagation();
    });
    
    // Add global function to open the PDF book modal
    window.openPdfBookModal = function(pdfUrl, title) {
        const pdfBook = modal.querySelector('.pdf-book');
        const loadingIndicator = modal.querySelector('.pdf-loading');
        
        // Clear previous content
        while (pdfBook.children.length > 1) { // Keep the loading indicator
            pdfBook.removeChild(pdfBook.lastChild);
        }
        
        // Show loading indicator
        loadingIndicator.style.display = 'block';
        
        // Show the modal
        modal.classList.add('active');
        
        // Load the PDF using PDF.js
        loadPdf(pdfUrl, pdfBook, loadingIndicator);
    };
    
    // Set up page turners
    const leftTurner = modal.querySelector('.page-turner.left');
    const rightTurner = modal.querySelector('.page-turner.right');
    
    leftTurner.addEventListener('click', function() {
        turnPage('previous');
    });
    
    rightTurner.addEventListener('click', function() {
        turnPage('next');
    });
    
    // Add swipe gesture support
    let touchStartX = 0;
    let touchEndX = 0;
    
    modal.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
    });
    
    modal.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });
    
    function handleSwipe() {
        const swipeThreshold = 50;
        if (touchEndX < touchStartX - swipeThreshold) {
            // Swipe left
            turnPage('next');
        } else if (touchEndX > touchStartX + swipeThreshold) {
            // Swipe right
            turnPage('previous');
        }
    }
}

// Load PDF using PDF.js
function loadPdf(pdfUrl, container, loadingIndicator) {
    // We'll use PDF.js to render the PDF
    // First, dynamically load PDF.js if not already loaded
    if (typeof pdfjsLib === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.min.js';
        script.onload = function() {
            // Set worker source
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.worker.min.js';
            renderPdf(pdfUrl, container, loadingIndicator);
        };
        document.head.appendChild(script);
    } else {
        renderPdf(pdfUrl, container, loadingIndicator);
    }
}

// Render PDF pages
function renderPdf(pdfUrl, container, loadingIndicator) {
    pdfjsLib.getDocument(pdfUrl).promise.then(function(pdf) {
        // Hide loading indicator
        loadingIndicator.style.display = 'none';
        
        // Update total pages
        const totalPagesElement = document.querySelector('.total-pages');
        totalPagesElement.textContent = pdf.numPages;
        
        // Store PDF data in window object for later use
        window.pdfData = {
            pdf: pdf,
            currentPage: 1,
            totalPages: pdf.numPages
        };
        
        // Render initial pages (first two pages)
        renderPage(1, container, 'left');
        if (pdf.numPages > 1) {
            renderPage(2, container, 'right');
        }
    }).catch(function(error) {
        console.error('Error loading PDF:', error);
        loadingIndicator.innerHTML = `
            <div>Error loading PDF: ${error.message}</div>
        `;
    });
}

// Render a specific page
function renderPage(pageNumber, container, position) {
    const pdf = window.pdfData.pdf;
    
    pdf.getPage(pageNumber).then(function(page) {
        const viewport = page.getViewport({ scale: 1.5 });
        
        // Create page div if it doesn't exist
        let pageDiv = container.querySelector(`.pdf-page.page-${pageNumber}`);
        if (!pageDiv) {
            pageDiv = document.createElement('div');
            pageDiv.classList.add('pdf-page', `page-${pageNumber}`);
            if (position) {
                pageDiv.classList.add(position);
            }
            container.appendChild(pageDiv);
        }
        
        // Create canvas for rendering
        const canvas = document.createElement('canvas');
        canvas.classList.add('pdf-page-content');
        const context = canvas.getContext('2d');
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        
        // Clear previous content
        pageDiv.innerHTML = '';
        pageDiv.appendChild(canvas);
        
        // Render PDF page
        page.render({
            canvasContext: context,
            viewport: viewport
        });
    });
}

// Turn page function
function turnPage(direction) {
    if (!window.pdfData) return;
    
    const { pdf, currentPage, totalPages } = window.pdfData;
    const container = document.querySelector('.pdf-book');
    
    if (direction === 'next' && currentPage < totalPages) {
        // Animate page turn
        const currentPageElement = container.querySelector(`.page-${currentPage}`);
        if (currentPageElement) {
            currentPageElement.style.transform = 'rotateY(-180deg)';
            
            // After animation, update pages
            setTimeout(() => {
                // Remove old pages
                const oldPages = container.querySelectorAll('.pdf-page');
                oldPages.forEach(page => container.removeChild(page));
                
                // Update current page
                window.pdfData.currentPage = Math.min(currentPage + 2, totalPages);
                
                // Render new pages
                renderPage(window.pdfData.currentPage, container, 'left');
                if (window.pdfData.currentPage < totalPages) {
                    renderPage(window.pdfData.currentPage + 1, container, 'right');
                }
                
                // Update page number display
                document.querySelector('.current-page').textContent = window.pdfData.currentPage;
            }, 500);
        }
    } else if (direction === 'previous' && currentPage > 1) {
        // Animate page turn
        const previousPageElement = container.querySelector(`.page-${currentPage - 1}`);
        if (previousPageElement) {
            previousPageElement.style.transform = 'rotateY(0deg)';
            
            // After animation, update pages
            setTimeout(() => {
                // Remove old pages
                const oldPages = container.querySelectorAll('.pdf-page');
                oldPages.forEach(page => container.removeChild(page));
                
                // Update current page
                window.pdfData.currentPage = Math.max(currentPage - 2, 1);
                
                // Render new pages
                renderPage(window.pdfData.currentPage, container, 'left');
                if (window.pdfData.currentPage < totalPages) {
                    renderPage(window.pdfData.currentPage + 1, container, 'right');
                }
                
                // Update page number display
                document.querySelector('.current-page').textContent = window.pdfData.currentPage;
            }, 500);
        }
    }
}

// Add a function to open the book preview with the actual PDF
function enhanceBookPreview() {
    // Override the showBookResults function to use the PDF modal
    window.originalShowBookResults = window.showBookResults;
    
    window.showBookResults = async function(projectId) {
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
            
            // Add view book button
            const viewBookButton = document.createElement('button');
            viewBookButton.classList.add('btn', 'view-book-btn');
            viewBookButton.textContent = 'View Book';
            viewBookButton.addEventListener('click', function() {
                openPdfBookModal(data.pdf_path, data.title);
            });
            resultsContainer.appendChild(viewBookButton);
            
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
            resultsContainer.appendChild(expandableSection);
            document.querySelector('.container').appendChild(resultsContainer);
            
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
    };
}

// Call the enhancement function when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    enhanceBookPreview();
});
