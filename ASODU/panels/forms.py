from django import forms
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe

from .models import EquipmentPanelAmount, Panel, Project


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


class UlErrorList(ErrorList):
    def __str__(self):
        return self.as_ul()

    def as_ul(self):
        if not self:
            return ''
        error_list = [
            f'<li class="error alert alert-danger mt-1">{e}</li>' for e in self
        ]
        return mark_safe(f'<ul class="errorlist">{"".join(error_list)}</ul>')


class EquipmentForm(forms.ModelForm):

    class Meta:
        model = EquipmentPanelAmount
        fields = ('equipment', 'amount')


EquipmentFormset = forms.inlineformset_factory(
    Panel, EquipmentPanelAmount, form=EquipmentForm, extra=0
)
