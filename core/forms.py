from django import forms
from django.utils.translation import gettext_lazy as _
from accounts.forms import UserChangeForm, UserRegistrationForm, UserCreationForm
from accounts.models import User
from forum.models import Post, PostImage
from forum.forms import MultipleFileInput, MultipleFileField
from django.core.exceptions import ValidationError

# from forum.forms import CategoryForm

# class AdminPanelCategoryForm(CategoryForm):
#     class Meta(CategoryForm.Meta):


#         fields = (*CategoryForm.Meta.fields, "slug", "_position", "_ref_node_id")
#         widgets = {
#             **CategoryForm.Meta.widgets,
#             "slug": forms.TextInput(attrs={"required": False}),
#         }

class AdminPanelUserForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        fields = ("email", "username", "first_name", "last_name", "password", "is_active", "is_staff", "is_superuser"
                  )


class AdminPanelUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Подтверждение пароля", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "avatar"
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Пароли не совпадают.")
            return None
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AdminPanelUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "avatar",
        )


class AdminPostForm(forms.ModelForm):
    # Создаем виртуальное поле для массовой загрузки
    upload_images = MultipleFileField(
        widget=MultipleFileInput(attrs={"multiple": True}),
        label="Загрузить новые изображения",
        required=False,
    )

    class Meta:
        model = Post
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        topic = cleaned_data.get("topic")
        parent = cleaned_data.get("parent")

        if parent and topic:
            if parent.topic != topic:
                # Генерируем ошибку, которая подсветит поле красным
                raise ValidationError(
                    {
                        "parent": f'Этот родительский пост привязан к теме "{parent.topic}", '
                        f'его нельзя сохранить в тему "{topic}".'
                    }
                )

        return cleaned_data
