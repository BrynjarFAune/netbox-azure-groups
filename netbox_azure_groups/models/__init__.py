# Import all models from azure_groups module
from .azure_groups import (
    AzureGroup,
    GroupMembership,
    GroupOwnership,
    GroupTypeChoices,
    GroupSourceChoices,
    MembershipTypeChoices,
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
    # Legacy aliases
    'ContactGroupMembership',
    'ContactGroupOwnership', 
    'DeviceGroupMembership',
]