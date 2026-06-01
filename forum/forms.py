from django import forms
from forum.models import Community, Topic, Post
from django.utils.translation import gettext_lazy as _


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def clean(self, data, initial=None):
        if not data:
            if self.required:
                return super().clean(data, initial)
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        clean_single_file = super().clean
        return [clean_single_file(item, initial) for item in data]


class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ["title", "description", "icon"]

        widgets = {
        'title': forms.TextInput(attrs={'class': 'validate'}),
        'description': forms.Textarea(attrs={'class': 'materialize-textarea'}),
        'icon': forms.ClearableFileInput(attrs={
                'class': 'file-input', 
                'accept': '.png, .svg, .jpg, .jpeg, .webp, image/webp, image/png, image/svg+xml, image/jpeg', 
            }),
        }


class TopicCreateForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'materialize-textarea'}),
        label=_("Content"),
        required=True
    )

    images = MultipleFileField(
        widget=MultipleFileInput(attrs={
            'class': 'file-input', 
            'accept': '.png, .svg, .jpg, .jpeg, .webp, image/webp, image/png, image/svg+xml, image/jpeg', 
            'multiple': True
        }),
        label=_("Images"),
        required=False
    )   
    class Meta:
        model = Topic
        fields = ["title", "community"]

        widgets = {
            'title': forms.TextInput(attrs={'class': 'validate', 'required': True}),
            'community': forms.Select(attrs={'class': 'materialize-select', 'required': True, 'initial': 'Выберите сообщество'}),
        }

class CommentCreateForm(forms.ModelForm):
    images = MultipleFileField(
        widget=MultipleFileInput(
            attrs={
                "class": "file-input",
                "accept": ".png, .svg, .jpg, .jpeg, .webp, image/webp, image/png, image/svg+xml, image/jpeg",
                "multiple": True,
            }
        ),
        label=_("Images"),
        required=False,
    )
    class Meta:
        model = Post
        fields = ["content"]

# вдруг сортировка понадобится, вот у меня пример из дз будет, просто перепишу под что надо
# class FilmFilterForm(forms.Form):
#     sort_choices = [
#         ('title', 'По названию'),
#         ('-title', 'По названию (убывание)'),
#         ('-release_year', 'Год выхода'),
#         ('release_year', 'Год выхода (возрастание)'),
#         ('-rating', 'Рейтинг (убывание)'),
#         ('rating', 'Рейтинг (возрастание)'),

#     ]
#     sort = forms.ChoiceField(
#         choices=sort_choices,
#         required=False,
#         initial='title',
#         widget=forms.Select(attrs={'id': 'sort-select'})
#         )
