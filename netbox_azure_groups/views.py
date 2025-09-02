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
        access_methods = instance.access_methods.all().select_related('azure_group')
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
        access_method_count=Count('access_methods'),
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


# AccessControlMethod Views

class AccessControlMethodView(generic.ObjectView):
    queryset = models.AccessControlMethod.objects.prefetch_related('tags')
    
    def get_extra_context(self, request, instance):
        # Get related FortiGate policy if this is a firewall policy control method
        fortigate_policy = None
        if instance.control_type == 'fortigate_policy':
            try:
                policy_id = instance.configuration.get('policy_id')
                if policy_id:
                    fortigate_policy = models.FortiGatePolicy.objects.get(policy_id=policy_id)
            except (models.FortiGatePolicy.DoesNotExist, KeyError):
                pass
        
        # Get access grants through this method
        access_grants = instance.access_grants.all().select_related('contact')
        
        return {
            'fortigate_policy': fortigate_policy,
            'access_grants_count': access_grants.count(),
            'access_grants': access_grants[:10],  # Show first 10
        }


class AccessControlMethodListView(generic.ObjectListView):
    queryset = models.AccessControlMethod.objects.select_related('resource', 'azure_group').annotate(
        grant_count=Count('access_grants')
    )
    table = tables.AccessControlMethodTable
    filterset = filtersets.AccessControlMethodFilterSet
    filterset_form = forms.AccessControlMethodFilterForm


class AccessControlMethodEditView(generic.ObjectEditView):
    queryset = models.AccessControlMethod.objects.all()
    form = forms.AccessControlMethodForm


class AccessControlMethodDeleteView(generic.ObjectDeleteView):
    queryset = models.AccessControlMethod.objects.all()


class AccessControlMethodChangeLogView(generic.ObjectChangeLogView):
    queryset = models.AccessControlMethod.objects.all()


# FortiGate Policy Views

class FortiGatePolicyView(generic.ObjectView):
    queryset = models.FortiGatePolicy.objects.prefetch_related('tags')
    
    def get_extra_context(self, request, instance):
        # Get access control methods using this policy
        access_methods = models.AccessControlMethod.objects.filter(
            control_type='fortigate_policy',
            configuration__policy_id=instance.policy_id
        ).select_related('resource', 'azure_group')
        
        # Get resources this policy protects (through access methods)
        protected_resources = models.ProtectedResource.objects.filter(
            access_methods__in=access_methods
        ).distinct()
        
        return {
            'access_methods': access_methods,
            'access_methods_count': access_methods.count(),
            'protected_resources': protected_resources,
            'protected_resources_count': protected_resources.count(),
        }


class FortiGatePolicyListView(generic.ObjectListView):
    queryset = models.FortiGatePolicy.objects.all()
    table = tables.FortiGatePolicyTable
    filterset = filtersets.FortiGatePolicyFilterSet
    filterset_form = forms.FortiGatePolicyFilterForm
    template_name = 'netbox_azure_groups/fortigatepolicy_list.html'


class FortiGatePolicyChangeLogView(generic.ObjectChangeLogView):
    queryset = models.FortiGatePolicy.objects.all()