from django.contrib import admin
from accounts.models import User
from .forms import AdminPanelUserCreationForm, AdminPanelUserChangeForm
# Register your models here.
from forum.models import Community, Post, Topic
from django.utils.html import format_html   
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from django.forms import ClearableFileInput

admin.site.register(Topic)
admin.site.register(Post)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    add_form = AdminPanelUserCreationForm
    form = AdminPanelUserChangeForm
    model = User
    list_display = ("email", "username", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "username", "first_name", "last_name", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "first_name", "last_name", "password1", "password2", "is_staff", "is_active"),
        }),
    )
    search_fields = ("email",)
    ordering = ("email",)


    @admin.action(description="Activate selected users")
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)


    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)

@admin.register(Community)
class CategoryAdmin(TreeAdmin):
    model = Community
    form = movenodeform_factory(Community )
    list_display = ("title", "slug", "description", "category_count", "icon_preview")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "slug")
    list_filter = ("title",)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
            if db_field.name == 'icon':
                kwargs['widget'] = ClearableFileInput(attrs={
                    'accept': '.png, .svg, image/png, image/svg+xml'
                })
            return super().formfield_for_dbfield(db_field, request, **kwargs)

    def category_count(self, obj):
        return obj.get_descendant_count()

    def icon_preview(self, obj):
        if obj.icon: 
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', obj.icon.url)
        return "No image"
    class Media:
        js = ('js/admin_image_preview.js',)

        