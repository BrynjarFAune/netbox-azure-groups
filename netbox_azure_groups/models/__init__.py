# Import all models from azure_groups module
from .azure_groups import (
    AzureGroup,
    GroupMembership,
    GroupOwnership,
    GroupTypeChoices,
    GroupSourceChoices,
    MembershipTypeChoices,
    # Access Control Extension Models
    ProtectedResource,
    AccessControlMethod,
    AccessGrant,
    ResourceTypeChoices,
    CriticalityChoices,
    ControlTypeChoices,
    AccessLevelChoices,
    GrantedViaChoices,
)

# Backward compatibility aliases for old model names
# TODO: Remove these aliases after updating all references
ContactGroupMembership = GroupMembership
ContactGroupOwnership = GroupOwnership
DeviceGroupMembership = GroupMembership

__all__ = [
    'AzureGroup',
    'GroupMembership',
    'GroupOwnership',
    'GroupTypeChoices',
    'GroupSourceChoices',
    'MembershipTypeChoices',
    # Access Control Extension Models
    'ProtectedResource',
    'AccessControlMethod',
    'AccessGrant',
    'ResourceTypeChoices',
    'CriticalityChoices',
    'ControlTypeChoices',
    'AccessLevelChoices',
    'GrantedViaChoices',
    # Legacy aliases
    'ContactGroupMembership',
    'ContactGroupOwnership', 
    'DeviceGroupMembership',
]