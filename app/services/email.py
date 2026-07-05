import os
from email.message import EmailMessage
import aiosmtplib
from jinja2 import Environment, FileSystemLoader
from loguru import logger
from app.core.settings import settings

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "email")
os.makedirs(TEMPLATE_DIR, exist_ok=True)

jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

class EmailService:
    @staticmethod
    async def send_email(to_email: str, subject: str, template_name: str, context: dict):
        try:
            template = jinja_env.get_template(template_name)
            html_content = template.render(context)
            
            message = EmailMessage()
            message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
            message["To"] = to_email
            message["Subject"] = subject
            
            message.set_content(html_content, subtype="html")
            
            if settings.smtp_host:
                await aiosmtplib.send(
                    message,
                    hostname=settings.smtp_host,
                    port=settings.smtp_port,
                    username=settings.smtp_user,
                    password=settings.smtp_password,
                    use_tls=settings.smtp_use_tls,
                )
                logger.info(f"Email sent to {to_email}")
            else:
                logger.warning(f"SMTP not configured. Simulated sending to {to_email} with subject: {subject}")
                
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            raise
