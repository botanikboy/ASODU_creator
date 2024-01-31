from django import forms
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe

from .models import EquipmentPanelAmount, Panel, Project, Attachment


class PanelForm(forms.ModelForm):

    class Meta:
        model = Panel
        fields = ('name', 'function_type', 'description', 'files')
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


class PanelCopyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PanelCopyForm, self).__init__(*args, **kwargs)

        if self.request and self.request.user.is_authenticated:
            self.fields['project'].queryset = Project.objects.filter(
                author=self.request.user)
        self.fields['name'].label = 'Новое имя щита'
        self.fields['project'].label = 'Проект'

    class Meta:
        model = Panel
        fields = ('name', 'description', 'project')

    project = forms.ModelChoiceField(
        queryset=Project.objects.none()
    )

    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get('project')
        if project.author != self.request.user:
            raise ValidationError(
                'Можно копировать только в собственные проекты.'
            )
        matching_panels = Panel.objects.filter(
            project=project,
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


class AttachmentForm(forms.ModelForm):

    class Meta:
        model = Attachment
        fields = ('drawing', 'description')


EquipmentFormset = forms.inlineformset_factory(
    Panel, EquipmentPanelAmount, form=EquipmentForm, extra=0
)
