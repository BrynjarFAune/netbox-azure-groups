from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from ..models import AzureGroup, ContactGroupMembership, ContactGroupOwnership, DeviceGroupMembership


class AzureGroupSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='plugins-api:netbox_azure_groups-api:azuregroup-detail')
    total_member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = AzureGroup
        fields = [
            'id', 'url', 'display', 'name', 'description', 'object_id', 'mail',
            'group_type', 'is_security_enabled', 'is_mail_enabled', 'created_datetime',
            'total_member_count', 'created', 'last_updated', 'custom_fields', 'tags'
        ]


class ContactGroupMembershipSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='plugins-api:netbox_azure_groups-api:contactgroupmembership-detail')
    group = AzureGroupSerializer(read_only=True)
    group_id = serializers.IntegerField(write_only=True)
    contact_id = serializers.IntegerField(write_only=True)
    member_type_display = serializers.CharField(source='get_member_type_display', read_only=True)
    
    class Meta:
        model = ContactGroupMembership
        fields = [
            'id', 'url', 'display', 'group', 'group_id', 'contact', 'contact_id',
            'member_type', 'member_type_display', 'created', 'last_updated',
            'custom_fields', 'tags'
        ]


class ContactGroupOwnershipSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='plugins-api:netbox_azure_groups-api:contactgroupownership-detail')
    group = AzureGroupSerializer(read_only=True)
    group_id = serializers.IntegerField(write_only=True)
    contact_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ContactGroupOwnership
        fields = [
            'id', 'url', 'display', 'group', 'group_id', 'contact', 'contact_id',
            'created', 'last_updated', 'custom_fields', 'tags'
        ]


class DeviceGroupMembershipSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='plugins-api:netbox_azure_groups-api:devicegroupmembership-detail')
    group = AzureGroupSerializer(read_only=True)
    group_id = serializers.IntegerField(write_only=True)
    device_id = serializers.IntegerField(write_only=True)
    member_type_display = serializers.CharField(source='get_member_type_display', read_only=True)
    
    class Meta:
        model = DeviceGroupMembership
        fields = [
            'id', 'url', 'display', 'group', 'group_id', 'device', 'device_id',
            'member_type', 'member_type_display', 'created', 'last_updated',
            'custom_fields', 'tags'
        ]