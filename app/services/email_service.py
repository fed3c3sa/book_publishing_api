"""
Email Service
Handles email notifications for orders and payments
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any

class EmailService:
    """Service for handling email notifications"""
    
    def __init__(self):
        """Initialize email configuration"""
        self.admin_email = os.getenv('ADMIN_EMAIL', 'admin@yourbookcompany.com')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
    
    def _send_email(self, to_email: str, subject: str, body: str) -> None:
        """
        Send email using SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body text
        """
        try:
            if not self.email_user or not self.email_password:
                print("Email credentials not configured, skipping email")
                return
            
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_user, to_email, text)
            server.quit()
            
            print(f"Email sent successfully to {to_email}")
            
        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
    
    def send_admin_notification(self, order_data: Dict[str, Any]) -> None:
        """
        Send notification email to admin about new order
        
        Args:
            order_data: Order information dictionary
        """
        subject = f"New Book Order - {order_data['book_title']}"
        
        body = f"""
New book order received:

Order ID: {order_data['order_id']}
Customer: {order_data['customer_name']} ({order_data['customer_email']})
Book Title: {order_data['book_title']}
Pages: {order_data['num_pages']}
Age Group: {order_data['age_group']}
Language: {order_data['language']}

Story Idea:
{order_data['story_idea']}

Characters: {len(order_data['characters'])} characters defined

Order Date: {order_data['order_date']}
Status: Cover generated, awaiting payment

Please review the order details in the system.
        """
        
        self._send_email(self.admin_email, subject, body)
    
    def send_customer_confirmation(self, order_data: Dict[str, Any]) -> None:
        """
        Send payment confirmation email to customer
        
        Args:
            order_data: Order information dictionary
        """
        subject = f"Payment Confirmed - Your Book '{order_data['book_title']}' is in Production!"
        
        body = f"""
Dear {order_data['customer_name']},

Thank you for your payment! We're excited to create your personalized children's book.

Order Details:
- Book Title: {order_data['book_title']}
- Order ID: {order_data['order_id']}
- Pages: {order_data['num_pages']}
- Age Group: {order_data['age_group']}

What happens next:
✅ Payment confirmed
✅ Our expert writers and illustrators are now reviewing your story
📚 Your complete book will be professionally crafted
📧 You'll receive your finished book via email within 12 hours

Our team of children's book experts will carefully review and enhance your story to ensure it's perfectly tailored for your target age group, with engaging illustrations and age-appropriate language.

If you have any questions, please don't hesitate to contact us.

Thank you for choosing our service!

Best regards,
The Children's Book Team
        """
        
        self._send_email(order_data['customer_email'], subject, body)
    
    def send_production_notification(self, order_data: Dict[str, Any]) -> None:
        """
        Send production notification to admin
        
        Args:
            order_data: Order information dictionary
        """
        subject = f"PRODUCTION NEEDED - {order_data['book_title']} (Order: {order_data['order_id']})"
        
        body = f"""
URGENT: Book production needed

Order ID: {order_data['order_id']}
Customer: {order_data['customer_name']} ({order_data['customer_email']})
Book Title: {order_data['book_title']}
Payment Status: PAID
Payment Date: {order_data['payment_date']}

DEADLINE: Book must be delivered within 12 hours of payment

Book Specifications:
- Pages: {order_data['num_pages']}
- Age Group: {order_data['age_group']}
- Language: {order_data['language']}
- Art Style: {order_data['art_style']}

Story Idea:
{order_data['story_idea']}

Characters: {len(order_data['characters'])} characters defined

Please begin production immediately and deliver the completed book to the customer within 12 hours.

Order file location: output/orders/order_{order_data['order_id']}.json
        """
        
        self._send_email(self.admin_email, subject, body) 