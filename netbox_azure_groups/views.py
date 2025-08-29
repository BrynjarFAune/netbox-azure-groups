from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from netbox.views import generic
from utilities.views import ViewTab, register_model_view
from . import filtersets, forms, models, tables


class AzureGroupView(generic.ObjectView):
    queryset = models.AzureGroup.objects.prefetch_related('tags', 'memberships', 'ownerships')

    def get_extra_context(self, request, instance):
        memberships = instance.memberships.select_related('contact', 'device')
        ownerships = instance.ownerships.select_related('contact')
        
        return {
            'memberships': memberships,
            'ownerships': ownerships,
            'total_member_count': memberships.count(),
        }


class AzureGroupListView(generic.ObjectListView):
    queryset = models.AzureGroup.objects.prefetch_related('tags')
    table = tables.AzureGroupTable
    filterset = filtersets.AzureGroupFilterSet
    filterset_form = forms.AzureGroupFilterForm


class AzureGroupEditView(generic.ObjectEditView):
    queryset = models.AzureGroup.objects.all()
    form = forms.AzureGroupForm


class AzureGroupDeleteView(generic.ObjectDeleteView):
    queryset = models.AzureGroup.objects.all()


# Contact Group Membership Views
class ContactGroupMembershipView(generic.ObjectView):
    queryset = models.ContactGroupMembership.objects.select_related('group', 'contact').prefetch_related('tags')

class ContactGroupMembershipEditView(generic.ObjectEditView):
    queryset = models.ContactGroupMembership.objects.all()
    form = forms.ContactGroupMembershipForm

class ContactGroupMembershipDeleteView(generic.ObjectDeleteView):
    queryset = models.ContactGroupMembership.objects.all()

class ContactGroupMembershipChangeLogView(generic.ObjectChangeLogView):
    queryset = models.ContactGroupMembership.objects.all()


# Device Group Membership Views  
class DeviceGroupMembershipView(generic.ObjectView):
    queryset = models.DeviceGroupMembership.objects.select_related('group', 'device').prefetch_related('tags')

class DeviceGroupMembershipEditView(generic.ObjectEditView):
    queryset = models.DeviceGroupMembership.objects.all()
    form = forms.DeviceGroupMembershipForm

class DeviceGroupMembershipDeleteView(generic.ObjectDeleteView):
    queryset = models.DeviceGroupMembership.objects.all()

class DeviceGroupMembershipChangeLogView(generic.ObjectChangeLogView):
    queryset = models.DeviceGroupMembership.objects.all()


# Contact Group Ownership Views
class ContactGroupOwnershipView(generic.ObjectView):
    queryset = models.ContactGroupOwnership.objects.select_related('group', 'contact').prefetch_related('tags')

class ContactGroupOwnershipEditView(generic.ObjectEditView):
    queryset = models.ContactGroupOwnership.objects.all()
    form = forms.ContactGroupOwnershipForm

class ContactGroupOwnershipDeleteView(generic.ObjectDeleteView):
    queryset = models.ContactGroupOwnership.objects.all()

class ContactGroupOwnershipChangeLogView(generic.ObjectChangeLogView):
    queryset = models.ContactGroupOwnership.objects.all()


# Azure Group changelog
class AzureGroupChangeLogView(generic.ObjectChangeLogView):
    queryset = models.AzureGroup.objects.all()


# Register model views
@register_model_view(models.AzureGroup, 'contact_memberships')
class AzureGroupContactMembershipsView(generic.ObjectChildrenView):
    queryset = models.AzureGroup.objects.all()
    child_model = models.ContactGroupMembership
    table = tables.ContactGroupMembershipTable
    filterset = filtersets.ContactGroupMembershipFilterSet
    template_name = 'netbox_azure_groups/azuregroup_contact_memberships.html'
    tab = ViewTab(
        label='Contact Members',
        badge=lambda obj: obj.contact_memberships.count(),
        permission='netbox_azure_groups.view_contactgroupmembership',
        weight=500
    )

@register_model_view(models.AzureGroup, 'device_memberships')  
class AzureGroupDeviceMembershipsView(generic.ObjectChildrenView):
    queryset = models.AzureGroup.objects.all()
    child_model = models.DeviceGroupMembership
    table = tables.DeviceGroupMembershipTable
    filterset = filtersets.DeviceGroupMembershipFilterSet
    template_name = 'netbox_azure_groups/azuregroup_device_memberships.html'
    tab = ViewTab(
        label='Device Members',
        badge=lambda obj: obj.device_memberships.count(),
        permission='netbox_azure_groups.view_devicegroupmembership',
        weight=510
    )

@register_model_view(models.AzureGroup, 'contact_ownerships')
class AzureGroupContactOwnershipsView(generic.ObjectChildrenView):
    queryset = models.AzureGroup.objects.all()
    child_model = models.ContactGroupOwnership
    table = tables.ContactGroupOwnershipTable
    filterset = filtersets.ContactGroupOwnershipFilterSet
    template_name = 'netbox_azure_groups/azuregroup_contact_ownerships.html'
    tab = ViewTab(
        label='Owners',
        badge=lambda obj: obj.contact_ownerships.count(),
        permission='netbox_azure_groups.view_contactgroupownership',
        weight=520
    )