from django.contrib import admin
from accounts.models import User
from .forms import AdminPanelUserCreationForm, AdminPanelUserChangeForm, AdminPostForm
# Register your models here.
from forum.models import Community, Post, Topic, PostImage
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from django.forms import ClearableFileInput
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    add_form = AdminPanelUserCreationForm
    form = AdminPanelUserChangeForm

    list_display = (
        "id",
        "email",
        "username",
        "full_name",
        "is_staff",
        "is_superuser",
        "is_active",
        "avatar_preview",
    )
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("id",)
    readonly_fields = ("avatar_preview",)

    fieldsets = (
        ("Данные для входа", {"fields": ("username", "email", "password")}),
        (
            "Подробности про пользователя",
            {"fields": ("first_name", "last_name", "avatar", "avatar_preview")},
        ),
        (
            "Статус на сайте и роли",
            {
                "classes": ("collapsed",),
                "fields": ("is_active", "is_staff", "is_superuser"),
            },
        ),
        ("Группы и разрешения", {"fields": ("groups", "user_permissions")}),
    )

    add_fieldsets = (
        (
            "Данные для входа",
            {"fields": ("username", "email", "password1", "password2")},
        ),
        ("Подробности про пользователя", {"fields": ("first_name", "last_name", "avatar")}),
        (
            "Статус на сайте и роли",
            {
                "classes": ("collapsed",),
                "fields": ("is_active", "is_staff", "is_superuser"),
            },
        ),
    )
    class Media:
        js = ('js/admin_image_preview.js',)

    @admin.display(description="Полное имя")
    def full_name(self, obj):
        first = obj.first_name if obj.first_name else ""
        last = obj.last_name if obj.last_name else ""
        return f"{first} {last}".strip() or "Не указано"

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 8px;" />',
                obj.avatar.url,
            )
        return "Нет изображения"

    avatar_preview.short_description = "Превью аватара"

    @admin.action(description="Activate selected users")
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(Community)
class CommunityAdmin(TreeAdmin):
    model = Community
    form = movenodeform_factory(Community)

    list_display = ("title", "slug", "description", "community_count", "icon_preview")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "slug")
    list_filter = ("title",)
    readonly_fields = ("icon_preview", "community_count")

    fieldsets = (
        ("Основная информация", {"fields": ("title", "slug", "description")}),
        ("Оформление", {"fields": ("icon", "icon_preview")}),
        (
            "Расположение в дереве",
            {
                "classes": ("collapse",),
                "fields": ("_position", "_ref_node_id"),
            },
        ),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "icon":
            kwargs["widget"] = ClearableFileInput(
                attrs={
                    "accept": ".png, .svg, .jpg, .jpeg, .webp, image/webp, image/png, image/svg+xml, image/jpeg",
                }
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def community_count(self, obj):
        return obj.get_descendant_count()

    community_count.short_description = "Количество дочерних"

    def icon_preview(self, obj):
        if obj.icon:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 8px;" />',
                obj.icon.url,
            )
        return "Нет изображения"

    icon_preview.short_description = "Превью"
    class Media:
        js = ("js/admin_image_preview.js",)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "community",
        "is_closed",
        "is_pinned",
        "views_count",
        "replies_count",
        "last_active",
    )
    search_fields = ("title",)
    list_filter = ("community", "is_closed", "is_pinned")

    readonly_fields = ("views_count", "replies_count", "last_active")

    fieldsets = (
        ("Основная информация", {"fields": ("title", "community")}),
        ("Статус и настройки", {"fields": ("is_closed", "is_pinned")}),
        (
            "Статистика (автоматическая)",
            {
                "classes": ("collapse",),
                "fields": ("views_count", "replies_count", "last_active"),
            },
        ),
    )


class PostTypeFilter(admin.SimpleListFilter):
    title = "Тип сообщения"
    parameter_name = "post_type"

    def lookups(self, request, model_admin):
        return (
            ("main", "Только главные посты"),
            ("reply", "Только комментарии"),
        )

    def queryset(self, request, queryset):
        if self.value() == "main":
            return queryset.filter(parent__isnull=True)
        if self.value() == "reply":
            return queryset.filter(parent__isnull=False)
        return queryset


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    readonly_fields = ("created_at",)
    class Meta:
        ordering = ["created_at"]
        verbose_name = "Изображение поста" 
        verbose_name_plural = "Изображения поста"  


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "topic",
        "post_type_badge",
        "author",
        "short_content",
        "likes_count",
    )
    search_fields = ("content", "author__username")

    list_filter = (PostTypeFilter, "topic")
    readonly_fields = ("likes_count", "post_type_badge")
    # autocomplete_fields = ("topic", "parent")
    # Он позволяет редактировать связанные модели прямо на странице основной модели.
    inlines = [PostImageInline]

    fieldsets = (
        ("Расположение", {"fields": ("topic", "parent")}),
        ("Контент сообщения", {"fields": ("author", "content")}),
        ("Статистика", {"classes": ("collapse",), "fields": ("likes_count",)}),
    )

    def short_content(self, obj):
        return (
            obj.content[:50] + "..."
            if obj.content and len(obj.content) > 50
            else obj.content
        )

    short_content.short_description = "Текст сообщения"

    def post_type_badge(self, obj):
        if obj.parent is None:
            return mark_safe(
                '<span style="color: white; background: #2e7d32; padding: 3px 8px; border-radius: 4px;">Главный пост</span>'
            )
        return mark_safe(
            '<span style="color: white; background: #1565c0; padding: 3px 8px; border-radius: 4px;">Комментарий</span>'
        )

    post_type_badge.short_description = "Тип"
