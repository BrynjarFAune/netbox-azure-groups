from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from ..models import AzureGroup


class AzureGroupSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='plugins-api:netbox_azure_groups-api:azuregroup-detail')

    class Meta:
        model = AzureGroup
        fields = [
            'id', 'url', 'display', 'object_id', 'name', 'description', 'group_type',
            'is_security_enabled', 'is_mail_enabled', 'mail', 'created_datetime',
            'created', 'last_updated', 'custom_fields', 'tags'
        ]
        read_only_fields = ['created', 'last_updated']