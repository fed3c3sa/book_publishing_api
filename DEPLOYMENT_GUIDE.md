# Google App Engine Deployment Guide

This guide will help you deploy your Book Publishing API to Google App Engine with Google Cloud Storage for file handling.

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK** installed on your local machine
3. **Python 3.12** installed locally
4. **Git** (for version control)

## Step 1: Set Up Google Cloud Project

### 1.1 Create a New Project
```bash
# Create a new project (replace with your preferred project ID)
gcloud projects create your-book-api-project-id --name="Book Publishing API"

# Set the project as default
gcloud config set project your-book-api-project-id

# Enable billing (required for App Engine)
# Do this through the Google Cloud Console: https://console.cloud.google.com/billing
```

### 1.2 Enable Required APIs
```bash
# Enable necessary APIs
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com
```

### 1.3 Initialize App Engine
```bash
# Initialize App Engine in your project
gcloud app create --region=us-central1
```

## Step 2: Create Google Cloud Storage Bucket

### 2.1 Create the Bucket
```bash
# Create a bucket for file storage (replace with your bucket name)
gsutil mb gs://your-book-api-storage-bucket

# Make bucket publicly readable (for serving covers)
gsutil iam ch allUsers:objectViewer gs://your-book-api-storage-bucket

# Optional: Set lifecycle policy to auto-delete old files
gsutil lifecycle set lifecycle.json gs://your-book-api-storage-bucket
```

### 2.2 Create Lifecycle Configuration (Optional)
Create `lifecycle.json` to automatically delete old temporary files:
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 30,
          "matchesPrefix": ["uploads/", "temp/"]
        }
      }
    ]
  }
}
```

## Step 3: Configure Environment Variables

### 3.1 Update app.yaml
Edit your `app.yaml` file and update the environment variables:

```yaml
env_variables:
  # Flask configuration
  FLASK_ENV: production
  SECRET_KEY: your-secret-key-here-change-this
  
  # File storage - UPDATE THIS
  GCS_BUCKET_NAME: your-book-api-storage-bucket
  
  # Add your API keys (set via gcloud for security)
  # OPENAI_API_KEY: set_via_gcloud_command
  # IDEOGRAM_API_KEY: set_via_gcloud_command
```

### 3.2 Set Secure Environment Variables
```bash
# Set sensitive environment variables (recommended approach)
gcloud app deploy --env-vars="OPENAI_API_KEY=your_openai_key,IDEOGRAM_API_KEY=your_ideogram_key,EMAIL_USER=your_email@gmail.com,EMAIL_PASSWORD=your_app_password,STRIPE_TEST_SECRET_KEY=sk_test_...,STRIPE_TEST_PUBLISHABLE_KEY=pk_test_...,ADMIN_EMAIL=admin@yourcompany.com,PRODUCTION_EMAIL=production@yourcompany.com"
```

Or set them individually:
```bash
# Set API keys
gcloud secrets create openai-api-key --data-file=-
# Enter your OpenAI API key when prompted

gcloud secrets create ideogram-api-key --data-file=-
# Enter your Ideogram API key when prompted

# Grant App Engine access to secrets
gcloud secrets add-iam-policy-binding openai-api-key \
    --member="serviceAccount:your-book-api-project-id@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## Step 4: Prepare for Deployment

### 4.1 Test Locally (Optional)
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables locally
export GCS_BUCKET_NAME=your-book-api-storage-bucket
export OPENAI_API_KEY=your_openai_key
export IDEOGRAM_API_KEY=your_ideogram_key

# Run locally
python app.py
```

### 4.2 Verify Files
Make sure these files are in your project root:
- `app.yaml` ✓
- `.gcloudignore` ✓
- `requirements.txt` ✓
- `app.py` ✓
- All your `app/` directory files ✓

## Step 5: Deploy to App Engine

### 5.1 First Deployment
```bash
# Deploy the application
gcloud app deploy app.yaml

# Deploy will take 5-10 minutes
# You'll see the deployment URL when complete
```

### 5.2 Set Custom Environment Variables
If you didn't set them during deploy:
```bash
# Update environment variables
gcloud app deploy --env-vars="GCS_BUCKET_NAME=your-book-api-storage-bucket"
```

### 5.3 View Your App
```bash
# Open your deployed app
gcloud app browse
```

## Step 6: Configure Stripe Webhooks

### 6.1 Get Your App URL
```bash
# Get your app URL
gcloud app describe --format="value(defaultHostname)"
# Result: your-project-id.uc.r.appspot.com
```

### 6.2 Set Up Stripe Webhook
1. Go to Stripe Dashboard → Webhooks
2. Add endpoint: `https://your-project-id.uc.r.appspot.com/api/webhook/stripe`
3. Select events: `checkout.session.completed`
4. Copy the webhook secret

### 6.3 Update Webhook Secret
```bash
# Update your app with the webhook secret
gcloud app deploy --env-vars="STRIPE_TEST_WEBHOOK_SECRET=whsec_your_webhook_secret"
```

## Step 7: Test Your Deployment

### 7.1 Health Check
```bash
curl https://your-project-id.uc.r.appspot.com/health
# Should return: {"status": "healthy", "service": "book_publishing_api"}
```

### 7.2 Test File Upload
1. Visit your app URL
2. Try uploading a character image
3. Generate a book cover
4. Complete a test payment

### 7.3 Check Cloud Storage
```bash
# List files in your bucket
gsutil ls gs://your-book-api-storage-bucket/

# You should see directories like:
# gs://your-book-api-storage-bucket/covers/
# gs://your-book-api-storage-bucket/orders/
# gs://your-book-api-storage-bucket/characters/
```

## Step 8: Monitoring and Logs

### 8.1 View Logs
```bash
# View recent logs
gcloud app logs tail -s default

# View specific logs
gcloud app logs read --service=default --limit=50
```

### 8.2 Monitor in Console
Visit Google Cloud Console:
- App Engine Dashboard: https://console.cloud.google.com/appengine
- Cloud Storage: https://console.cloud.google.com/storage
- Logs: https://console.cloud.google.com/logs

## Step 9: Updating Your App

### 9.1 Deploy Updates
```bash
# After making code changes
gcloud app deploy app.yaml

# Deploy only if tests pass
gcloud app deploy --promote --stop-previous-version
```

### 9.2 Manage Versions
```bash
# List versions
gcloud app versions list

# Delete old versions to save costs
gcloud app versions delete old-version-id
```

## Troubleshooting

### Common Issues

#### 1. "GCS_BUCKET_NAME not set" Error
- Make sure you've set the environment variable in `app.yaml`
- Redeploy after updating

#### 2. "Permission denied" for Cloud Storage
```bash
# Check bucket permissions
gsutil iam get gs://your-book-api-storage-bucket

# Grant App Engine service account access
gsutil iam ch serviceAccount:your-project-id@appspot.gserviceaccount.com:objectAdmin gs://your-book-api-storage-bucket
```

#### 3. Email Not Sending
- Verify EMAIL_USER and EMAIL_PASSWORD are set
- Use App Passwords for Gmail (not regular password)
- Check that less secure app access is enabled (Gmail)

#### 4. Stripe Webhooks Not Working
- Verify webhook URL is correct
- Check webhook secret is properly set
- Ensure events are properly configured in Stripe

### Cost Optimization

#### 1. Use Basic Scaling
Your `app.yaml` already includes basic scaling to minimize costs:
```yaml
basic_scaling:
  max_instances: 10
  idle_timeout: 10m
```

#### 2. Monitor Usage
```bash
# Check current costs
gcloud billing budgets list

# Set up billing alerts in Cloud Console
```

#### 3. Clean Up Resources
```bash
# Delete old versions
gcloud app versions list
gcloud app versions delete VERSION_ID

# Clean up old files in storage
gsutil rm gs://your-bucket/old-files/**
```

## Security Considerations

1. **Never commit secrets** - Use environment variables or Secret Manager
2. **Use HTTPS only** - App Engine enforces this by default
3. **Validate file uploads** - The code includes file type validation
4. **Monitor access logs** - Check for unusual activity
5. **Regular updates** - Keep dependencies updated

## Production Checklist

- [ ] Custom domain configured (optional)
- [ ] SSL certificate set up (automatic with App Engine)
- [ ] Error monitoring configured
- [ ] Backup strategy for important data
- [ ] Monitoring and alerting set up
- [ ] Performance testing completed
- [ ] Security review completed
- [ ] Documentation updated

## Support

If you encounter issues:
1. Check the logs first: `gcloud app logs tail`
2. Verify environment variables are set correctly
3. Test individual components (storage, email, Stripe)
4. Check Google Cloud Status: https://status.cloud.google.com/

Your Book Publishing API is now ready for production use on Google App Engine! 🚀 