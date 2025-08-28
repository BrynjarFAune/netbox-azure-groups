from django.db.models import Count
from netbox.api.viewsets import NetBoxModelViewSet
from ..models import AzureGroup, ContactGroupMembership, ContactGroupOwnership, DeviceGroupMembership
from .serializers import (
    AzureGroupSerializer, 
    ContactGroupMembershipSerializer, 
    ContactGroupOwnershipSerializer, 
    DeviceGroupMembershipSerializer
)


class AzureGroupViewSet(NetBoxModelViewSet):
    queryset = AzureGroup.objects.prefetch_related('tags').annotate(
        total_member_count=Count('contact_memberships') + Count('device_memberships')
    )
    serializer_class = AzureGroupSerializer
    filterset_fields = [
        'name', 'object_id', 'group_type', 'is_security_enabled',
        'is_mail_enabled', 'created_datetime'
    ]


class ContactGroupMembershipViewSet(NetBoxModelViewSet):
    queryset = ContactGroupMembership.objects.prefetch_related('tags', 'group', 'contact')
    serializer_class = ContactGroupMembershipSerializer
    filterset_fields = [
        'group_id', 'contact_id', 'member_type'
    ]


class ContactGroupOwnershipViewSet(NetBoxModelViewSet):
    queryset = ContactGroupOwnership.objects.prefetch_related('tags', 'group', 'contact')
    serializer_class = ContactGroupOwnershipSerializer
    filterset_fields = [
        'group_id', 'contact_id'
    ]


class DeviceGroupMembershipViewSet(NetBoxModelViewSet):
    queryset = DeviceGroupMembership.objects.prefetch_related('tags', 'group', 'device')
    serializer_class = DeviceGroupMembershipSerializer
    filterset_fields = [
        'group_id', 'device_id', 'member_type'
    ]