from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active))

account_activation_token = AccountActivationTokenGenerator()

class CustomPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    """Erstellt einen sicheren Token für das Zurücksetzen des Passworts"""
    def _make_hash_value(self, user, timestamp):
        return six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.last_login)

custom_password_reset_token = CustomPasswordResetTokenGenerator()