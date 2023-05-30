import re
import threading

from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.template.loader import render_to_string
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ausers.models import VIA_EMAIL, VIA_PHONE

email_regex = re.compile(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+")
phone_regex = re.compile(r'^\+?\d{1,3}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$')


def check_email_or_phone(email_or_phone):
    if re.fullmatch(email_regex, email_or_phone):
        return VIA_EMAIL
    elif re.fullmatch(phone_regex, email_or_phone):
        return VIA_PHONE
    else:
        raise serializers.ValidationError("Invalid input format")


def validate_email_or_phone(email_or_phone):
    if '@' in email_or_phone:  # Check if the value contains '@', indicating an email
        try:
            validate_email(email_or_phone)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format")
    else:  # Assume it's a phone number and perform phone number validation logic
        # Add your phone number validation logic here
        pass

    return email_or_phone


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Email:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data["subject"],
            body=data["body"],
            to=[data["to_email"]]
        )
        if data.get("content_type") == "html":
            email.content_subtype = "html"

        EmailThread(email).start()


def send_message_to_email(email, code):
    html_content = render_to_string(
        template_name="email/authentication/activate_account.html",
        context={"code": code}
    )

    Email.send_email(data={
        "subject": "Sign Up",
        "body": html_content,
        "to_email": email,
        "content_type": "html"
    })
