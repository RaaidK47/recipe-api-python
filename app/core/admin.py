"""
Django Admin customization
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _  # To translate strings in Django Admin

from core import models  # To import custom models that we want to register with Django Admin

# Adding functionality to UserAdmin Class
class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users"""
    ordering = ['id']
    list_display = ['email', 'name', 'password','last_login']

    # adding field for Change User page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    # ^fieldsets contain tuple of tuples
    # ^First tuple is the title of the fieldset
    # ^Second tuple is the fields to be displayed in the fieldset
    # ^Third tuple is the options for the fieldset
    # we've basically customized the field sets variable and we've only specified fields that we created in our models. (or that were integrated with PermissionMixin)
    # we've also customized the ordering of the fields in the fieldsets.

    readonly_fields = ['last_login']

    # adding fields for Add User page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),  # We can assign custom CSS Classes to Django Admin (To make Admin Page more neater)
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )

# Making Models manageable through Django Admin Interface
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)
