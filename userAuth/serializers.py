from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError({"email": "Diese E-Mail ist nicht registriert."})

        if not user.is_active:
            raise serializers.ValidationError({"email": "E-Mail ist nicht aktiviert. Bitte bestätige dein Konto."})

        user = authenticate(username=user.username, password=password)

        if not user:
            raise serializers.ValidationError({"password": "Falsches Passwort."})

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username
            }
        }
     
       
class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password1 = attrs.get("password1")
        password2 = attrs.get("password2")

        # Prüfen, ob die E-Mail bereits existiert
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Diese E-Mail ist bereits registriert."})

        # Prüfen, ob die Passwörter übereinstimmen
        if password1 != password2:
            raise serializers.ValidationError({"password2": "Passwörter stimmen nicht überein!"})

        return attrs
    
    def generate_username(self, email):
        """Erstellt einen einzigartigen Benutzernamen basierend auf der E-Mail"""
        base_username = email.split("@")[0]
        username = base_username
        counter = 1

        # Falls der Benutzername bereits existiert, füge eine Zahl hinzu
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        return username

    def create(self, validated_data):
        """Erstellt einen Benutzer mit der E-Mail als Login"""
        email = validated_data["email"]
        password = validated_data["password1"]

        # Generiere einen einzigartigen Benutzernamen
        username = self.generate_username(email)

        # Benutzer erstellen
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password
        )
        user.is_active = False  # Falls du eine E-Mail-Bestätigung nutzen möchtest
        user.save()
        return user


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get("email")
        
        # Prüfen, ob die E-Mail existiert
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Es gibt keinen Benutzer mit dieser E-Mail-Adresse."})

        return attrs  
    
    def get_user(self):
        """Holt den Benutzer basierend auf der eingegebenen E-Mail"""
        email = self.validated_data.get("email")  
        user = User.objects.get(email=email)  
        return user

class ConfirmSerializer(serializers.Serializer):
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        password1 = attrs.get("password1")
        password2 = attrs.get("password2")

        if password1 != password2:
            raise serializers.ValidationError({"password2": "Passwörter stimmen nicht überein!"})

        validate_password(password1)

        return attrs

    def save(self, user):
        """Speichert das neue Passwort für den Benutzer"""
        user.set_password(self.validated_data["password1"])
        user.save()

