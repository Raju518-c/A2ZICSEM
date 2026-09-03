from django.conf import settings
from django.core.mail import send_mail


def send_tenant_registration_invitation_email(
    email,
    subject,
    message,
):
    """
    Send tenant registration invitation email.
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    return True