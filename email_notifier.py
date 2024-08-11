import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging

# --- EMAIL NOTIFICATION SETUP ---
EMAIL_ADDRESS = 'botshelomokoka@gmail.com'  
EMAIL_PASSWORD = 'pqss' 
RECIPIENT_EMAIL = 'botshelomokoka@gmail.com'  

def send_email(subject, body, attachment_path=None):
    # ... (same as before)

# --- LOGGING ---
class EmailHandler(logging.Handler):
    # ... (same as before)
