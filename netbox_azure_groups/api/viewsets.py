from django.db.models import Count
from netbox.api.viewsets import NetBoxModelViewSet
from ..models import AzureGroup, GroupMembership
from .serializers import AzureGroupSerializer, GroupMembershipSerializer


class AzureGroupViewSet(NetBoxModelViewSet):
    queryset = AzureGroup.objects.prefetch_related('tags').annotate(
        member_count=Count('memberships')
    )
    serializer_class = AzureGroupSerializer
    filterset_fields = [
        'name', 'object_id', 'group_type', 'is_security_enabled',
        'is_mail_enabled', 'created_datetime'
    ]


class GroupMembershipViewSet(NetBoxModelViewSet):
    queryset = GroupMembership.objects.prefetch_related('tags', 'group')
    serializer_class = GroupMembershipSerializer
    filterset_fields = [
        'group_id', 'content_type', 'object_id', 'member_type'
    ]