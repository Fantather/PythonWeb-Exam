
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _
from forum.forms import CategoryForm, UserChangeForm, UserRegistrationForm


class AdminPanelUserForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        fields = ("email", "username", "first_name", "last_name", "password", "is_active", "is_staff", "is_superuser"
                  )

class AdminPanelUserCreationForm(UserRegistrationForm):
    class Meta(UserRegistrationForm.Meta):
        fields = ("email", "username", "first_name", "last_name", "password1", "password2", "is_active", "is_staff", "is_superuser"
                  )
        
class AdminPanelUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        fields = ("email", "username", "first_name", "last_name", "password", "is_active", "is_staff", "is_superuser"
 )
        

class AdminPanelCategoryForm(CategoryForm):
    class Meta(CategoryForm.Meta):

            
        fields = (*CategoryForm.Meta.fields, "slug", "_position", "_ref_node_id")
        widgets = {
            **CategoryForm.Meta.widgets,
            "slug": forms.TextInput(attrs={"required": False}),
        }
    