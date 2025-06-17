# StoryMaker - Simplified Version

This is a simplified version of the StoryMaker children's book generator that only generates book covers and handles email workflow for payment and full book delivery.

## Features

- **Same Frontend**: Identical user interface as the full version
- **Cover Generation Only**: Generates only the book cover using AI
- **Email Workflow**: Stores order information and sends emails to admin and customer
- **Payment Simulation**: Simple payment processing (ready for integration with real payment processors)
- **Expert Review Promise**: Tells customers that expert writers will review and enhance their book

## How It Works

1. **User fills out the form** with their information, book details, and characters
2. **Cover generation** happens immediately using the existing AI pipeline
3. **Order information** is stored in JSON files and sent via email to admin
4. **Payment screen** shows the generated cover and asks for payment
5. **After payment**, customer receives confirmation and admin gets production notification
6. **Expert writers** (you) manually create the full book and deliver within 12 hours

## Setup Instructions

### Prerequisites
This simplified version requires the main project's `src` directory to function. Make sure you have the following structure:

```
book_publishing_api/
├── src/                    # Main project source code (required)
├── simplified_version/     # This simplified version
│   ├── app.py
│   ├── templates/
│   └── ...
└── ...
```

### 1. Install Dependencies

```bash
cd simplified_version
pip install -r requirements.txt
```

### 2. Configure Email Settings

Create or edit the `secrets.env` file in the simplified_version directory:

```env
# Email Configuration
ADMIN_EMAIL=admin@yourbookcompany.com
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# For Gmail, you'll need to:
# 1. Enable 2-factor authentication
# 2. Generate an "App Password" for this application
# 3. Use the app password instead of your regular password
```

### 3. Run the Application

**Option 1: Using the run script (recommended)**
```bash
cd simplified_version
chmod +x run.sh
./run.sh
```

**Option 2: Manual setup**
```bash
cd simplified_version
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The application will start on `http://localhost:5001` (different port to avoid conflicts with the full version).

## File Structure

```
simplified_version/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Frontend (identical to full version)
├── assets/               # Static assets (images, etc.)
├── temp_uploads/         # Temporary character image uploads
├── output/
│   ├── covers/          # Generated book covers
│   └── orders/          # Order JSON files
├── secrets.env          # Email and API configuration
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Order Management

### Order Files
Each order creates a JSON file in `output/orders/` with all the customer information and order details.

### Email Notifications
- **Admin notification**: Sent when cover is generated (before payment)
- **Customer confirmation**: Sent after successful payment
- **Production notification**: Urgent email to admin with 12-hour deadline

### Manual Fulfillment Process
1. Check `output/orders/` for paid orders
2. Use the full version to generate the complete book
3. Email the finished PDF to the customer
4. Update order status (optional)

## Customization

### Pricing
Change the price in `templates/index.html` around line 800:
```html
<div class="price-display">$19.99</div>
```

### Email Templates
Modify the email content in `app.py` in the functions:
- `send_admin_notification()`
- `send_customer_confirmation()`
- `send_production_notification()`

### Payment Integration
To integrate with a real payment processor like Stripe:
1. Add Stripe to requirements.txt
2. Replace the `processPayment()` function in the frontend
3. Update the `/api/payment` endpoint in the backend

## Production Deployment

### Security Considerations
- Use environment variables for all secrets
- Enable HTTPS
- Add rate limiting
- Validate all inputs
- Add CSRF protection

### Scaling
- Use a proper database instead of JSON files
- Add order management dashboard
- Implement automated email queues
- Add payment webhook handling

## Support

For questions about this simplified version, check the order files in `output/orders/` and email logs in the console output. 