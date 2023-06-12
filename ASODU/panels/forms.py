from django import forms

from .models import Panel


class PanelForm(forms.ModelForm):
    class Meta:
        model = Panel
        fields = ('name', 'function_type', 'description', 'equipment')
