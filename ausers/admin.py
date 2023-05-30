from django.contrib import admin

from .models import User, UserConfirmation


# Registering the User model with the admin site
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # List of fields to display in the admin interface for User objects
    list_display = ["username", "email", "phone_number", "auth_type"]


# Registering the UserConfirmation model with the admin site
@admin.register(UserConfirmation)
class UserConfirmationAdmin(admin.ModelAdmin):
    # List of fields to display in the admin interface for UserConfirmation objects
    list_display = ["code", "verify_type", "is_confirmed"]
