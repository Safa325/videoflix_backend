from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, ResetPasswordSerializer, ConfirmSerializer, LoginSerializer
from django.contrib.auth import get_user_model
from .tasks import send_activation_email, send_password_reset_email
from django.utils.http import urlsafe_base64_decode
from .tokens import account_activation_token, custom_password_reset_token 
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_activation_email(user.pk) 
            return Response({'message': 'Überprüfe deine E-Mail, um dein Konto zu aktivieren.'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            if account_activation_token.check_token(user, token):
                user.is_active = True  
                user.save()
                return JsonResponse({"message": "Dein Konto wurde erfolgreich aktiviert!"}, status=200)
            else:
                return JsonResponse({"error": "Ungültiger oder abgelaufener Aktivierungslink!"}, status=400)
        except (User.DoesNotExist, ValueError, TypeError) as e:
            return JsonResponse({"error": "Ungültiger Aktivierungslink!"}, status=400)
        
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.get_user()  
            send_password_reset_email(user.id)
            return Response({"message": "Falls die E-Mail existiert, wurde ein Link zum Zurücksetzen des Passworts gesendet."}, status=200)

        return Response(serializer.errors, status=400)
    
class ConfirmNewPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            if not custom_password_reset_token.check_token(user, token):
                return JsonResponse({"error": "Ungültiger oder abgelaufener Aktivierungslink!"}, status=400)
            serializer = ConfirmSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user)  
                return JsonResponse({"message": "Dein Passwort wurde erfolgreich geändert!"}, status=200)
            return JsonResponse(serializer.errors, status=400)
        
        except (User.DoesNotExist, ValueError, TypeError):
            return JsonResponse({"error": "Ungültiger Aktivierungslink!"}, status=400)
        
class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Kein Token gefunden."}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Erfolgreich ausgeloggt."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class TokenVerifyView(APIView):
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        return Response({
            "message": "✅ Token ist gültig",
            "user": {
                "id": request.user.id,
                "email": request.user.email,
                "username": request.user.username
            }
        }, status=200)
