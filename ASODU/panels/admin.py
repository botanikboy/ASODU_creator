from django.contrib import admin

from .models import Vendor, Panel, Equipment, Project, EquipmentPanelAmount


class EquipmentPanelAmountInline(admin.TabularInline):
    model = EquipmentPanelAmount
    fields = ('equipment', 'amount')
    extra = 1
    verbose_name = 'Оборудование в щите'


class PanelAdmin(admin.ModelAdmin):
    list_display = ('project', 'name', 'description')
    search_fields = ('project', 'name')
    list_filter = ('function_type',)
    inlines = (EquipmentPanelAmountInline,)


class VendorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name',)
    list_filter = ('author',)


class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'code', 'description')
    search_fields = ('code', 'description')
    list_filter = ('vendor',)


admin.site.register(Vendor, VendorAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(Panel, PanelAdmin)
