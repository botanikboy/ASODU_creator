from django import forms
from django.core.exceptions import ValidationError

from .models import Panel, Project, EquipmentPanelAmount


class PanelForm(forms.ModelForm):

    class Meta:
        model = Panel
        fields = ('name', 'function_type', 'description')
        exclude = ('project',)

    def clean(self):
        cleaned_data = super().clean()
        matching_panels = Panel.objects.filter(
            project=self.instance.project,
            name=cleaned_data.get('name')
        )
        if self.instance:
            matching_panels = matching_panels.exclude(pk=self.instance.pk)
        if matching_panels.exists():
            raise ValidationError(
                'Щит с таким именем уже существует в этом проекте.'
            )


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('name', 'description')


class EquipmentForm(forms.ModelForm):

    class Meta:
        model = EquipmentPanelAmount
        fields = ('equipment', 'amount')


EquipmentFormset = forms.inlineformset_factory(
    Panel, EquipmentPanelAmount, form=EquipmentForm, extra=1
)
