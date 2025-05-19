// Backend API Integration for Book Publishing Web Interface

// This file handles the communication between the frontend and the backend API

class BookPublishingAPI {
    constructor() {
        this.baseUrl = window.location.origin; // Use the same origin for API calls
        this.endpoints = {
            generateBook: '/api/generate-book',
            getBookStatus: '/api/book-status',
            getBookPreview: '/api/book-preview'
        };
    }

    // Generate a new book based on user input
    async generateBook(bookData) {
        try {
            const response = await fetch(this.endpoints.generateBook, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    book_idea: bookData.book_idea,
                    title: bookData.title,
                    main_genre: bookData.main_genre,
                    writing_style: bookData.writing_style,
                    image_style: bookData.image_style
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();
            return {
                projectId: data.project_id,
                status: data.status
            };
        } catch (error) {
            console.error('Error generating book:', error);
            throw error;
        }
    }

    // Check the status of a book generation process
    async getBookStatus(projectId) {
        try {
            const response = await fetch(`${this.endpoints.getBookStatus}?project_id=${projectId}`);
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();
            return {
                status: data.status,
                progress: data.progress,
                currentStage: data.current_stage,
                pdfPath: data.pdf_path,
                error: data.error
            };
        } catch (error) {
            console.error('Error checking book status:', error);
            throw error;
        }
    }

    // Get book preview data
    async getBookPreview(projectId) {
        try {
            const response = await fetch(`${this.endpoints.getBookPreview}?project_id=${projectId}`);
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();
            return {
                title: data.title,
                coverImage: data.cover_image,
                pages: data.pages,
                pdfPath: data.pdf_path
            };
        } catch (error) {
            console.error('Error getting book preview:', error);
            throw error;
        }
    }
}

// Export the API instance
window.bookAPI = new BookPublishingAPI();
