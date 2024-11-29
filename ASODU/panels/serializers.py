from rest_framework import serializers

from .models import (Equipment, EquipmentGroup, EquipmentPanelAmount, Panel,
                     Vendor)


class EquipmentGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentGroup
        fields = ['title']


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['name']


class EquipmentSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer()
    group = EquipmentGroupSerializer()

    class Meta:
        model = Equipment
        fields = ['vendor', 'code', 'description', 'group', 'units']


class EquipmentPanelAmountSerializer(serializers.ModelSerializer):
    equipment = EquipmentSerializer()

    class Meta:
        model = EquipmentPanelAmount
        fields = ['amount', 'equipment']


class PanelSerializer(serializers.ModelSerializer):
    amounts = EquipmentPanelAmountSerializer(many=True)

    class Meta:
        model = Panel
        fields = ['name', 'amounts', 'description']
