import re
import threading

from decouple import config
from twilio.rest import Client

from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.template.loader import render_to_string
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ausers.models import VIA_EMAIL, VIA_PHONE

# Regular expression pattern for validating email addresses
email_regex = re.compile(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+")
# Regular expression pattern for validating phone numbers
phone_regex = re.compile(r'^\+?\d{1,3}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$')


# Function to check if a given input is a valid email address or phone number
def check_email_or_phone(email_or_phone):
    # Checking if the input matches the email_regex pattern
    if re.fullmatch(email_regex, email_or_phone):
        return VIA_EMAIL
    # Checking if the input matches the phone_regex pattern
    elif re.fullmatch(phone_regex, email_or_phone):
        return VIA_PHONE
    else:
        # If the input doesn't match either pattern, raising a validation error
        raise serializers.ValidationError("Invalid input format")


# def validate_email_or_phone(email_or_phone):
#     if '@' in email_or_phone:  # Check if the value contains '@', indicating an email
#         try:
#             validate_email(email_or_phone)
#         except ValidationError:
#             raise serializers.ValidationError("Invalid email format")
#     else:  # Assume it's a phone number and perform phone number validation logic
#         # Add your phone number validation logic here
#         pass
#
#     return email_or_phone


# Custom Thread class for sending emails asynchronously
class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Email:
    # Static method to send an email with the provided data
    @staticmethod
    def send_email(data):
        # Creating an EmailMessage object with the subject, body, and recipient(s) from the provided data
        email = EmailMessage(
            subject=data["subject"],
            body=data["body"],
            to=[data["to_email"]]
        )

        # Checking if the content type is set to "html"
        if data.get("content_type") == "html":
            # Setting the content_subtype to "html" for sending HTML-formatted emails
            email.content_subtype = "html"

        # Starting a new thread to send the email asynchronously
        EmailThread(email).start()


# Function to send a message to the provided email address
def send_message_to_email(email, code):
    # Rendering the HTML content for the email using a template and the provided code
    html_content = render_to_string(
        template_name="email/authentication/activate_account.html",
        context={"code": code}
    )

    # Sending the email by calling the send_email method of the Email class
    Email.send_email(data={
        "subject": "Sign Up",
        "body": html_content,
        "to_email": email,
        "content_type": "html"
    })


def send_phone_code(phone_number, code):
    account_sid = config("account_sid")
    auth_token = config("your_auth_token")

    client = Client(account_sid, auth_token)
    client.messages.create(
        to=phone_number,  # +12316851234,
        from_="+15555555555",  # from twilio
        body=f"Hello there!, Your verification code is: {code}"
    )
