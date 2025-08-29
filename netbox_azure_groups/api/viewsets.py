from netbox.api.viewsets import NetBoxModelViewSet
from ..models import AzureGroup
from .serializers import AzureGroupSerializer


class AzureGroupViewSet(NetBoxModelViewSet):
    queryset = AzureGroup.objects.all()
    serializer_class = AzureGroupSerializer
    filterset_fields = [
        'name', 'object_id', 'group_type', 'is_security_enabled', 'is_mail_enabled'
    ]