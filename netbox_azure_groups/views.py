from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.shortcuts import render
from django.views.generic import View
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


# BusinessUnit Views

class BusinessUnitView(generic.ObjectView):
    queryset = models.BusinessUnit.objects.prefetch_related('tags')
    
    def get_extra_context(self, request, instance):
        # Get child business units
        child_units = instance.children.filter(is_active=True)
        
        # Get protected resources using this business unit
        protected_resources = instance.resources.all()
        
        # Get access control methods for resources in this business unit
        access_methods = models.AccessControlMethod.objects.filter(
            resource__business_unit=instance,
            is_active=True
        ).select_related('azure_group', 'resource')
        
        # Get active access grants for resources in this business unit
        access_grants = models.AccessGrant.objects.filter(
            resource__business_unit=instance,
            is_active=True
        ).select_related('contact', 'azure_group', 'resource')
        
        # Get Azure groups that provide access to resources in this business unit
        related_azure_groups = models.AzureGroup.objects.filter(
            enables_access_via__resource__business_unit=instance
        ).distinct()
        
        # Get business unit memberships (direct)
        direct_memberships = models.BusinessUnitMembership.objects.filter(
            business_unit=instance,
            is_active=True
        ).select_related('contact').order_by('role', 'contact__name')
        
        # Get inferred memberships from child business units
        child_business_units = self._get_all_descendants(instance)
        inferred_memberships = models.BusinessUnitMembership.objects.filter(
            business_unit__in=child_business_units,
            is_active=True
        ).select_related('contact', 'business_unit').order_by('business_unit__name', 'role', 'contact__name')
        
        # Combine memberships with type annotation
        all_memberships = []
        for membership in direct_memberships:
            membership.membership_type = 'direct'
            all_memberships.append(membership)
        
        for membership in inferred_memberships:
            membership.membership_type = 'inferred'
            all_memberships.append(membership)
        
        return {
            'child_units': child_units,
            'child_units_count': child_units.count(),
            'protected_resources': protected_resources[:10],  # Show first 10 in template
            'protected_resources_count': protected_resources.count(),
            'access_methods_count': access_methods.count(),
            'access_grants_count': access_grants.count(),
            'related_azure_groups': related_azure_groups[:12],  # Show first 12 in template
            'memberships': all_memberships[:20],  # Show first 20 members (direct + inferred)
            'direct_memberships': direct_memberships[:10],  # For direct display section
            'inferred_memberships': inferred_memberships[:10],  # For inferred display section
            'direct_memberships_count': direct_memberships.count(),
            'inferred_memberships_count': inferred_memberships.count(),
            'total_memberships_count': len(all_memberships),
        }
    
    def _get_all_descendants(self, business_unit):
        """Recursively get all descendant business units."""
        descendants = []
        direct_children = models.BusinessUnit.objects.filter(parent=business_unit, is_active=True)
        
        for child in direct_children:
            descendants.append(child)
            descendants.extend(self._get_all_descendants(child))
        
        return descendants


class BusinessUnitListView(generic.ObjectListView):
    queryset = models.BusinessUnit.objects.annotate(
        child_count=Count('children'),
        resource_count=Count('resources')
    ).select_related('parent', 'contact')
    table = tables.BusinessUnitTable
    filterset = filtersets.BusinessUnitFilterSet
    filterset_form = forms.BusinessUnitFilterForm


class BusinessUnitEditView(generic.ObjectEditView):
    queryset = models.BusinessUnit.objects.all()
    form = forms.BusinessUnitForm


class BusinessUnitDeleteView(generic.ObjectDeleteView):
    queryset = models.BusinessUnit.objects.all()


class BusinessUnitChangeLogView(generic.ObjectChangeLogView):
    queryset = models.BusinessUnit.objects.all()


# BusinessUnitMembership Views

class BusinessUnitMembershipView(generic.ObjectView):
    queryset = models.BusinessUnitMembership.objects.select_related('business_unit', 'contact')


class BusinessUnitMembershipListView(generic.ObjectListView):
    queryset = models.BusinessUnitMembership.objects.select_related('business_unit', 'contact')
    table = tables.BusinessUnitMembershipTable
    filterset = filtersets.BusinessUnitMembershipFilterSet
    filterset_form = forms.BusinessUnitMembershipFilterForm


class BusinessUnitMembershipEditView(generic.ObjectEditView):
    queryset = models.BusinessUnitMembership.objects.all()
    form = forms.BusinessUnitMembershipForm


class BusinessUnitMembershipDeleteView(generic.ObjectDeleteView):
    queryset = models.BusinessUnitMembership.objects.all()


class BusinessUnitMembershipChangeLogView(generic.ObjectChangeLogView):
    queryset = models.BusinessUnitMembership.objects.all()


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
    queryset = models.FortiGatePolicy.objects.annotate(
        groups_count=Count(
            'access_control_method__azure_group',
            distinct=True,
            filter=Q(access_control_method__control_type='fortigate_policy')
        )
    )
    table = tables.FortiGatePolicyTable
    filterset = filtersets.FortiGatePolicyFilterSet
    filterset_form = forms.FortiGatePolicyFilterForm
    template_name = 'netbox_azure_groups/fortigatepolicy_list.html'


class FortiGatePolicyChangeLogView(generic.ObjectChangeLogView):
    queryset = models.FortiGatePolicy.objects.all()


# Access Grant Views

class AccessGrantView(generic.ObjectView):
    queryset = models.AccessGrant.objects.select_related(
        'resource', 'contact', 'azure_group', 'control_method'
    ).prefetch_related('tags')
    
    def get_extra_context(self, request, instance):
        # Get FortiGate policy details if applicable
        fortigate_policy = None
        if instance.control_method.control_type == 'fortigate_policy':
            policy_id = instance.control_method.configuration.get('policy_id')
            if policy_id:
                try:
                    fortigate_policy = models.FortiGatePolicy.objects.get(policy_id=policy_id)
                except models.FortiGatePolicy.DoesNotExist:
                    pass
        
        # Get other grants for the same resource
        related_grants = models.AccessGrant.objects.filter(
            resource=instance.resource
        ).exclude(pk=instance.pk).select_related('contact', 'azure_group')[:10]
        
        return {
            'fortigate_policy': fortigate_policy,
            'related_grants': related_grants,
            'related_grants_count': models.AccessGrant.objects.filter(
                resource=instance.resource
            ).exclude(pk=instance.pk).count(),
        }


class AccessGrantListView(generic.ObjectListView):
    queryset = models.AccessGrant.objects.select_related(
        'resource', 'contact', 'azure_group', 'control_method'
    )
    table = tables.AccessGrantTable
    filterset = filtersets.AccessGrantFilterSet
    filterset_form = forms.AccessGrantFilterForm
    template_name = 'netbox_azure_groups/accessgrant_list.html'


class AccessGrantEditView(generic.ObjectEditView):
    queryset = models.AccessGrant.objects.all()
    form = forms.AccessGrantForm


class AccessGrantDeleteView(generic.ObjectDeleteView):
    queryset = models.AccessGrant.objects.all()


class AccessGrantChangeLogView(generic.ObjectChangeLogView):
    queryset = models.AccessGrant.objects.all()


# Dashboard Views

class AccessControlDashboardView(View):
    """Dashboard showing comprehensive access control metrics and insights."""
    template_name = 'netbox_azure_groups/dashboard.html'
    
    def get(self, request):
        # Get comprehensive statistics
        stats = self._get_dashboard_stats()
        
        # Get recent activity
        recent_grants = models.AccessGrant.objects.select_related(
            'resource', 'contact', 'azure_group'
        ).order_by('-first_granted')[:10]
        
        recent_resources = models.ProtectedResource.objects.order_by('-created')[:5]
        recent_methods = models.AccessControlMethod.objects.select_related(
            'resource', 'azure_group'
        ).order_by('-created')[:5]
        
        # Get top resources by grant count
        from django.db.models import Count
        top_resources = models.ProtectedResource.objects.annotate(
            grant_count=Count('access_grants')
        ).filter(grant_count__gt=0).order_by('-grant_count')[:10]
        
        # Get top Azure groups by grant count
        top_groups = models.AzureGroup.objects.annotate(
            grant_count=Count('access_grants')
        ).filter(grant_count__gt=0).order_by('-grant_count')[:10]
        
        # Get resource type distribution
        resource_types = models.ProtectedResource.objects.values(
            'resource_type'
        ).annotate(count=Count('id')).order_by('-count')
        
        # Get control method types distribution
        control_types = models.AccessControlMethod.objects.values(
            'control_type'
        ).annotate(count=Count('id')).order_by('-count')
        
        context = {
            'stats': stats,
            'recent_grants': recent_grants,
            'recent_resources': recent_resources,
            'recent_methods': recent_methods,
            'top_resources': top_resources,
            'top_groups': top_groups,
            'resource_types': resource_types,
            'control_types': control_types,
        }
        
        return render(request, self.template_name, context)
    
    def _get_dashboard_stats(self):
        """Calculate comprehensive dashboard statistics."""
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        # Basic counts
        total_resources = models.ProtectedResource.objects.count()
        total_methods = models.AccessControlMethod.objects.count()
        total_grants = models.AccessGrant.objects.count()
        total_groups = models.AzureGroup.objects.count()
        total_policies = models.FortiGatePolicy.objects.count()
        
        # Active/inactive counts
        active_resources = models.ProtectedResource.objects.filter(is_active=True).count()
        active_methods = models.AccessControlMethod.objects.filter(is_active=True).count()
        active_grants = models.AccessGrant.objects.filter(is_active=True).count()
        
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_grants = models.AccessGrant.objects.filter(
            first_granted__gte=thirty_days_ago
        ).count()
        
        # Resource type breakdown
        resource_critical = models.ProtectedResource.objects.filter(
            criticality='critical'
        ).count()
        resource_high = models.ProtectedResource.objects.filter(
            criticality='high'
        ).count()
        
        # Control method types
        fortigate_methods = models.AccessControlMethod.objects.filter(
            control_type='fortigate_policy'
        ).count()
        azure_ca_methods = models.AccessControlMethod.objects.filter(
            control_type='azure_conditional_access'
        ).count()
        
        # Grant distribution
        direct_grants = models.AccessGrant.objects.filter(
            granted_via='direct_membership'
        ).count()
        nested_grants = models.AccessGrant.objects.filter(
            granted_via='nested_group'
        ).count()
        
        # Coverage metrics
        resources_with_grants = models.ProtectedResource.objects.annotate(
            grant_count=Count('access_grants')
        ).filter(grant_count__gt=0).count()
        
        coverage_percentage = (
            (resources_with_grants / total_resources * 100) 
            if total_resources > 0 else 0
        )
        
        return {
            # Basic counts
            'total_resources': total_resources,
            'total_methods': total_methods,
            'total_grants': total_grants,
            'total_groups': total_groups,
            'total_policies': total_policies,
            
            # Active counts
            'active_resources': active_resources,
            'active_methods': active_methods,
            'active_grants': active_grants,
            
            # Recent activity
            'recent_grants': recent_grants,
            
            # Resource breakdown
            'resource_critical': resource_critical,
            'resource_high': resource_high,
            
            # Method types
            'fortigate_methods': fortigate_methods,
            'azure_ca_methods': azure_ca_methods,
            
            # Grant types
            'direct_grants': direct_grants,
            'nested_grants': nested_grants,
            
            # Coverage
            'resources_with_grants': resources_with_grants,
            'coverage_percentage': round(coverage_percentage, 1),
        }