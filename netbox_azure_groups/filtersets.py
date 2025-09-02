import django_filters
from django_filters import filterset
from .models import AzureGroup, GroupMembership, GroupOwnership, ProtectedResource, AccessControlMethod, FortiGatePolicy, AccessGrant


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


class FortiGatePolicyFilterSet(filterset.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    ai_description = django_filters.CharFilter(
        field_name='ai_description', 
        lookup_expr='icontains',
        label='Description Search'
    )
    fortigate_host = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = FortiGatePolicy
        fields = [
            'policy_id', 'name', 'action', 'status', 'nat_enabled', 
            'utm_status', 'fortigate_host', 'vdom', 'ai_description'
        ]


class AccessGrantFilterSet(filterset.FilterSet):
    contact_name = django_filters.CharFilter(
        field_name='contact__name', 
        lookup_expr='icontains',
        label='Contact Name'
    )
    resource_name = django_filters.CharFilter(
        field_name='resource__name',
        lookup_expr='icontains',
        label='Resource Name'
    )
    azure_group_name = django_filters.CharFilter(
        field_name='azure_group__name',
        lookup_expr='icontains',
        label='Azure Group Name'
    )
    
    class Meta:
        model = AccessGrant
        fields = [
            'resource', 'contact', 'azure_group', 'control_method',
            'access_level', 'granted_via', 'is_active'
        ]