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