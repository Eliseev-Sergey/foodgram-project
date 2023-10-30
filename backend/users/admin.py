from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """ Интерфейс админ-зоны с необходимыми полями модели пользователей."""
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': (
    #             'email',
    #             'password1',
    #             'password2',
    #             'is_staff',
    #             'is_active')
    #         }),
    # )
    search_fields = ('email', 'username',)
    list_filter = ('email', 'username',)

    ordering = ('email',)
