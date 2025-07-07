"""
Email Service
Handles email notifications for orders and payments
"""

import os
import json
import smtplib
import tempfile
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any

from .storage_service import CloudStorageService

class EmailService:
    """Service for handling email notifications"""
    
    def __init__(self):
        """Initialize email configuration"""
        self.admin_email = os.getenv('ADMIN_EMAIL', 'admin@yourbookcompany.com')
        self.production_email = os.getenv('PRODUCTION_EMAIL', self.admin_email)  # For production notifications
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        
        # Initialize Cloud Storage service
        self.storage_service = CloudStorageService()
    
    def _send_email(self, to_email: str, subject: str, body: str, attachments: list = None) -> None:
        """
        Send email using SMTP with optional attachments
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body text
            attachments: List of file paths to attach
        """
        try:
            if not self.email_user or not self.email_password:
                print("Email credentials not configured, skipping email")
                return
            
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if Path(file_path).exists():
                        try:
                            with open(file_path, "rb") as attachment:
                                part = MIMEBase('application', 'octet-stream')
                                part.set_payload(attachment.read())
                            
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {Path(file_path).name}',
                            )
                            msg.attach(part)
                            print(f"Attached file: {file_path}")
                        except Exception as e:
                            print(f"Failed to attach file {file_path}: {str(e)}")
                    else:
                        print(f"Attachment file not found: {file_path}")
            
            # Send email
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

Order data is stored in Cloud Storage and will be sent as email attachments.
        """
        
        self._send_email(self.production_email, subject, body)
    
    def send_complete_order_information(self, order_data: Dict[str, Any]) -> None:
        """
        Send complete order information with all attachments to production email
        This includes user form data as JSON, generated cover, and character descriptions
        
        Args:
            order_data: Complete order information dictionary
        """
        subject = f"COMPLETE ORDER INFO - {order_data['book_title']} (Order: {order_data['order_id']})"
        
        # Create detailed body with all order information
        body = f"""
COMPLETE ORDER INFORMATION FOR BOOK PRODUCTION

=== CUSTOMER INFORMATION ===
Name: {order_data.get('customer_name', 'N/A')}
Email: {order_data.get('customer_email', 'N/A')}
Order ID: {order_data.get('order_id', 'N/A')}
Payment Date: {order_data.get('payment_date', 'N/A')}

=== BOOK SPECIFICATIONS ===
Title: {order_data.get('book_title', 'N/A')}
Number of Pages: {order_data.get('num_pages', 'N/A')}
Age Group: {order_data.get('age_group', 'N/A')}
Language: {order_data.get('language', 'N/A')}
Art Style: {order_data.get('art_style', 'N/A')}

=== STORY CONCEPT ===
{order_data.get('story_idea', 'N/A')}

=== THEMES ===
{', '.join(order_data.get('themes', [])) if order_data.get('themes') else 'None specified'}

=== CHARACTERS ===
Number of characters: {len(order_data.get('characters', []))}
"""
        
        # Add character details to body
        for i, char in enumerate(order_data.get('characters', []), 1):
            body += f"""
Character {i}:
- Name: {char.get('name', 'N/A')}
- Type: {char.get('character_type', 'N/A')}
- Input Method: {char.get('type', 'N/A')}
- Description/Content: {char.get('content', 'N/A')}
"""
        
        body += f"""

=== ATTACHMENTS INCLUDED ===
1. order_data.json - Complete form data in JSON format
2. cover_image.png - Generated book cover
3. character_descriptions.json - Detailed character descriptions (if available)

=== DELIVERY DEADLINE ===
Book must be completed and delivered within 12 hours of this email.

=== ORDER COMPLETION CHECKLIST ===
□ Review all customer requirements above
□ Create story content based on specifications
□ Generate all page illustrations
□ Ensure age-appropriate content for {order_data.get('age_group', 'specified age group')}
□ Format as PDF
□ Deliver to customer: {order_data.get('customer_email', 'customer email')}

Please confirm receipt of this email and begin production immediately.
        """
        
        # Prepare attachments (download from Cloud Storage to temporary files)
        attachments = []
        temp_files = []  # Keep track of temp files to clean up
        order_id = order_data.get('order_id', 'unknown')
        
        try:
            # 1. Create complete order data as temporary JSON file
            temp_json = tempfile.NamedTemporaryFile(mode='w', suffix=f'_complete_order_{order_id}.json', delete=False)
            json.dump(order_data, temp_json, indent=2, ensure_ascii=False)
            temp_json.close()
            attachments.append(temp_json.name)
            temp_files.append(temp_json.name)
            print(f"Created temporary order JSON: {temp_json.name}")
            
            # 2. Download and attach the generated cover image from Cloud Storage
            cover_cloud_path = f"covers/cover_{order_id}.png"
            if self.storage_service.file_exists(cover_cloud_path):
                temp_cover = self.storage_service.download_file_to_temp(cover_cloud_path)
                # Rename temp file to have proper extension
                cover_temp = tempfile.NamedTemporaryFile(suffix=f'_cover_{order_id}.png', delete=False)
                cover_temp.close()
                # Copy content to new temp file with proper name
                import shutil
                shutil.copy2(temp_cover, cover_temp.name)
                attachments.append(cover_temp.name)
                temp_files.extend([temp_cover, cover_temp.name])
                print(f"Downloaded cover image from Cloud Storage: {cover_cloud_path}")
            else:
                print(f"Cover image not found in Cloud Storage: {cover_cloud_path}")
            
            # 3. Download and attach character descriptions from Cloud Storage
            character_descriptions = []
            for char in order_data.get('characters', []):
                char_name = char.get('name', '').lower().replace(' ', '_')
                if char_name:
                    # Clean character name to match Cloud Storage path format
                    clean_name = "".join(c for c in char_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    clean_name = clean_name.replace(' ', '_').lower()
                    char_cloud_path = f"characters/{clean_name}.json"
                    
                    if self.storage_service.file_exists(char_cloud_path):
                        try:
                            char_data = self.storage_service.download_json(char_cloud_path)
                            character_descriptions.append(char_data)
                            
                            # Create temporary file for this character
                            temp_char = tempfile.NamedTemporaryFile(
                                mode='w', 
                                suffix=f'_character_{clean_name}.json', 
                                delete=False
                            )
                            json.dump(char_data, temp_char, indent=2, ensure_ascii=False)
                            temp_char.close()
                            attachments.append(temp_char.name)
                            temp_files.append(temp_char.name)
                            print(f"Downloaded character description: {char_cloud_path}")
                        except Exception as e:
                            print(f"Failed to download character description for {char_name}: {str(e)}")
            
            # If we have character descriptions, create a combined temporary file
            if character_descriptions:
                try:
                    temp_combined = tempfile.NamedTemporaryFile(
                        mode='w',
                        suffix=f'_all_characters_{order_id}.json',
                        delete=False
                    )
                    json.dump(character_descriptions, temp_combined, indent=2, ensure_ascii=False)
                    temp_combined.close()
                    attachments.append(temp_combined.name)
                    temp_files.append(temp_combined.name)
                    print(f"Created combined character descriptions file")
                except Exception as e:
                    print(f"Failed to create combined character descriptions file: {str(e)}")
            
            # Send email with attachments
            self._send_email(self.production_email, subject, body, attachments)
            
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    Path(temp_file).unlink(missing_ok=True)
                except Exception as e:
                    print(f"Failed to clean up temporary file {temp_file}: {str(e)}")
        
        print(f"Complete order information sent for order {order_id} with {len(attachments)} attachments") 