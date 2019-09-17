from django.contrib import admin
from django.contrib.auth import admin as auth_admin

from {{ cookiecutter.project_slug }}.users.forms import UserChangeForm, UserCreationForm
from {{ cookiecutter.project_slug }}.users.models import User


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (('User', {'fields': ('name',)}),) + auth_admin.UserAdmin.fieldsets
    list_display = ['username', 'name', 'is_superuser']
    search_fields = ['name']
