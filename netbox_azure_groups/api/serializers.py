from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from ..models import AzureGroup, GroupMembership


class AzureGroupSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='plugins-api:netbox_azure_groups-api:azuregroup-detail')
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = AzureGroup
        fields = [
            'id', 'url', 'display', 'name', 'description', 'object_id', 'mail',
            'group_type', 'is_security_enabled', 'is_mail_enabled', 'created_datetime',
            'member_count', 'created', 'last_updated', 'custom_fields', 'tags'
        ]


class GroupMembershipSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='plugins-api:netbox_azure_groups-api:groupmembership-detail')
    group = AzureGroupSerializer(read_only=True)
    group_id = serializers.IntegerField(write_only=True)
    member_type_display = serializers.CharField(source='get_member_type_display', read_only=True)
    
    class Meta:
        model = GroupMembership
        fields = [
            'id', 'url', 'display', 'group', 'group_id', 'content_type', 'object_id',
            'member', 'member_type', 'member_type_display', 'created', 'last_updated',
            'custom_fields', 'tags'
        ]