import smtplib
from email.message import EmailMessage

class EmailManager:
    def __init__(self):
        from custom_modules.env_module import get_pwrd, get_email
        self.email = get_email()
        self.pwrd = get_pwrd()

    def send_confirmation(self, to_email:str) -> int:
        import random
        code = f"{random.randint(0,9)}{random.randint(0,9)}{random.randint(0,9)}{random.randint(0,9)}{random.randint(0,9)}{random.randint(0,9)}"

        subject = "Ace Incorp' Email Verification"
        body = f"""
Hello,

Your verification code is: {code}

Please enter this code in the system to continue.

If you did not request this code, please ignore this email.

Kind regards,  
AceInc Security Team
""".strip()
        clean_body = '\n'.join(line.strip() for line in body.strip().splitlines())
        self.__send_email(subject, clean_body, to_email)
        return int(code)



    def __send_email(self, subject:str, body:str, to_email:str):
        # Create the email message
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = self.email
        msg['To'] = to_email
        # Connect to Gmail SMTP and send the email
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(self.email, self.pwrd)
                smtp.send_message(msg)
            print("Email sent successfully.")
        except Exception as e:
            print("Failed to send email:", e)