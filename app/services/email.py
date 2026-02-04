import resend
from app.core.config import settings

def send_verification_email(email_to: str, code: str):
    # Print for debugging/dev
    if not settings.RESEND_API_KEY:
        print("RESEND_API_KEY not set. Skipping real email send.")
        return

    resend.api_key = settings.RESEND_API_KEY
    html_content = f"""
    <p>您的验证码是：<strong>{code}</strong></p>
    <p>Your verification code is: <strong>{code}</strong></p>
    <p>此验证码5分钟后过期。</p>
    <p>This code expires in 5 minutes.</p>
    """

    try:
        r = resend.Emails.send({
            "from": settings.RESEND_FROM_EMAIL,
            "to": email_to,
            "subject": "[Unibook]由你注册验证码",
            "html": html_content
        })
        print(f"Real email sent to {email_to} via Resend. ID: {r.get('id')}")
    except Exception as e:
        print(f"Failed to send real email via Resend: {e}")

