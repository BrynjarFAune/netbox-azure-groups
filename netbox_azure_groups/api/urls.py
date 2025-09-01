from netbox.api.routers import NetBoxRouter
from . import viewsets

app_name = 'netbox_azure_groups-api'

router = NetBoxRouter()
router.register('azure-groups', viewsets.AzureGroupViewSet)
router.register('group-memberships', viewsets.GroupMembershipViewSet)
router.register('group-ownerships', viewsets.GroupOwnershipViewSet)
urlpatterns = router.urls