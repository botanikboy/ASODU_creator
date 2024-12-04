from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q
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
        if self.instance.pk:
            self.fields['equipment'].required = False

    def as_table(self):
        equipment_instance = (self.instance.equipment
                              if self.instance.pk else None)
        if self.instance.pk:
            equipment_display = (str(equipment_instance)
                                 if equipment_instance else "—")
            equipment_field = f"<span>{equipment_display}</span>"
        else:
            equipment_field = str(self['equipment'])
        units = equipment_instance.units if equipment_instance else "—"
        return mark_safe(
            f"{self.render_non_field_errors()}"
            f"<tr>"
            f"<td>{equipment_field}"
            f"{self.render_errors(self['equipment'])}</td>"
            f"<td>{self['amount']}"
            f"{self.render_errors(self['amount'])}</td>"
            f"<td>{units}</td>"
            '<td>'
            '<button type="button" class="btn btn-outline-danger '
            'btn-sm remove-row">'
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

    def is_empty(self):
        equipment = self.cleaned_data.get('equipment')
        amount = self.cleaned_data.get('amount')
        return not equipment and not amount

    def clean_equipment(self):
        if self.instance.pk:
            return self.instance.equipment
        equipment = self.cleaned_data.get('equipment')
        if not equipment:
            raise forms.ValidationError(
                'Поле "Оборудование" обязательно для новых строк.')
        return equipment

    class Meta:
        model = EquipmentPanelAmount
        fields = ('equipment', 'amount')
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control w-60',
                'step': 1,
                'min': 0,
                'max': 99999,
            }),
        }


class AttachmentForm(forms.ModelForm):

    class Meta:
        model = Attachment
        fields = ('drawing', 'description')


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
