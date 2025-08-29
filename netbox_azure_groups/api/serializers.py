from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from ..models import AzureGroup


class AzureGroupSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='plugins-api:netbox_azure_groups-api:azuregroup-detail')

    class Meta:
        model = AzureGroup
        fields = [
            'id', 'url', 'display', 'object_id', 'name', 'description', 'group_type',
            'source', 'is_security_enabled', 'is_mail_enabled', 'mail', 'membership_type',
            'membership_rule', 'member_count', 'owner_count', 'azure_created', 'azure_modified',
            'last_sync', 'is_deleted', 'created', 'last_updated', 'custom_fields', 'tags'
        ]
        read_only_fields = [
            'member_count', 'owner_count', 'last_sync', 'created', 'last_updated'
        ]


class GroupMembershipSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='plugins-api:netbox_azure_groups-api:groupmembership-detail')
    group = AzureGroupSerializer(read_only=True)
    group_id = serializers.IntegerField(write_only=True)
    contact_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    device_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    membership_type_display = serializers.CharField(source='get_membership_type_display', read_only=True)
    
    class Meta:
        model = GroupMembership
        fields = [
            'id', 'url', 'display', 'group', 'group_id', 'contact', 'contact_id',
            'device', 'device_id', 'membership_type', 'membership_type_display',
            'nested_via', 'created', 'last_updated'
        ]
        read_only_fields = ['created', 'last_updated']


class GroupOwnershipSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='plugins-api:netbox_azure_groups-api:groupownership-detail')
    group = AzureGroupSerializer(read_only=True)
    group_id = serializers.IntegerField(write_only=True)
    contact_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = GroupOwnership
        fields = [
            'id', 'url', 'display', 'group', 'group_id', 'contact', 'contact_id',
            'created', 'last_updated'
        ]
        read_only_fields = ['created', 'last_updated']