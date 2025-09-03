from netbox.api.routers import NetBoxRouter
from . import viewsets

app_name = 'netbox_azure_groups-api'

router = NetBoxRouter()
# Azure Groups (existing)
router.register('azure-groups', viewsets.AzureGroupViewSet)
router.register('group-memberships', viewsets.GroupMembershipViewSet)
router.register('group-ownerships', viewsets.GroupOwnershipViewSet)

# Access Control (new)
router.register('business-units', viewsets.BusinessUnitViewSet)
router.register('business-unit-memberships', viewsets.BusinessUnitMembershipViewSet)
router.register('protected-resources', viewsets.ProtectedResourceViewSet)
router.register('access-control-methods', viewsets.AccessControlMethodViewSet)
router.register('access-grants', viewsets.AccessGrantViewSet)

# FortiGate Integration
router.register('fortigate-policies', viewsets.FortiGatePolicyViewSet)

urlpatterns = router.urls