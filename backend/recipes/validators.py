from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet


class IngredientRecipeValidator(BaseInlineFormSet):
    def clean(self):
        super().clean()

        items = [item.cleaned_data.get('DELETE')
                 for item in self.forms if hasattr(item, 'cleaned_data')]

        if all(items):
            raise ValidationError('Укажите хотя бы один ингредиент')
