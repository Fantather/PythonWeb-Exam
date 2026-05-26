from django import forms
from forum.models import Category, Topic
from django.utils.translation import gettext_lazy as _


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["title", "description", "icon"]

        widgets = {
        'title': forms.TextInput(attrs={'class': 'validate'}),
        'description': forms.Textarea(attrs={'class': 'materialize-textarea'}),
        'icon': forms.ClearableFileInput(attrs={'class': 'file-input'}),
        }

   

#вдруг сортировка понадобится, вот у меня пример из дз будет, просто перепишу под что надо
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

