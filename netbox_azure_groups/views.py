from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from netbox.views import generic
from utilities.views import ViewTab, register_model_view
from . import filtersets, forms, models, tables


class AzureGroupView(generic.ObjectView):
    queryset = models.AzureGroup.objects.prefetch_related('tags', 'memberships')

    def get_extra_context(self, request, instance):
        memberships = instance.memberships.select_related('content_type')
        return {
            'memberships': memberships,
            'member_count': memberships.count(),
        }


class AzureGroupListView(generic.ObjectListView):
    queryset = models.AzureGroup.objects.prefetch_related('tags').annotate(
        member_count=Count('memberships')
    )
    table = tables.AzureGroupTable
    filterset = filtersets.AzureGroupFilterSet
    filterset_form = forms.AzureGroupFilterForm


class AzureGroupEditView(generic.ObjectEditView):
    queryset = models.AzureGroup.objects.all()
    form = forms.AzureGroupForm


class AzureGroupDeleteView(generic.ObjectDeleteView):
    queryset = models.AzureGroup.objects.all()


class GroupMembershipView(generic.ObjectView):
    queryset = models.GroupMembership.objects.select_related('group', 'content_type').prefetch_related('tags')


# GroupMembershipListView removed - use group detail pages instead


class GroupMembershipEditView(generic.ObjectEditView):
    queryset = models.GroupMembership.objects.all()
    form = forms.GroupMembershipForm


class GroupMembershipDeleteView(generic.ObjectDeleteView):
    queryset = models.GroupMembership.objects.all()


class AzureGroupChangeLogView(generic.ObjectChangeLogView):
    queryset = models.AzureGroup.objects.all()


class GroupMembershipChangeLogView(generic.ObjectChangeLogView):
    queryset = models.GroupMembership.objects.all()


class GroupOwnershipView(generic.ObjectView):
    queryset = models.GroupOwnership.objects.select_related('group', 'content_type').prefetch_related('tags')


# GroupOwnershipListView removed - use group detail pages instead


class GroupOwnershipEditView(generic.ObjectEditView):
    queryset = models.GroupOwnership.objects.all()
    form = forms.GroupOwnershipForm


class GroupOwnershipDeleteView(generic.ObjectDeleteView):
    queryset = models.GroupOwnership.objects.all()


class GroupOwnershipChangeLogView(generic.ObjectChangeLogView):
    queryset = models.GroupOwnership.objects.all()


# Register model views
@register_model_view(models.AzureGroup, 'memberships')
class AzureGroupMembershipsView(generic.ObjectChildrenView):
    queryset = models.AzureGroup.objects.all()
    child_model = models.GroupMembership
    table = tables.GroupMembershipTable
    filterset = filtersets.GroupMembershipFilterSet
    template_name = 'netbox_azure_groups/azuregroup_memberships.html'
    tab = ViewTab(
        label='Memberships',
        badge=lambda obj: obj.memberships.count(),
        permission='netbox_azure_groups.view_groupmembership',
        weight=500
    )