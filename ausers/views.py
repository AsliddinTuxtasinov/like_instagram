from rest_framework import views, generics, permissions

from .models import User
from .serializers import SignUpSerializers


class SignUpViews(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializers
    permission_classes = [permissions.AllowAny]

