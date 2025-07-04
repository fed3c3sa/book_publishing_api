# Book Publishing API - Production Version

A Flask-based web application that generates personalized children's book covers using AI and handles payment processing for complete book orders.

## Features

- ✨ AI-powered book cover generation
- 🎨 Character processing (text descriptions or image uploads)
- 💳 Stripe payment integration
- 📧 Email notifications
- 🌍 Multi-language support (Italian/English)
- 📱 Responsive web interface
- 🔒 Secure file handling

## Project Structure

```
book_publishing_api/
├── app/                          # Main application package
│   ├── routes/                   # API route blueprints
│   │   ├── asset_routes.py      # Static assets and templates
│   │   ├── book_routes.py       # Book cover generation
│   │   ├── payment_routes.py    # Stripe payment processing
│   │   └── upload_routes.py     # File upload handling
│   ├── services/                # Business logic modules
│   │   ├── book_generation_service.py  # Cover generation service
│   │   ├── email_service.py            # Email notifications
│   │   ├── ai_clients/                 # AI client integrations
│   │   ├── book_planning/              # Story planning logic
│   │   ├── character_processing/       # Character handling
│   │   ├── content_generation/         # Image/text generation
│   │   └── utils/                      # Configuration utilities
│   └── models/                   # Data models
├── config/                       # Configuration files
│   └── stripe_config.py         # Stripe payment configuration
├── templates/                    # Frontend HTML templates
│   ├── index.html               # Main application interface
│   └── success.html             # Payment success page
├── static/                       # Static assets
│   └── assets/                  # Frontend assets (CSS, JS, images)
├── output/                       # Generated files
│   ├── covers/                  # Generated book covers
│   └── orders/                  # Order data
├── temp_uploads/                # Temporary file uploads
├── tos/                         # Terms of Service files
├── app.py                       # Main application entry point
└── requirements.txt             # Python dependencies
```

## Quick Start

### 1. Environment Setup

Create a `secrets.env` file with your configuration:

```env
# Environment
ENVIRONMENT=local  # local, staging, production

# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Ideogram API (for image generation)
IDEOGRAM_API_KEY=your_ideogram_api_key

# Email Configuration (optional)
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
ADMIN_EMAIL=admin@yourcompany.com

# Stripe Configuration
STRIPE_TEST_SECRET_KEY=sk_test_...
STRIPE_TEST_PUBLISHABLE_KEY=pk_test_...
STRIPE_TEST_WEBHOOK_SECRET=whsec_...

# Production Stripe (for production only)
STRIPE_LIVE_SECRET_KEY=sk_live_...
STRIPE_LIVE_PUBLISHABLE_KEY=pk_live_...
STRIPE_LIVE_WEBHOOK_SECRET=whsec_...

# Application
SECRET_KEY=your_secret_key_here
PORT=5001
```

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd book_publishing_api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application

```bash
# Development mode
python app.py

# Production mode (with gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

The application will be available at `http://localhost:5001`

## API Endpoints

### Book Generation
- `POST /api/generate` - Generate book cover and create order
- `GET /api/cover/<order_id>` - Retrieve generated cover image

### Payment Processing
- `POST /api/create-checkout-session` - Create Stripe checkout session
- `POST /api/webhook/stripe` - Stripe webhook handler
- `GET /api/mock-payment/<order_id>` - Mock payment (development only)

### File Upload
- `POST /api/upload_character_image` - Upload character images

### Static Assets
- `GET /` - Main application interface
- `GET /assets/<filename>` - Static assets
- `GET /tos/<filename>` - Terms of Service files
- `GET /success` - Payment success page

## Configuration

### Stripe Integration

The application supports both test and live Stripe modes:

- **Local Development**: Uses mock payments by default
- **Staging**: Uses Stripe test keys
- **Production**: Uses Stripe live keys

Configure webhook endpoints in your Stripe dashboard:
- Test: `https://your-domain.com/api/webhook/stripe`
- Live: `https://your-domain.com/api/webhook/stripe`

### Email Notifications

Email notifications are sent for:
- New order created (to admin)
- Payment confirmed (to customer)
- Production needed (to admin)

Configure SMTP settings in `secrets.env`.

## Development

### Adding New Routes

1. Create a new route file in `app/routes/`
2. Define a Blueprint with your routes
3. Register the blueprint in `app.py`

### Adding New Services

1. Create service files in `app/services/`
2. Import and use in your routes
3. Follow the existing patterns for error handling

### Frontend Customization

The frontend is a single-page application in `templates/index.html` with:
- Multi-language support via `static/assets/translations.js`
- Responsive design
- Payment integration

## Deployment

### Environment Variables

Set `ENVIRONMENT=production` and configure all production keys.

### Security Considerations

- Use strong `SECRET_KEY` in production
- Configure proper CORS settings
- Use HTTPS in production
- Validate file uploads properly
- Secure webhook endpoints

### Monitoring

- Monitor `/api/webhook/stripe` for payment events
- Check `output/orders/` for order data
- Monitor email delivery status

## License

[Your License Here]

## Support

For support, email [your-support-email] or create an issue in the repository.

