import smtplib
from email.mime.text import MIMEText

sender = "thotavenkatahemanth@gmail.com"
app_password = "unke icnv fglw qgnj"
receiver = "thotavenkatahemanth@gmail.com"

msg = MIMEText("This is a test email")
msg["Subject"] = "Test Email"
msg["From"] = sender
msg["To"] = receiver

try:
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.login(sender, app_password)
        server.send_message(msg)
    print("Email sent successfully")
except Exception as e:
    print("Failed to send email:")
    print(e)
