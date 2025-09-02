import django_filters
from django_filters import filterset
from .models import AzureGroup, GroupMembership, GroupOwnership, ProtectedResource, AccessControlMethod


# Minimal filtersets for migration purposes only
class AzureGroupFilterSet(filterset.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = AzureGroup
        fields = ['name', 'object_id', 'group_type', 'source']


class GroupMembershipFilterSet(filterset.FilterSet):
    class Meta:
        model = GroupMembership
        fields = ['group']


class GroupOwnershipFilterSet(filterset.FilterSet):
    class Meta:
        model = GroupOwnership
        fields = ['group']


# Legacy aliases for backward compatibility with views
ContactGroupMembershipFilterSet = GroupMembershipFilterSet
DeviceGroupMembershipFilterSet = GroupMembershipFilterSet  
ContactGroupOwnershipFilterSet = GroupOwnershipFilterSet


class ProtectedResourceFilterSet(filterset.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    business_unit = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = ProtectedResource
        fields = [
            'name', 'resource_type', 'criticality', 
            'business_unit', 'is_active', 'owner_contact'
        ]


class AccessControlMethodFilterSet(filterset.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    resource = django_filters.ModelChoiceFilter(queryset=ProtectedResource.objects.all())
    azure_group = django_filters.ModelChoiceFilter(queryset=AzureGroup.objects.all())
    
    class Meta:
        model = AccessControlMethod
        fields = [
            'name', 'resource', 'control_type', 'azure_group',
            'access_level', 'is_active'
        ]