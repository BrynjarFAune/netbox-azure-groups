from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import action
from rest_framework.response import Response
from netbox.api.viewsets import NetBoxModelViewSet
from ..models import AzureGroup
from ..models.azure_groups import GroupTypeChoices, GroupSourceChoices
from .serializers import AzureGroupSerializer


class AzureGroupViewSet(NetBoxModelViewSet):
    queryset = AzureGroup.objects.filter(is_deleted=False)
    serializer_class = AzureGroupSerializer
    filterset_fields = [
        'name', 'object_id', 'group_type', 'source', 'is_security_enabled',
        'is_mail_enabled', 'membership_type', 'azure_created'
    ]
    
    def get_serializer_class(self):
        # Use read-only serializer for on-premises groups
        if self.action in ['update', 'partial_update']:
            obj = self.get_object()
            if obj.source == GroupSourceChoices.ON_PREMISES:
                # Would need AzureGroupReadOnlySerializer - for now return regular
                return AzureGroupSerializer
        return super().get_serializer_class()
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Quick statistics endpoint."""
        queryset = self.get_queryset()
        return Response({
            'total': queryset.count(),
            'by_source': {
                'azure_ad': queryset.filter(source=GroupSourceChoices.AZURE_AD).count(),
                'on_premises': queryset.filter(source=GroupSourceChoices.ON_PREMISES).count(),
                'external': queryset.filter(source=GroupSourceChoices.EXTERNAL).count(),
            },
            'by_type': {
                choice[0]: queryset.filter(group_type=choice[0]).count()
                for choice in GroupTypeChoices.CHOICES
            },
            'stale_count': queryset.filter(
                last_sync__lt=timezone.now() - timedelta(hours=24)
            ).count(),
            'deleted_count': AzureGroup.objects.filter(is_deleted=True).count(),
        })
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Paginated member list."""
        group = self.get_object()
        
        # Use new unified membership model if available, fallback to legacy
        if hasattr(group, 'memberships'):
            memberships = group.memberships.select_related('contact', 'device')
        else:
            # Legacy approach - combine contact and device memberships
            contact_memberships = group.contact_memberships.select_related('contact')
            device_memberships = group.device_memberships.select_related('device')
            
            # Create a combined list
            memberships = list(contact_memberships) + list(device_memberships)
        
        # Pagination
        paginator = self.paginator
        page = paginator.paginate_queryset(memberships, request)
        
        # Simple serialization for now
        serialized_data = []
        for membership in page:
            if hasattr(membership, 'contact') and membership.contact:
                member_data = {
                    'type': 'contact',
                    'id': membership.contact.id,
                    'name': str(membership.contact),
                    'membership_type': getattr(membership, 'membership_type', membership.member_type)
                }
            elif hasattr(membership, 'device') and membership.device:
                member_data = {
                    'type': 'device', 
                    'id': membership.device.id,
                    'name': str(membership.device),
                    'membership_type': getattr(membership, 'membership_type', membership.member_type)
                }
            else:
                continue
            serialized_data.append(member_data)
        
        return paginator.get_paginated_response(serialized_data)
    
    @action(detail=False, methods=['get'], url_path='sync-status')
    def sync_status(self, request):
        """Basic sync health check."""
        queryset = self.get_queryset()
        stale_threshold = timezone.now() - timedelta(hours=24)
        
        stale_groups = queryset.filter(last_sync__lt=stale_threshold)
        
        return Response({
            'last_update': queryset.order_by('-last_sync').first().last_sync if queryset.exists() else None,
            'total_groups': queryset.count(),
            'stale_groups': stale_groups.count(),
            'health': 'healthy' if not stale_groups.exists() else 'stale'
        })


class GroupMembershipViewSet(NetBoxModelViewSet):
    queryset = GroupMembership.objects.select_related('group', 'contact', 'device')
    serializer_class = GroupMembershipSerializer
    filterset_fields = [
        'group_id', 'contact_id', 'device_id', 'membership_type'
    ]


class GroupOwnershipViewSet(NetBoxModelViewSet):
    queryset = GroupOwnership.objects.select_related('group', 'contact')
    serializer_class = GroupOwnershipSerializer
    filterset_fields = [
        'group_id', 'contact_id'
    ]