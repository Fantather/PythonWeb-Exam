from django import forms
from forum.models import Community, Topic
from django.utils.translation import gettext_lazy as _


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

