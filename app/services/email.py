import resend
from app.core.config import settings

def send_verification_email(email_to: str, code: str):
    # Print for debugging/dev
    print(f"--- EMAIL SIMULATION ---")
    print(f"To: {email_to}")
    print(f"Subject: Your Unibook Verification Code")
    print(f"Code: {code}")
    print(f"------------------------")

    if not settings.RESEND_API_KEY:
        print("RESEND_API_KEY not set. Skipping real email send.")
        return

    resend.api_key = settings.RESEND_API_KEY

    html_content = f"""
    <p>Your verification code is: <strong>{code}</strong></p>
    <p>This code expires in 5 minutes.</p>
    """

    try:
        r = resend.Emails.send({
            "from": settings.RESEND_FROM_EMAIL,
            "to": email_to,
            "subject": "Unibook Verification Code",
            "html": html_content
        })
        print(f"Real email sent to {email_to} via Resend. ID: {r.get('id')}")
    except Exception as e:
        print(f"Failed to send real email via Resend: {e}")
