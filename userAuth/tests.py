from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from userAuth.tokens import account_activation_token, custom_password_reset_token

User = get_user_model()


class AuthTests(TestCase):
    def setUp(self):
        """Vorbereitung für die Tests"""
        self.client = APIClient()
        self.user_email = "testuser@example.com"
        self.user_password = "Testpasswort123"
        
        # Benutzer erstellen (noch nicht aktiviert)
        self.user = User.objects.create_user(
            email=self.user_email,
            username="testuser",
            password=self.user_password
        )
        self.user.is_active = False
        self.user.save()

    def test_login_with_inactive_user(self):
        """Testet, dass sich ein inaktiver Benutzer nicht einloggen kann"""
        data = {"email": self.user_email, "password": self.user_password}
        response = self.client.post("/api/auth/login/", data)

        self.assertEqual(response.status_code, 400)
        self.assertIn("E-Mail ist nicht aktiviert", response.json().get("email", [""])[0])


    def test_registration(self):
        """Testet die Benutzerregistrierung"""
        data = {
            "email": "newuser@example.com",
            "password1": "NeuesPasswort123",
            "password2": "NeuesPasswort123"
        }
        response = self.client.post("/api/auth/register/", data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Überprüfe deine E-Mail", response.json()["message"])

    def test_activation(self):
        """Testet die Aktivierung des Benutzerkontos"""
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_activation_token.make_token(self.user)

        response = self.client.get(f"/api/auth/activate/{uidb64}/{token}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Dein Konto wurde erfolgreich aktiviert!")

        # Benutzer sollte jetzt aktiv sein
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_password_reset(self):
        """Testet das Senden der Passwort-Zurücksetzen-E-Mail"""
        data = {"email": self.user_email}
        response = self.client.post("/api/auth/password-reset/", data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Falls die E-Mail existiert", response.json()["message"])

    def test_password_reset_confirm(self):
        """Testet das Zurücksetzen des Passworts mit Token"""
        self.user.is_active = True
        self.user.save()
        
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = custom_password_reset_token.make_token(self.user)

        new_password_data = {
            "password1": "NeuesSicheresPasswort123",
            "password2": "NeuesSicheresPasswort123"
        }
        response = self.client.post(f"/api/auth/password-reset/confirm/{uidb64}/{token}/", new_password_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Dein Passwort wurde erfolgreich geändert!")
        
        login_data = {"email": self.user_email, "password": "NeuesSicheresPasswort123"}
        login_response = self.client.post("/api/auth/login/", login_data)

        print("DEBUG LOGIN RESPONSE:", login_response.status_code, login_response.json())  

        self.assertEqual(login_response.status_code, 200)


    def test_login(self):
        """Testet das Login mit Access- und Refresh-Token"""
        # Benutzer aktivieren, um sich anmelden zu können
        self.user.is_active = True
        self.user.save()

        data = {"email": self.user_email, "password": self.user_password}
        response = self.client.post("/api/auth/login/", data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_logout(self):
        """Testet das Logout mit Refresh-Token"""
        # Benutzer aktivieren und anmelden
        self.user.is_active = True
        self.user.save()

        login_data = {"email": self.user_email, "password": self.user_password}
        login_response = self.client.post("/api/auth/login/", login_data)
        refresh_token = login_response.json().get("refresh")

        logout_response = self.client.post("/api/auth/logout/", {"refresh": refresh_token})
        self.assertEqual(logout_response.status_code, 200)
        self.assertEqual(logout_response.json()["message"], "Erfolgreich ausgeloggt.")
