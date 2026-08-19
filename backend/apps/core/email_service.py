from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


def send_login_success_email(user):
    if not user.email:
        return

    now = timezone.localtime()

    subject = "Login Successful — Smart Air Monitor System"

    message = f"""
Hello {user.full_name},

Your account has been successfully logged in to the Smart Air Monitor System.

Login Details
-------------------------
Username: {user.username}
Date: {now.strftime("%d %B %Y")}
Time: {now.strftime("%I:%M %p")}

Your login was successful.

Smart Air Monitor System
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def send_alert_email(user, station, alert):
    if not user.email:
        return

    now = timezone.localtime()

    subject = (
        f"🚨 {alert.parameter} Alert — "
        f"{station.name}"
    )

    message = f"""
Hello {user.full_name},

Smart Air Monitor System has detected an environmental alert.

SITE
-------------------------
Site: {station.name}

ALERT DETAILS
-------------------------
Parameter: {alert.parameter}
Severity: {alert.severity}
Message: {alert.message}

Recommendation:
{alert.recommendation or "Please check the environmental conditions."}

TIME
-------------------------
Date: {now.strftime("%d %B %Y")}
Time: {now.strftime("%I:%M %p")}

Please check the Smart Air Monitor dashboard for the latest readings.

Smart Air Monitor System
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )