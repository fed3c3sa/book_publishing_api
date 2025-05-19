// Enhanced book preview functionality with page turning animation
// This script extends main.js with more advanced book preview features

document.addEventListener('DOMContentLoaded', function() {
    // Add script reference to the main HTML file
    if (!document.querySelector('script[src="static/js/book-preview.js"]')) {
        const script = document.createElement('script');
        script.src = "static/js/book-preview.js";
        document.body.appendChild(script);
    }
});

// Book preview configuration
const bookPreviewConfig = {
    pageAccessLimit: 4, // First 2 pages (4 in turn.js counting both sides)
    purchased: false,
    currentBook: null,
    loadingPages: false
};

// Initialize the book preview with enhanced features
function initEnhancedBookPreview(bookData) {
    const book = document.querySelector('.book');
    
    // Clear any existing content
    book.innerHTML = '';
    
    // Store book data for later use
    bookPreviewConfig.currentBook = bookData;
    
    // Create cover and initial pages
    createBookPages(book, bookData);
    
    // Initialize turn.js with enhanced options
    $(book).turn({
        width: Math.min(800, window.innerWidth - 40),
        height: Math.min(600, window.innerHeight - 200),
        elevation: 50,
        gradients: true,
        autoCenter: true,
        acceleration: true, // Improves performance on mobile
        display: 'double', // Show two pages at once
        when: {
            turning: function(event, page, view) {
                // Check if user is trying to access restricted pages
                if (page > bookPreviewConfig.pageAccessLimit && !bookPreviewConfig.purchased) {
                    showPurchaseOverlay();
                    return event.preventDefault();
                }
                
                // Add page turning sound effect
                playPageTurnSound();
                
                // Add page shadow during animation
                addPageTurningShadow();
            },
            turned: function(event, page, view) {
                // Remove page shadow after animation completes
                removePageTurningShadow();
                
                // Update current page indicator
                updatePageIndicator(page);
                
                // Load more pages if needed (lazy loading)
                if (page > $(book).turn('pages') - 4 && !bookPreviewConfig.loadingPages) {
                    loadMorePages();
                }
            }
        }
    });
    
    // Make the book responsive
    makeBookResponsive();
    
    // Add page corner hover effect
    addPageCornerEffect();
    
    // Set up purchase button with enhanced animation
    setupEnhancedPurchaseButton();
    
    // Add ambient page movement
    addAmbientPageMovement();
}

// Create book pages with content
function createBookPages(book, bookData) {
    // First page (cover)
    const coverPage = document.createElement('div');
    coverPage.classList.add('hard', 'cover');
    
    // Use cover image if available, otherwise use styled title
    if (bookData.coverImage) {
        coverPage.innerHTML = `
            <div class="book-page cover-page">
                <img src="${bookData.coverImage}" alt="Book Cover" class="full-cover-image">
            </div>
        `;
    } else {
        coverPage.innerHTML = `
            <div class="book-page cover-page">
                <div class="cover-content">
                    <h1 class="book-title">${bookData.title || 'Your Generated Book'}</h1>
                    <div class="cover-decoration"></div>
                </div>
            </div>
        `;
    }
    book.appendChild(coverPage);
    
    // Inside cover page
    const insideCoverPage = document.createElement('div');
    insideCoverPage.classList.add('hard');
    insideCoverPage.innerHTML = `
        <div class="book-page inside-cover">
            <div class="page-content">
                <h2 class="inside-title">${bookData.title || 'Your Generated Book'}</h2>
                <p class="inside-subtitle">Created with Magical Book Creator</p>
                <div class="inside-decoration"></div>
            </div>
        </div>
    `;
    book.appendChild(insideCoverPage);
    
    // Add content pages
    for (let i = 0; i < 8; i++) {
        const page = document.createElement('div');
        page.innerHTML = `
            <div class="book-page">
                <div class="page-content">
                    <h2>Chapter ${Math.floor(i/2) + 1}</h2>
                    <p class="book-text">This is page ${i+1} of your book. ${i >= 2 ? 'This content is only visible after purchase.' : 'This is a preview of your generated book. The content is tailored to your specifications and includes custom illustrations.'}</p>
                    <div class="page-decoration"></div>
                    <div class="page-number ${i % 2 === 0 ? 'left' : 'right'}">${i+3}</div>
                </div>
            </div>
        `;
        book.appendChild(page);
    }
    
    // Back cover
    const backCoverPage = document.createElement('div');
    backCoverPage.classList.add('hard');
    backCoverPage.innerHTML = `
        <div class="book-page back-cover">
            <div class="page-content">
                <p class="back-cover-text">Thank you for exploring this book!</p>
                <div class="back-cover-decoration"></div>
            </div>
        </div>
    `;
    book.appendChild(backCoverPage);
}

// Add page corner hover effect
function addPageCornerEffect() {
    const book = document.querySelector('.book');
    
    // Add corner elements to each page
    $(book).find('div').not('.hard').each(function() {
        const corner = document.createElement('div');
        corner.classList.add('page-corner');
        this.appendChild(corner);
    });
    
    // Add hover effect
    $(document).on('mouseover', '.page-corner', function() {
        $(this).addClass('hover');
    }).on('mouseout', '.page-corner', function() {
        $(this).removeClass('hover');
    });
    
    // Add click effect
    $(document).on('click', '.page-corner', function() {
        const book = $('.book');
        const currentPage = book.turn('page');
        
        // Determine if it's a right or left page
        const isRightPage = $(this).parent().hasClass('p-even');
        
        if (isRightPage) {
            // Check access restrictions
            if (currentPage + 1 > bookPreviewConfig.pageAccessLimit && !bookPreviewConfig.purchased) {
                showPurchaseOverlay();
                return;
            }
            book.turn('next');
        } else {
            book.turn('previous');
        }
    });
}

// Make the book responsive
function makeBookResponsive() {
    const book = $('.book');
    
    // Update book size on window resize
    $(window).resize(function() {
        if (book.turn('is')) {
            const width = Math.min(800, window.innerWidth - 40);
            const height = Math.min(600, window.innerHeight - 200);
            
            book.turn('size', width, height);
            book.turn('center');
        }
    });
    
    // Handle touch events for mobile
    book.bind('touchstart', function(e) {
        const touchX = e.originalEvent.touches[0].pageX;
        const width = book.width();
        
        if (touchX < width * 0.3) {
            book.turn('previous');
        } else if (touchX > width * 0.7) {
            // Check access restrictions
            const currentPage = book.turn('page');
            if (currentPage + 1 > bookPreviewConfig.pageAccessLimit && !bookPreviewConfig.purchased) {
                showPurchaseOverlay();
                return;
            }
            book.turn('next');
        }
    });
}

// Enhanced purchase button setup
function setupEnhancedPurchaseButton() {
    const purchaseBtn = document.querySelector('.purchase-btn');
    if (purchaseBtn) {
        purchaseBtn.addEventListener('click', function() {
            // Add purchase animation
            this.classList.add('purchase-animation');
            
            // Set purchased flag
            bookPreviewConfig.purchased = true;
            
            // Hide overlay with fade effect
            const overlay = document.querySelector('.purchase-overlay');
            overlay.style.opacity = '0';
            
            // Show success message with animation
            const successMessage = document.createElement('div');
            successMessage.classList.add('success-message');
            successMessage.innerHTML = `
                <div class="success-icon">✓</div>
                <div class="success-text">Purchase successful! You now have access to the full book.</div>
            `;
            document.querySelector('.book-preview-container').prepend(successMessage);
            
            // Remove overlay and enable pointer events after animation
            setTimeout(() => {
                overlay.classList.remove('active');
                overlay.style.opacity = '1';
                this.classList.remove('purchase-animation');
            }, 1000);
            
            // Remove success message after a few seconds
            setTimeout(() => {
                successMessage.classList.add('fade-out');
                setTimeout(() => {
                    successMessage.remove();
                }, 500);
            }, 5000);
        });
    }
}

// Add ambient page movement
function addAmbientPageMovement() {
    const book = $('.book');
    
    // Subtle movement on mouse move
    $(document).on('mousemove', function(e) {
        if (!book.turn('is')) return;
        
        const mouseX = e.pageX / window.innerWidth;
        const mouseY = e.pageY / window.innerHeight;
        
        // Calculate rotation based on mouse position
        const rotateY = (mouseX - 0.5) * 5; // -2.5 to 2.5 degrees
        const rotateX = (mouseY - 0.5) * -5; // -2.5 to 2.5 degrees
        
        // Apply subtle rotation to book
        book.css('transform', `perspective(1200px) rotateY(${rotateY}deg) rotateX(${rotateX}deg)`);
    });
    
    // Reset on mouse leave
    $(document).on('mouseleave', function() {
        book.css('transform', 'perspective(1200px) rotateY(0deg) rotateX(0deg)');
    });
}

// Play page turning sound
function playPageTurnSound() {
    // Create audio element if it doesn't exist
    if (!window.pageTurnSound) {
        window.pageTurnSound = new Audio();
        window.pageTurnSound.src = 'data:audio/mp3;base64,SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA//tQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWGluZwAAAA8AAAACAAADmADMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzM//////////////////////////////////////////////////////////////////8AAAAATGF2YzU4LjEzAAAAAAAAAAAAAAAAJAAAAAAAAAAAA5hxuJBzAAAAAAAAAAAAAAAAAAAA//sUZAAP8AAAaQAAAAgAAA0gAAABAAABpAAAACAAADSAAAAETEFNRTMuMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//sUZB4P8AAAaQAAAAgAAA0gAAABAAABpAAAACAAADSAAAAEVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV//sUZDwP8AAAaQAAAAgAAA0gAAABAAABpAAAACAAADSAAAAEVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV';
        window.pageTurnSound.volume = 0.2;
    }
    
    // Play the sound
    window.pageTurnSound.currentTime = 0;
    window.pageTurnSound.play().catch(e => console.log('Audio play failed:', e));
}

// Add shadow during page turning
function addPageTurningShadow() {
    const book = document.querySelector('.book');
    book.classList.add('turning');
}

// Remove shadow after page turning
function removePageTurningShadow() {
    const book = document.querySelector('.book');
    book.classList.remove('turning');
}

// Update page indicator
function updatePageIndicator(page) {
    const pageIndicator = document.querySelector('.page-indicator');
    if (!pageIndicator) {
        const indicator = document.createElement('div');
        indicator.classList.add('page-indicator');
        document.querySelector('.book-controls').appendChild(indicator);
    }
    
    const book = $('.book');
    const totalPages = book.turn('pages');
    
    document.querySelector('.page-indicator').textContent = `Page ${page} of ${totalPages}`;
}

// Load more pages (simulated lazy loading)
function loadMorePages() {
    bookPreviewConfig.loadingPages = true;
    
    // Simulate loading delay
    setTimeout(() => {
        const book = $('.book');
        const currentPages = book.turn('pages');
        
        // Add more pages if needed
        if (currentPages < 20) {
            for (let i = 0; i < 4; i++) {
                const page = document.createElement('div');
                page.innerHTML = `
                    <div class="book-page">
                        <div class="page-content">
                            <h2>Additional Content</h2>
                            <p class="book-text">This is additional content that was loaded dynamically as you progressed through the book.</p>
                            <div class="page-decoration"></div>
                            <div class="page-number ${i % 2 === 0 ? 'left' : 'right'}">${currentPages + i + 1}</div>
                        </div>
                    </div>
                `;
                
                // Add corner effect to new pages
                const corner = document.createElement('div');
                corner.classList.add('page-corner');
                page.appendChild(corner);
                
                // Add to book
                book.turn('addPage', page, currentPages + i + 1);
            }
        }
        
        bookPreviewConfig.loadingPages = false;
    }, 1000);
}
