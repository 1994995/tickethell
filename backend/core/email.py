from typing import Literal
from fastapi_mail import (
    FastMail,
    MessageSchema,
    MessageType,
    ConnectionConfig
)
from fastapi import UploadFile
import os
from io import BytesIO

from dotenv import load_dotenv

load_dotenv()

_smtp_config = ConnectionConfig(
    MAIL_USERNAME=os.environ["SMTP_USER"],
    MAIL_PASSWORD=os.environ["SMTP_PASSWORD"],
    MAIL_FROM=os.environ["FROM_EMAIL"],
    MAIL_PORT=int(os.environ["SMTP_PORT"]),
    MAIL_SERVER=os.environ["SMTP_HOST"],
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

_ATTACHMENT_EXT = Literal["png", "pdf"]
_ATTACHMENT_HEADERS = {
    "content-type": None
}

async def send_ticket_email(to_email: str, qr_code: BytesIO, 
                      file_name: str, ext: _ATTACHMENT_EXT="png"):
    headers = _ATTACHMENT_HEADERS
    if ext == "png":
        headers.update({"content-type": "image/png"})
    elif ext == "pdf":
        headers.update({"content-type": "application/pdf"})
    # TODO: return error if bad ext was passed??
    
    name = f"{file_name}.{ext}"
    attachment = UploadFile(qr_code, filename=name, headers=headers)

    # DEBUG atm
    html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h1 style="color: #667eea;">QR Test!</h1>
            </body>
        </html>
    """
    html_test= f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h1 style="color: #667eea;">Matteo I did it</h1>
                <p>I got it working...it works...it was really easy</p>
                <p>People can even buy multiple tickets' at once and it automatically makes them into a pdf with each code</p>
                <p>we can do this for sure</p>
                <p>you should scan the attached QR code to make sure it's actually working</p>
                <p>Matt</p>
            </body>
        </html>
    """
    message = MessageSchema(
        subject="I Figured it out!",
        recipients=[to_email],
        body=html_test,
        subtype=MessageType.html,
        attachments=[attachment]
    )

    try:
        await FastMail(_smtp_config).send_message(message)
        return True
    except Exception:
        # TODO: Proper exception handling
        return False
