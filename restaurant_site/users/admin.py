from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'role_badge',
        'phone',
        'django_admin_access',
        'is_active',
    )
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'phone')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Profile', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (
            'Role and access',
            {
                'fields': ('role', 'is_staff'),
                'description': (
                    '<strong>Role on site</strong> defines the orders panel (/staff/orders/). '
                    '<strong>Staff status</strong> (access to Django-admin) is set automatically '
                    'for roles «Staff» and «Admin». '
                    '  Superuser always has full access regardless of role.'
                ),
            },
        ),
        (
            'Django permissions',
            {
                'classes': ('collapse',),
                'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions'),
            },
        ),
        ('Дати', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'password1', 'password2'),
            },
        ),
        ('Profile', {'fields': ('email', 'phone')}),
        ('Role and access', {'fields': ('role',)}),
    )

    @admin.display(description='Role')
    def role_badge(self, obj):
        colors = {
            User.ROLE_CUSTOMER: '#6c757d',
            User.ROLE_STAFF: '#0d6efd',
            User.ROLE_ADMIN: '#cda45e',
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background:{}; color:#fff; padding:2px 8px; border-radius:4px; font-size:12px;">{}</span>',
            color,
            obj.get_role_display(),
        )

    @admin.display(description='Django-admin', boolean=True)
    def django_admin_access(self, obj):
        return obj.is_staff or obj.is_superuser

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if obj is not None:
            readonly.append('is_staff')
        return readonly

    def save_model(self, request, obj, form, change):
        obj.sync_staff_flag_from_role()
        super().save_model(request, obj, form, change)
