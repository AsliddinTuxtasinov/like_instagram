from django.db.models import Q
from rest_framework import serializers, exceptions

from shared.utilty import check_email_or_phone, send_message_to_email
from .models import User, UserConfirmation, VIA_EMAIL, VIA_PHONE


class SignUpSerializers(serializers.ModelSerializer):
    email_or_phone = serializers.CharField(required=False)

    class Meta:
        model = User
        read_only_fields = ["id"]
        fields = ["id", "auth_type", "auth_status", "email_or_phone"]

        extra_kwargs = {
            "auth_type": {"read_only": True, "required": False},
            "auth_status": {"read_only": True, "required": False}
        }

    def create(self, validated_data):
        user = super().create(validated_data)

        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_message_to_email(email=user.email, code=code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            print("code: ", code)
            # send_phone_code(user.phone_number, code)
        user.save()
        return user

    def validate(self, attrs):
        super().validate(attrs)
        attrs = self.auth_validate(attrs)
        return attrs

    @staticmethod
    def auth_validate(attrs):
        user_input = str(attrs.get("email_or_phone")).lower()
        # check email or phone number
        auth_type = check_email_or_phone(email_or_phone=user_input)

        if auth_type == VIA_EMAIL:
            attrs = {
                "email": user_input,
                "auth_type": auth_type
            }
        elif auth_type == VIA_PHONE:
            attrs = {
                "phone_number": user_input,
                "auth_type": auth_type
            }
        return attrs

    @staticmethod
    def validate_email_or_phone(value):
        filter_query = Q(email=value) | Q(phone_number=value)
        if value and User.objects.filter(filter_query).exists():
            raise exceptions.ValidationError({
                "message": f"{value} is already exists !"
            })
        return value

    def to_representation(self, instance):
        context_data = super().to_representation(instance)
        context_data["tokens"]=instance.token()
        return context_data
