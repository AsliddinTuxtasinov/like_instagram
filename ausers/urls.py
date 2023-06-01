from django.urls import path
from . import views


urlpatterns = [
    # URL pattern for the sign-up api
    path("signup/", views.SignUpViews.as_view(), name="sign-up-new"),
    path("verify/", views.VerifyAPIViews.as_view(), name="verify-sign-up-code")
]
