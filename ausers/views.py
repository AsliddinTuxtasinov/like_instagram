import datetime

from rest_framework import generics, permissions, views, exceptions, response, status

from .models import User, CODE_VERIFIED, NEW
from .serializers import SignUpSerializers


# Class-based view for handling sign-up requests
class SignUpViews(generics.CreateAPIView):
    # Queryset for the view, which fetches all User objects from the database
    queryset = User.objects.all()
    # Serializer class used for validating and serializing input data
    serializer_class = SignUpSerializers
    # List of permission classes applied to the view
    permission_classes = [permissions.AllowAny]


class VerifyAPIViews(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        code = request.data.get("code")

        self.check_verify(user, code)
        return response.Response(data={
            "success": True,
            "auth_status": user.auth_status,
            "tokens": user.token()
        }, status=status.HTTP_200_OK)

    @staticmethod
    def check_verify(user, code):
        if code:
            verify_code = user.verify_codes.filter(
                expiration_time__gt=datetime.datetime.now(),
                code=code,
                is_confirmed=False
            ).first()

            if verify_code:
                verify_code.is_confirmed = True
                verify_code.save()

                if user.auth_status == NEW:
                    user.auth_status = CODE_VERIFIED
                    user.save()
                return True

        raise exceptions.ValidationError({
            "message": "Your verify code is wrong or old !"
        })
