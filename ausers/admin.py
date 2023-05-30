from django.contrib import admin

from .models import User, UserConfirmation


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "phone_number", "auth_type"]


@admin.register(UserConfirmation)
class UserConfirmationAdmin(admin.ModelAdmin):
    list_display = ["code", "verify_type", "is_confirmed"]
