from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import (Attachment, Equipment, EquipmentGroup,
                     EquipmentPanelAmount, Panel, Project, Vendor)

User = get_user_model()


class EquipmentPanelAmountInline(admin.TabularInline):
    model = EquipmentPanelAmount
    fields = ('equipment', 'amount')
    extra = 0
    verbose_name = 'Элемент'
    verbose_name_plural = 'Оборудование в щите'


class AttachmentInline(admin.TabularInline):
    model = Attachment
    fields = ('drawing', 'description')
    extra = 0
    verbose_name = 'Файл'
    verbose_name_plural = 'Файлы'


class PanelAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'description')
    exclude = ('files',)
    search_fields = ('project', 'name')
    list_filter = ('function_type', 'project')
    inlines = (EquipmentPanelAmountInline, AttachmentInline)


class VendorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name',)
    list_filter = ('author',)
    filter_horizontal = ('co_authors',)


class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'vendor', 'description', 'group')
    search_fields = ('code', 'description')
    list_filter = ('vendor', 'group')


class EquipmentGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    list_filter = ('title',)


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('drawing', 'panel', 'description')
    search_fields = ('drawing', 'panel')
    list_filter = ('panel',)


admin.site.register(Vendor, VendorAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(Panel, PanelAdmin)
admin.site.register(EquipmentGroup, EquipmentGroupAdmin)
admin.site.register(Attachment, AttachmentAdmin)
