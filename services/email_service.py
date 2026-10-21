import os
import smtplib

from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv(override=True)


EMAIL_ADDRESS = os.getenv(
    "EMAIL_ADDRESS"
)

EMAIL_APP_PASSWORD = os.getenv(
    "EMAIL_APP_PASSWORD"
)

def send_password_reset_otp(
    recipient_email,
    otp
):
    if (
        not EMAIL_ADDRESS
        or not EMAIL_APP_PASSWORD
    ):
        return {
            "success": False,
            "message":
                "Email service is not configured."
        }

    try:
        message = EmailMessage()

        message[
            "Subject"
        ] = "SONGlytics Password Reset"

        message[
            "From"
        ] = EMAIL_ADDRESS

        message[
            "To"
        ] = recipient_email

        message.set_content(
            f"""
SONGlytics Password Reset

Your verification code is:

{otp}

This code will expire in 5 minutes.

If you did not request a password reset,
you can ignore this email.
"""
        )

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as smtp:

            smtp.login(
                EMAIL_ADDRESS,
                EMAIL_APP_PASSWORD
            )

            smtp.send_message(
                message
            )

        return {
            "success": True,
            "message":
                "Verification code sent."
        }

    except Exception as e:
        print(
            "Email OTP error:",
            e
        )

        return {
            "success": False,
            "message":
                "Unable to send verification code."
        }