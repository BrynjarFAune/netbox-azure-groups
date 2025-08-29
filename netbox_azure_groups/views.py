from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from netbox.views import generic
from utilities.views import ViewTab, register_model_view
from . import filtersets, forms, models, tables


class AzureGroupView(generic.ObjectView):
    queryset = models.AzureGroup.objects.prefetch_related('tags')

    def get_extra_context(self, request, instance):
        return {
            'total_member_count': instance.member_count,
            'total_owner_count': instance.owner_count,
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