from django import forms
from django.db.models import Q
from django.shortcuts import get_list_or_404
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe

from .models import Attachment, EquipmentPanelAmount, Panel, Project

User = get_user_model()


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


class PanelCopyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PanelCopyForm, self).__init__(*args, **kwargs)

        if self.request and self.request.user.is_authenticated:
            self.fields['project'].queryset = Project.objects.filter(
                Q(author=self.request.user) | Q(
                    id__in=self.request.user.co_projects.values('id'))
            )
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
        if (project.author != self.request.user
                and project not in self.request.user.co_projects.all()):
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
        fields = ('is_published', 'name', 'description')
        widgets = {
            'is_published': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}),
        }


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

    def as_table(self):
        equipment_instance = (self.instance.equipment
                              if self.instance.pk else None)
        units = equipment_instance.units if equipment_instance else "—"
        return mark_safe(
            f"<tr>"
            f"<td>{self['equipment']}</td>"
            f"<td>{self['amount']}</td>"
            f"<td>{units}</td>"
            f"<td>{self['DELETE']}</td>"
            f"<td>{self['id']}</td>"
            f"</tr>"
        )

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


class CoAuthorForm(forms.Form):
    co_author = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Соавтор",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
    )
    co_authors = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not project:
            raise ValueError("Необходимо передать проект")
        self.project = project

    def save(self):
        if self.cleaned_data['co_authors']:
            co_authors_ids = [
                int(id) for id in self.cleaned_data['co_authors'].split(',')]
            co_authors = get_list_or_404(User, id__in=co_authors_ids)
            self.project.co_authors.set(co_authors)
        else:
            self.project.co_authors.clear()
        self.project.save()
