from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import action
from rest_framework.response import Response
from netbox.api.viewsets import NetBoxModelViewSet
from ..models import (
    AzureGroup, GroupMembership, GroupOwnership,
    ProtectedResource, AccessControlMethod, AccessGrant,
    FortiGatePolicy, BusinessUnit
)
from ..models.azure_groups import GroupTypeChoices, GroupSourceChoices
from .serializers import (
    AzureGroupSerializer, GroupMembershipSerializer, GroupOwnershipSerializer,
    ProtectedResourceSerializer, AccessControlMethodSerializer, AccessGrantSerializer,
    FortiGatePolicySerializer, BusinessUnitSerializer
)


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

    @action(detail=True, methods=['get'], url_path='provides-access-to')
    def provides_access_to(self, request, pk=None):
        """List all resources this Azure group provides access to."""
        group = self.get_object()
        access_methods = AccessControlMethod.objects.filter(azure_group=group).select_related('resource')
        resources = [method.resource for method in access_methods]
        
        return Response({
            'group': group.name,
            'provides_access_to': [
                {
                    'resource': resource.name,
                    'resource_type': resource.get_resource_type_display(),
                    'access_level': method.get_access_level_display(),
                    'control_method': method.name
                }
                for method, resource in zip(access_methods, resources)
            ]
        })


class GroupMembershipViewSet(NetBoxModelViewSet):
    queryset = GroupMembership.objects.all().order_by('pk')
    serializer_class = GroupMembershipSerializer
    filterset_fields = ['group', 'contact', 'device', 'membership_type']


class GroupOwnershipViewSet(NetBoxModelViewSet):
    queryset = GroupOwnership.objects.all().order_by('pk')
    serializer_class = GroupOwnershipSerializer
    filterset_fields = ['group', 'contact']


# Access Control ViewSets

class BusinessUnitViewSet(NetBoxModelViewSet):
    queryset = BusinessUnit.objects.all()
    serializer_class = BusinessUnitSerializer
    filterset_fields = ['name', 'parent', 'contact', 'is_active']

    @action(detail=True, methods=['get'], url_path='children')
    def children(self, request, pk=None):
        """List child business units."""
        unit = self.get_object()
        children = BusinessUnit.objects.filter(parent=unit, is_active=True)
        
        return Response({
            'parent': unit.name,
            'children': [
                {
                    'id': child.id,
                    'name': child.name,
                    'description': child.description,
                    'contact': child.contact.name if child.contact else None
                }
                for child in children
            ]
        })

    @action(detail=True, methods=['get'], url_path='resources')
    def resources(self, request, pk=None):
        """List protected resources for this business unit."""
        unit = self.get_object()
        resources = unit.resources.all()
        
        return Response({
            'business_unit': unit.name,
            'protected_resources': [
                {
                    'id': resource.id,
                    'name': resource.name,
                    'resource_type': resource.get_resource_type_display(),
                    'criticality': resource.get_criticality_display(),
                    'is_active': resource.is_active
                }
                for resource in resources
            ]
        })


class ProtectedResourceViewSet(NetBoxModelViewSet):
    queryset = ProtectedResource.objects.all()
    serializer_class = ProtectedResourceSerializer
    filterset_fields = [
        'name', 'resource_type', 'owner_contact', 'business_unit', 
        'criticality', 'is_active'
    ]

    @action(detail=True, methods=['get'], url_path='who-has-access')
    def who_has_access(self, request, pk=None):
        """List all users with access to this resource."""
        resource = self.get_object()
        access_grants = AccessGrant.objects.filter(
            resource=resource, 
            is_active=True
        ).select_related('contact', 'azure_group', 'control_method')
        
        return Response({
            'resource': resource.name,
            'access_grants': [
                {
                    'contact': grant.contact.name if grant.contact else None,
                    'access_level': grant.get_access_level_display(),
                    'via_group': grant.azure_group.name,
                    'control_method': grant.control_method.name,
                    'granted_via': grant.get_granted_via_display(),
                    'first_granted': grant.first_granted
                }
                for grant in access_grants
            ]
        })

    @action(detail=True, methods=['get'], url_path='access-methods')
    def access_methods(self, request, pk=None):
        """List all access control methods for this resource."""
        resource = self.get_object()
        methods = AccessControlMethod.objects.filter(
            resource=resource,
            is_active=True
        ).select_related('azure_group')
        
        return Response({
            'resource': resource.name,
            'access_methods': [
                {
                    'name': method.name,
                    'control_type': method.get_control_type_display(),
                    'access_level': method.get_access_level_display(),
                    'azure_group': method.azure_group.name,
                    'is_active': method.is_active
                }
                for method in methods
            ]
        })


class AccessControlMethodViewSet(NetBoxModelViewSet):
    queryset = AccessControlMethod.objects.all()
    serializer_class = AccessControlMethodSerializer
    filterset_fields = [
        'resource', 'control_type', 'azure_group', 'access_level', 'is_active'
    ]


class AccessGrantViewSet(NetBoxModelViewSet):
    queryset = AccessGrant.objects.all()
    serializer_class = AccessGrantSerializer
    filterset_fields = [
        'resource', 'contact', 'azure_group', 'control_method', 
        'access_level', 'granted_via', 'is_active'
    ]

    @action(detail=False, methods=['get'], url_path='by-contact')
    def by_contact(self, request):
        """List access grants grouped by contact."""
        contact_id = request.query_params.get('contact_id')
        if not contact_id:
            return Response({'error': 'contact_id parameter required'}, status=400)
        
        grants = AccessGrant.objects.filter(
            contact_id=contact_id,
            is_active=True
        ).select_related('resource', 'azure_group', 'control_method')
        
        return Response({
            'contact_id': contact_id,
            'resource_access': [
                {
                    'resource': grant.resource.name,
                    'resource_type': grant.resource.get_resource_type_display(),
                    'access_level': grant.get_access_level_display(),
                    'via_group': grant.azure_group.name,
                    'control_method': grant.control_method.name,
                    'first_granted': grant.first_granted
                }
                for grant in grants
            ]
        })

    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Access control analytics and statistics."""
        queryset = self.get_queryset()
        
        return Response({
            'total_grants': queryset.count(),
            'active_grants': queryset.filter(is_active=True).count(),
            'by_access_level': {
                level[0]: queryset.filter(access_level=level[0]).count()
                for level in AccessGrant._meta.get_field('access_level').choices
            },
            'by_granted_via': {
                via[0]: queryset.filter(granted_via=via[0]).count()
                for via in AccessGrant._meta.get_field('granted_via').choices
            },
            'unique_contacts_with_access': queryset.filter(is_active=True).values('contact').distinct().count(),
            'unique_resources_with_grants': queryset.filter(is_active=True).values('resource').distinct().count()
        })


# FortiGate ViewSet

class FortiGatePolicyViewSet(NetBoxModelViewSet):
    queryset = FortiGatePolicy.objects.all()
    serializer_class = FortiGatePolicySerializer
    filterset_fields = [
        'policy_id', 'name', 'status', 'action', 'nat_enabled', 'utm_status',
        'fortigate_host', 'vdom', 'access_control_method'
    ]

    @action(detail=False, methods=['post'], url_path='bulk-import')
    def bulk_import(self, request):
        """Bulk import FortiGate policies from JSON"""
        policies_data = request.data
        
        if not isinstance(policies_data, list):
            return Response({'error': 'Expected list of policies'}, status=400)
        
        created_count = 0
        updated_count = 0
        errors = []
        
        for policy_data in policies_data:
            try:
                policy_id = policy_data.get('policy_id')
                fortigate_host = policy_data.get('fortigate_host')
                vdom = policy_data.get('vdom', 'root')
                
                # Try to find existing policy
                existing = FortiGatePolicy.objects.filter(
                    policy_id=policy_id,
                    fortigate_host=fortigate_host,
                    vdom=vdom
                ).first()
                
                if existing:
                    # Update existing policy
                    serializer = self.get_serializer(existing, data=policy_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        updated_count += 1
                    else:
                        errors.append(f"Policy {policy_id}: {serializer.errors}")
                else:
                    # Create new policy
                    serializer = self.get_serializer(data=policy_data)
                    if serializer.is_valid():
                        serializer.save()
                        created_count += 1
                    else:
                        errors.append(f"Policy {policy_id}: {serializer.errors}")
                        
            except Exception as e:
                errors.append(f"Policy {policy_data.get('policy_id', 'unknown')}: {str(e)}")
        
        return Response({
            'created': created_count,
            'updated': updated_count,
            'errors': errors
        })

    @action(detail=False, methods=['get'], url_path='by-action')
    def by_action(self, request):
        """Group policies by action (accept/deny)"""
        queryset = self.get_queryset()
        
        return Response({
            'accept': queryset.filter(action='accept').count(),
            'deny': queryset.filter(action='deny').count(),
            'ipsec': queryset.filter(action='ipsec').count(),
            'total': queryset.count()
        })

    @action(detail=True, methods=['post'], url_path='regenerate-description')
    def regenerate_description(self, request, pk=None):
        """Regenerate AI description for a policy"""
        policy = self.get_object()
        
        # Generate new description using the model method
        new_description = policy.generate_ai_description()
        policy.ai_description = new_description
        policy.save(update_fields=['ai_description'])
        
        return Response({
            'policy_id': policy.policy_id,
            'ai_description': new_description
        })

    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """FortiGate policy statistics"""
        queryset = self.get_queryset()
        
        return Response({
            'total_policies': queryset.count(),
            'by_action': {
                'accept': queryset.filter(action='accept').count(),
                'deny': queryset.filter(action='deny').count(),
                'ipsec': queryset.filter(action='ipsec').count(),
            },
            'by_status': {
                'enabled': queryset.filter(status='enable').count(),
                'disabled': queryset.filter(status='disable').count(),
            },
            'nat_policies': queryset.filter(nat_enabled=True).count(),
            'utm_policies': queryset.filter(utm_status='enable').count(),
            'by_fortigate': {
                host: queryset.filter(fortigate_host=host).count()
                for host in queryset.values_list('fortigate_host', flat=True).distinct()
            }
        })