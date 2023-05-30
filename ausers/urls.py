from django.urls import path
from . import views


urlpatterns = [
    path("sign-up/", views.SignUpViews.as_view(), name="sign-up-new")
]
