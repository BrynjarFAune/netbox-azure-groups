from netbox.api.routers import NetBoxRouter
from . import viewsets

app_name = 'netbox_azure_groups-api'

router = NetBoxRouter()
router.register('azure-groups', viewsets.AzureGroupViewSet)
router.register('contact-group-memberships', viewsets.ContactGroupMembershipViewSet)
router.register('contact-group-ownerships', viewsets.ContactGroupOwnershipViewSet)
router.register('device-group-memberships', viewsets.DeviceGroupMembershipViewSet)
urlpatterns = router.urls