from django.urls import path

from .views import (
    CheckUserExistsAPIView,
    ConsentRecordListCreateAPIView,
    ConsentRecordRetrieveUpdateDeleteAPIView,
    LoginAPIView,
    LogoutAPIView,
    OTPRequestAPIView,
    OTPVerifyAPIView,
    RegisterAPIView,
    RegistrationApplicationDecisionAPIView,
    RegistrationApplicationListCreateAPIView,
    RegistrationApplicationRetrieveUpdateDeleteAPIView,
    UserTblListCreateAPIView,
    UserTblRetrieveUpdateDeleteAPIView,
)

app_name = "accounts"

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("check-user/", CheckUserExistsAPIView.as_view(), name="check-user"),
    path("otp-request/", OTPRequestAPIView.as_view(), name="otp-request"),
    path("otp-verify/", OTPVerifyAPIView.as_view(), name="otp-verify"),
    path("users/", UserTblListCreateAPIView.as_view(), name="users-list-create"),
    path("users/<int:pk>/", UserTblRetrieveUpdateDeleteAPIView.as_view(), name="users-detail"),
    path("registration-applications/", RegistrationApplicationListCreateAPIView.as_view(), name="registration-applications-list-create"),
    path("registration-applications/<int:pk>/", RegistrationApplicationRetrieveUpdateDeleteAPIView.as_view(), name="registration-applications-detail"),
    path("registration-applications/<int:pk>/decision/", RegistrationApplicationDecisionAPIView.as_view(), name="registration-applications-decision"),
    path("consent-records/", ConsentRecordListCreateAPIView.as_view(), name="consent-records-list-create"),
    path("consent-records/<int:pk>/", ConsentRecordRetrieveUpdateDeleteAPIView.as_view(), name="consent-records-detail"),
]
