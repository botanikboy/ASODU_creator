from django.contrib import admin

from .models import (Equipment, EquipmentGroup, EquipmentPanelAmount, Panel,
                     Project, Vendor)


class EquipmentPanelAmountInline(admin.TabularInline):
    model = EquipmentPanelAmount
    fields = ('equipment', 'amount')
    extra = 0
    verbose_name = 'Элемент'
    verbose_name_plural = 'Оборудование в щите'


class PanelAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'description')
    search_fields = ('project', 'name')
    list_filter = ('function_type', 'project')
    inlines = (EquipmentPanelAmountInline,)


class VendorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name',)
    list_filter = ('author',)


class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'vendor', 'description', 'group')
    search_fields = ('code', 'description')
    list_filter = ('vendor', 'group')


class EquipmentGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    list_filter = ('title',)


admin.site.register(Vendor, VendorAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(Panel, PanelAdmin)
admin.site.register(EquipmentGroup, EquipmentGroupAdmin)
