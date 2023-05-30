import random
import uuid
from datetime import datetime, timedelta

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

from shared.models import BaseModel

ORDINARY_USER, MANAGER, ADMIN = ("ordinary_user", "manager", "admin")
VIA_EMAIL, VIA_PHONE = ("via_email", "via_phone")
NEW, CODE_VERIFIED, DONE, PHOTO_STEP = ("new", "code_verified", "done", "photo_step")


class User(AbstractUser, BaseModel):
    USER_ROLES_CHOICES = (
        (ORDINARY_USER, ORDINARY_USER),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN)
    )

    AUTH_TYPE_CHOICES = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )

    AUTH_STATUS_CHOICES = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHOTO_STEP, PHOTO_STEP)
    )

    user_roles = models.CharField(max_length=35, choices=USER_ROLES_CHOICES, default=ORDINARY_USER)
    auth_type = models.CharField(max_length=35, choices=AUTH_TYPE_CHOICES)
    auth_status = models.CharField(max_length=35, choices=AUTH_STATUS_CHOICES, default=NEW)

    email = models.EmailField(null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True, unique=True)
    profile_photo = models.ImageField(upload_to="user_photos/", blank=True, null=True, validators=[
        FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])
    ])

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def create_verify_code(self, verify_type):
        code = "".join([str(random.randint(0, 100) % 10) for _ in range(4)])
        UserConfirmation.objects.create(user_id=self.id, code=code, verify_type=verify_type)
        return code

    def check_username(self):
        if not self.username:
            temp_username = f"instagram-{uuid.uuid4().__str__().split('-')[-1]}"
            while User.objects.filter(username=temp_username):
                temp_username = f"{temp_username}{random.randint(0, 9)}"

            self.username = temp_username

    def check_email(self):
        if not self.email:
            normalize_email = str(self.email).lower()  # Asliddin@gmail.com -> asliddin@gmail.com
            self.email = normalize_email

    def check_pass(self):
        if not self.password:
            temp_password = f"password-{uuid.uuid4().__str__().split('-')[-1]}"
            self.password = temp_password

    def hashing_password(self):
        if not self.password.startswith("pbkdf2_sha256"):
            self.set_password(self.password)

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access": str(refresh.access_token),
            "refresh_token": str(refresh)
        }

    def clean(self):
        self.check_username()
        self.check_email()
        self.check_pass()
        self.hashing_password()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


PHONE_EXPIRE = 2
EMAIL_EXPIRE = 5


class UserConfirmation(BaseModel):
    AUTH_TYPE_CHOICES = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )

    code = models.CharField(max_length=4)
    verify_type = models.CharField(max_length=35, choices=AUTH_TYPE_CHOICES)
    user = models.ForeignKey('ausers.User', on_delete=models.CASCADE, related_name="verify_odes")
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())

    def save(self, *args, **kwargs):
        # if not self.pk:
        if self.verify_type == VIA_EMAIL:
            expiration_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRE)
        else:
            expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPIRE)
        self.expiration_time = expiration_time

        super().save(*args, **kwargs)
