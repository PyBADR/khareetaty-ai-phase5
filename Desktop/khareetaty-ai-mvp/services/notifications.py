from twilio.rest import Client
import os

def send_whatsapp(phone, message):
    """
    Send WhatsApp message using Twilio
    Requires environment variables:
    - TWILIO_SID: Twilio Account SID
    - TWILIO_TOKEN: Twilio Auth Token
    - WHATSAPP_SENDER: WhatsApp sender number (e.g. whatsapp:+14155238886)
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    wa_sender = os.getenv("TWILIO_WHATSAPP_NUMBER")
    
    if not all([account_sid, auth_token, wa_sender]):
        print("Twilio credentials not set. Skipping WhatsApp message.")
        print(f"[TEST MODE] Would send to {phone}: {message}")
        return
    
    client = Client(account_sid, auth_token)

    try:
        message_response = client.messages.create(
            from_=wa_sender,
            body=message,
            to=f"whatsapp:{phone}"
        )
        print(f"[ALERT SENT] ID: {message_response.sid}, To: {phone}, Message: {message}")
        return message_response.sid
    except Exception as e:
        print(f"[ALERT FAILED] Error sending to {phone}: {e}")
        raise


def send_sms(phone, message):
    """
    Send SMS using Twilio
    Requires environment variables:
    - TWILIO_SID: Twilio Account SID
    - TWILIO_TOKEN: Twilio Auth Token
    - SMS_SENDER: SMS sender number
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    sms_sender = os.getenv("SMS_SENDER")
    
    if not all([account_sid, auth_token, sms_sender]):
        print("Twilio credentials not set. Skipping SMS message.")
        print(f"[TEST MODE] Would send to {phone}: {message}")
        return
    
    client = Client(account_sid, auth_token)

    try:
        message_response = client.messages.create(
            from_=sms_sender,
            body=message,
            to=phone
        )
        print(f"[SMS SENT] ID: {message_response.sid}, To: {phone}, Message: {message}")
        return message_response.sid
    except Exception as e:
        print(f"[SMS FAILED] Error sending to {phone}: {e}")
        raise


def send_email(to_emails, subject, body):
    """
    Send email using SMTP
    Requires environment variables:
    - SMTP_SERVER: SMTP server address
    - SMTP_PORT: SMTP port
    - SMTP_USER: SMTP username
    - SMTP_PASSWORD: SMTP password
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    smtp_server = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not all([smtp_server, smtp_user, smtp_password]):
        print("SMTP credentials not set. Skipping email.")
        print(f"[TEST MODE] Would send to {to_emails}: {subject}")
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = ", ".join(to_emails) if isinstance(to_emails, list) else to_emails
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        
        text = msg.as_string()
        server.sendmail(smtp_user, to_emails if isinstance(to_emails, list) else [to_emails], text)
        server.quit()
        
        print(f"[EMAIL SENT] To: {to_emails}, Subject: {subject}")
    except Exception as e:
        print(f"[EMAIL FAILED] Error sending to {to_emails}: {e}")
        raise