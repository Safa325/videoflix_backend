
from django.urls import path, include
from .views import RegisterView, ActivateAccountView, ResetPasswordView, ConfirmNewPasswordView, LoginView, LogoutView, TokenVerifyView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('register/',RegisterView.as_view(),name='registration') ,
    path('activate/<str:uidb64>/<str:token>/', ActivateAccountView.as_view(), name='activate-account'),
    path('password-reset/', ResetPasswordView.as_view(), name='reset-password'),
    path('password-reset/confirm/<str:uidb64>/<str:token>/', ConfirmNewPasswordView.as_view(), name='confirm-password'),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('token/verify/', TokenVerifyView.as_view(), name="check_auth"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
