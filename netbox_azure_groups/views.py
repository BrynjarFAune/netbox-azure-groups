from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from netbox.views import generic
from utilities.views import ViewTab, register_model_view
from . import filtersets, forms, models, tables


class AzureGroupView(generic.ObjectView):
    queryset = models.AzureGroup.objects.prefetch_related('tags')

    def get_extra_context(self, request, instance):
        # Get actual memberships and ownerships from related models
        contact_memberships = instance.memberships.filter(contact__isnull=False).select_related('contact')
        device_memberships = instance.memberships.filter(device__isnull=False).select_related('device')
        contact_ownerships = instance.ownerships.all().select_related('contact')
        
        # Calculate actual counts
        total_member_count = contact_memberships.count() + device_memberships.count()
        
        return {
            'total_member_count': total_member_count,
            'total_owner_count': contact_ownerships.count(),
            'contact_memberships': contact_memberships,
            'device_memberships': device_memberships,
            'contact_ownerships': contact_ownerships,
        }


class AzureGroupListView(generic.ObjectListView):
    queryset = models.AzureGroup.objects.annotate(
        total_members=Count('member_count')
    )
    table = tables.AzureGroupTable
    filterset = filtersets.AzureGroupFilterSet
    filterset_form = forms.AzureGroupFilterForm


class AzureGroupDeleteView(generic.ObjectDeleteView):
    queryset = models.AzureGroup.objects.all()


class AzureGroupChangeLogView(generic.ObjectChangeLogView):
    queryset = models.AzureGroup.objects.all()


# ProtectedResource Views

class ProtectedResourceView(generic.ObjectView):
    queryset = models.ProtectedResource.objects.prefetch_related('tags')
    
    def get_extra_context(self, request, instance):
        # Get access control methods and grants for this resource
        access_methods = instance.access_control_methods.all().select_related('azure_group')
        access_grants = instance.access_grants.all().select_related('contact', 'azure_group')
        
        # Get related FortiGate policies through access control methods
        fortigate_policies = models.FortiGatePolicy.objects.filter(
            access_control_method__resource=instance
        )
        
        return {
            'access_methods_count': access_methods.count(),
            'access_grants_count': access_grants.count(),
            'fortigate_policies_count': fortigate_policies.count(),
            'access_methods': access_methods,
            'access_grants': access_grants[:10],  # Show first 10
            'fortigate_policies': fortigate_policies,
        }


class ProtectedResourceListView(generic.ObjectListView):
    queryset = models.ProtectedResource.objects.annotate(
        access_method_count=Count('access_control_methods'),
        grant_count=Count('access_grants')
    )
    table = tables.ProtectedResourceTable
    filterset = filtersets.ProtectedResourceFilterSet
    filterset_form = forms.ProtectedResourceFilterForm


class ProtectedResourceEditView(generic.ObjectEditView):
    queryset = models.ProtectedResource.objects.all()
    form = forms.ProtectedResourceForm


class ProtectedResourceDeleteView(generic.ObjectDeleteView):
    queryset = models.ProtectedResource.objects.all()


class ProtectedResourceChangeLogView(generic.ObjectChangeLogView):
    queryset = models.ProtectedResource.objects.all()