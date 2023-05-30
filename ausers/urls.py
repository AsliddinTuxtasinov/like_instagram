from django.urls import path
from . import views


urlpatterns = [
    # URL pattern for the sign-up api
    path("sign-up/", views.SignUpViews.as_view(), name="sign-up-new")
]
