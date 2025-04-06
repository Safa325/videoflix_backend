from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from .tokens import account_activation_token, custom_password_reset_token
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def send_activation_email(user_id):
    user = User.objects.get(pk=user_id)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    activation_link = f"https://app.videoflix.shamarisafa.ch/activate/{uidb64}/{account_activation_token.make_token(user)}"
  
    mail_subject = 'Aktiviere deinen Account'
    html_content = render_to_string('activation_email.html', {
        'user': user,
        'activation_link': activation_link,
    })
    msg = EmailMessage(mail_subject, html_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.content_subtype = "html"
    msg.send()

def send_password_reset_email(user_id):
    user = User.objects.get(pk=user_id)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    reset_link = f"https://app.videoflix.shamarisafa.ch/set-password/{uidb64}/{custom_password_reset_token.make_token(user)}"
    
    mail_subject = 'Videoflix - Passwort zurücksetzen'
    html_content = render_to_string('set_password_email.html', {
        'user': user,
        'reset_link': reset_link,
    })
    msg = EmailMessage(mail_subject, html_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.content_subtype = "html"
    msg.send()
    