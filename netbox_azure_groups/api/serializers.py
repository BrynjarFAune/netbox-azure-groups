from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from ..models import AzureGroup, GroupMembership, GroupOwnership


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

    class Meta:
        model = GroupMembership
        fields = [
            'id', 'url', 'display', 'group', 'contact', 'device', 'membership_type',
            'nested_via', 'created', 'last_updated', 'custom_fields', 'tags'
        ]
        read_only_fields = ['created', 'last_updated']


class GroupOwnershipSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='plugins-api:netbox_azure_groups-api:groupownership-detail')

    class Meta:
        model = GroupOwnership
        fields = [
            'id', 'url', 'display', 'group', 'contact', 'assigned_date',
            'created', 'last_updated', 'custom_fields', 'tags'
        ]
        read_only_fields = ['assigned_date', 'created', 'last_updated']