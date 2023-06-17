from django import forms

from .models import Panel, Project, EquipmentPanelAmount


class PanelForm(forms.ModelForm):

    class Meta:
        model = Panel
        fields = ('name', 'function_type', 'description')


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('name', 'description')


class EquipmentForm(forms.ModelForm):

    class Meta:
        model = EquipmentPanelAmount
        fields = ('equipment', 'amount')


EquipmentFormset = forms.inlineformset_factory(
    Panel, EquipmentPanelAmount, form=EquipmentForm, extra=2
)
