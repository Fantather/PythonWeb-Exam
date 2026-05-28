from django.contrib import admin
from accounts.models import User
from .forms import AdminPanelUserCreationForm, AdminPanelUserChangeForm
# Register your models here.
from forum.models import Category, Post, Topic
from django.utils.html import format_html   
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from django.forms import ClearableFileInput

# admin.site.register(Topic)
# admin.site.register(Post)

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

@admin.register(Category)
class CategoryAdmin(TreeAdmin):
    model = Category
    form = movenodeform_factory(Category )
    list_display = ("title", "slug", "description", "category_count", "icon_preview")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "slug")
    list_filter = ("title",)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
            if db_field.name == 'icon':
                kwargs['widget'] = ClearableFileInput(attrs={
                    'accept': '.png, .svg, .jpg, .jpeg, .webp, image/webp, image/png, image/svg+xml, image/jpeg', 
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

        
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_closed", "is_pinned", "views_count", "replies_count", "last_active")
    search_fields = ("title",)
    list_filter = ("title",)



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("topic", "author", "content", "likes_count", "parent")
    search_fields = ("content",)
    list_filter = ("topic",)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
            if db_field.name == 'image':
                kwargs['widget'] = ClearableFileInput(attrs={
                    'accept': '.png, .svg, .jpg, .jpeg, .webp, image/webp, image/png, image/svg+xml, image/jpeg', 
                })
            return super().formfield_for_dbfield(db_field, request, **kwargs)
    