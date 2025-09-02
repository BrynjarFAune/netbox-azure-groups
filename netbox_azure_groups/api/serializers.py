from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from ..models import (
    AzureGroup, GroupMembership, GroupOwnership,
    ProtectedResource, AccessControlMethod, AccessGrant
)


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


# Access Control Serializers

class ProtectedResourceSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='plugins-api:netbox_azure_groups-api:protectedresource-detail')

    class Meta:
        model = ProtectedResource
        fields = [
            'id', 'url', 'display', 'name', 'resource_type', 'description',
            'base_url', 'ip_addresses', 'physical_location',
            'owner_contact', 'business_unit', 'criticality', 'is_active',
            'created', 'last_updated', 'custom_fields', 'tags'
        ]
        read_only_fields = ['created', 'last_updated']


class AccessControlMethodSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='plugins-api:netbox_azure_groups-api:accesscontrolmethod-detail')

    class Meta:
        model = AccessControlMethod
        fields = [
            'id', 'url', 'display', 'resource', 'control_type', 'name', 'description',
            'azure_group', 'access_level', 'configuration', 'is_active', 'last_verified',
            'created', 'last_updated', 'custom_fields', 'tags'
        ]
        read_only_fields = ['created', 'last_updated']


class AccessGrantSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='plugins-api:netbox_azure_groups-api:accessgrant-detail')

    class Meta:
        model = AccessGrant
        fields = [
            'id', 'url', 'display', 'resource', 'contact', 'azure_group', 'control_method',
            'access_level', 'granted_via', 'first_granted', 'last_verified', 'is_active',
            'created', 'last_updated', 'custom_fields', 'tags'
        ]
        read_only_fields = ['first_granted', 'last_verified', 'created', 'last_updated']