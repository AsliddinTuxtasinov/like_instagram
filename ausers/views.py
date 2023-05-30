from rest_framework import generics, permissions

from .models import User
from .serializers import SignUpSerializers


# Class-based view for handling sign-up requests
class SignUpViews(generics.CreateAPIView):
    # Queryset for the view, which fetches all User objects from the database
    queryset = User.objects.all()
    # Serializer class used for validating and serializing input data
    serializer_class = SignUpSerializers
    # List of permission classes applied to the view
    permission_classes = [permissions.AllowAny]
