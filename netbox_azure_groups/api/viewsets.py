from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import action
from rest_framework.response import Response
from netbox.api.viewsets import NetBoxModelViewSet
from ..models import AzureGroup, GroupMembership, GroupOwnership
from ..models.azure_groups import GroupTypeChoices, GroupSourceChoices
from .serializers import AzureGroupSerializer, GroupMembershipSerializer, GroupOwnershipSerializer


class AzureGroupViewSet(NetBoxModelViewSet):
    queryset = AzureGroup.objects.filter(is_deleted=False)
    serializer_class = AzureGroupSerializer
    filterset_fields = [
        'name', 'object_id', 'group_type', 'source', 'is_security_enabled',
        'is_mail_enabled', 'membership_type', 'azure_created'
    ]
    
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
    queryset = GroupMembership.objects.all().order_by('pk')
    serializer_class = GroupMembershipSerializer
    filterset_fields = ['group', 'contact', 'device', 'membership_type']


class GroupOwnershipViewSet(NetBoxModelViewSet):
    queryset = GroupOwnership.objects.all().order_by('pk')
    serializer_class = GroupOwnershipSerializer
    filterset_fields = ['group', 'contact']