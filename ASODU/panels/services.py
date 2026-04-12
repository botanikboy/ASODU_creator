import os
import shutil

from django.conf import settings
from django.db import models, transaction
from django.forms import inlineformset_factory
from django.utils import timezone

from core.utils import transliterate

from .forms import EquipmentForm, UlErrorList
from .models import (Attachment, Equipment, EquipmentGroup,
                     EquipmentPanelAmount, Panel)
from .serializers import PanelSerializer
from .tasks import generate_excel_report
from .utils import amounts_by_group


def save_equipment_formset(formset):
    """Persist one equipment formset with bulk operations."""
    to_update = []
    to_create = []
    to_delete = []

    for form in formset:
        if form.is_empty():
            continue
        if form.cleaned_data.get('DELETE') and form.instance.pk:
            to_delete.append(form.instance)
        elif not form.cleaned_data.get('DELETE'):
            instance = form.save(commit=False)
            if instance.pk:
                to_update.append(instance)
            else:
                to_create.append(instance)

    if to_delete:
        EquipmentPanelAmount.objects.filter(
            pk__in=[obj.pk for obj in to_delete]
        ).delete()

    if to_update:
        EquipmentPanelAmount.objects.bulk_update(to_update, ['amount'])

    if to_create:
        EquipmentPanelAmount.objects.bulk_create(to_create)


def prepare_equipment_formset_for_group(request, panel, group, amounts):
    """Build one grouped inline formset for panel equipment editing."""
    existing_equipment_ids = [amount.equipment.id for amount in amounts]
    amounts_in_panel = [amount.id for amount in amounts]
    amounts_queryset = EquipmentPanelAmount.objects.filter(
        id__in=amounts_in_panel
    ).select_related('equipment', 'equipment__group')
    equipment_queryset = Equipment.objects.exclude(
        id__in=existing_equipment_ids
    ).select_related('group')

    def dynamic_formfield_callback(field, **kwargs):
        if isinstance(field, models.ForeignKey) and field.name == 'equipment':
            formfield = field.formfield()
            formfield.queryset = equipment_queryset.filter(
                group=group
            ).select_related('group')
            return formfield
        return field.formfield(**kwargs)

    equipment_formset = inlineformset_factory(
        Panel,
        EquipmentPanelAmount,
        form=EquipmentForm,
        extra=0,
        can_delete=True,
        formfield_callback=dynamic_formfield_callback,
    )

    return equipment_formset(
        request.POST or None,
        instance=panel,
        error_class=UlErrorList,
        queryset=amounts_queryset,
        prefix=f'group_{group.id if group else "no_group"}',
    )


def build_panel_group_formsets(request, panel):
    """Build all grouped equipment formsets for a panel edit page."""
    grouped_amounts = amounts_by_group(panel)
    processed_groups_ids = [group.id for group in set(grouped_amounts.keys())]
    missing_groups = EquipmentGroup.objects.exclude(id__in=processed_groups_ids)

    group_formsets = []

    for group, amounts in grouped_amounts.items():
        formset = prepare_equipment_formset_for_group(
            request, panel, group, amounts
        )
        group_formsets.append({'group': group, 'formset': formset})

    for group in missing_groups:
        formset = prepare_equipment_formset_for_group(request, panel, group, [])
        group_formsets.append({'group': group, 'formset': formset})

    return group_formsets


def save_panel_group_formsets(group_formsets):
    """Persist all valid grouped equipment formsets for a panel."""
    for group_data in group_formsets:
        save_equipment_formset(group_data['formset'])


def enqueue_excel_report(*, panels, user, model, obj_id):
    """Serialize panel data and schedule report generation."""
    panels_data = PanelSerializer(panels, many=True).data
    report_key = (
        f'{user}-{model}-{obj_id}-'
        f'{timezone.now().strftime("%Y%m%d%H%M%S%f")}'
    )
    generate_excel_report.delay(panels_data, report_key)
    return report_key


def copy_panel(source_panel, *, project, name, description):
    """Clone a panel with all equipment rows and attachments."""
    with transaction.atomic():
        copied_panel = Panel.objects.create(
            name=name,
            description=description,
            project=project,
            function_type=source_panel.function_type,
        )

        copied_amounts = [
            EquipmentPanelAmount(
                equipment=amount.equipment,
                panel=copied_panel,
                amount=amount.amount,
            )
            for amount in source_panel.amounts.select_related('equipment')
        ]
        EquipmentPanelAmount.objects.bulk_create(copied_amounts)

        copied_attachments = []
        for attachment in source_panel.attachments.all():
            copied_attachments.append(
                Attachment(
                    panel=copied_panel,
                    description=attachment.description,
                    drawing=_copy_attachment_file(attachment, copied_panel),
                )
            )
        Attachment.objects.bulk_create(copied_attachments)

    return copied_panel


def _copy_attachment_file(source_attachment, target_panel):
    new_folder = _build_panel_storage_dir(target_panel)
    os.makedirs(new_folder, exist_ok=True)

    new_file = os.path.join(
        new_folder,
        os.path.basename(source_attachment.drawing.name),
    )
    shutil.copy2(source_attachment.drawing.path, new_file)
    return os.path.relpath(new_file, settings.MEDIA_ROOT)


def _build_panel_storage_dir(panel):
    return os.path.join(
        settings.MEDIA_ROOT,
        'panels',
        f'{panel.project.pk}',
        f'{panel.pk}_{transliterate(panel.name)}',
    )
