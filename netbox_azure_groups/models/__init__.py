# Temporarily simplified imports during refactoring 
from .azure_groups import AzureGroup, GroupTypeChoices

__all__ = ['AzureGroup', 'GroupTypeChoices']

# TODO: Complete the refactoring of these models
# from .azure_groups import ContactGroupMembership, ContactGroupOwnership, DeviceGroupMembership