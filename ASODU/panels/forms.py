from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe

from .models import Attachment, Equipment, EquipmentPanelAmount, Panel, Project

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
            raise ValidationError({
                'name': 'Щит с таким именем уже существует в этом проекте.'
            })


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipment'].queryset = Equipment.objects.select_related(
            'group')

    def as_table(self):
        equipment_instance = (self.instance.equipment
                              if self.instance.pk else None)
        units = equipment_instance.units if equipment_instance else "—"
        return mark_safe(
            f"{self.render_non_field_errors()}"
            f"<tr>"
            f"<td>{self['equipment']}"
            f"{self.render_errors(self['equipment'])}</td>"
            f"<td>{self['amount']}"
            f"{self.render_errors(self['amount'])}</td>"
            f"<td>{units}</td>"
            '<td>'
            '<button type="button" class="btn btn-outline-danger remove-row">'
            'Удалить</button></td>'
            f"{self['DELETE'].as_hidden()}"
            f"{self['id'].as_hidden()}"
            "</tr>"
        )

    def render_errors(self, field):
        if field.errors:
            return ('<div class="text-danger">'
                    f'{" ".join(field.errors)}</div>')
        return ''

    class Meta:
        model = EquipmentPanelAmount
        fields = ('equipment', 'amount')

    def render_non_field_errors(self):
        """Вывод NON_FIELD_ERRORS для строки формы."""
        errors = self.non_field_errors()
        if errors:
            return (
                f"<tr>"
                f"<td colspan='4'><div class='text-danger'>"
                f"{' '.join(errors)}"
                f"</div></td>"
                f"</tr>"
            )
        return ''


class AttachmentForm(forms.ModelForm):

    class Meta:
        model = Attachment
        fields = ('drawing', 'description')


EquipmentFormset = forms.inlineformset_factory(
    Panel, EquipmentPanelAmount, form=EquipmentForm, extra=1
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

    def clean_co_authors(self):
        if not self.data['co_authors']:
            return []

        try:
            co_authors_ids = [
                int(id) for id in self.data['co_authors'].split(',')]
        except ValueError:
            raise ValidationError('Неверное значение')

        co_authors = User.objects.filter(id__in=co_authors_ids)
        if co_authors.exists():
            return co_authors
        else:
            raise ValidationError('Неверное значение')

    def save(self):
        self.project.co_authors.set(self.cleaned_data['co_authors'])
        self.project.save()
