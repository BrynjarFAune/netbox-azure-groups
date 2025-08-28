# Temporarily simplified imports during refactoring 
from .azure_groups import AzureGroup, GroupTypeChoices

# Temporary dummy classes to prevent import errors during refactoring
# These will be replaced with the proper refactored models
class GroupMembership:
    """Temporary dummy class - DO NOT USE"""
    _meta = type('Meta', (), {'get_field': lambda self, name: type('Field', (), {'choices': []})()})()
    
class GroupOwnership:
    """Temporary dummy class - DO NOT USE"""
    _meta = type('Meta', (), {'get_field': lambda self, name: type('Field', (), {'choices': []})()})()

__all__ = ['AzureGroup', 'GroupTypeChoices', 'GroupMembership', 'GroupOwnership']

# TODO: Complete the refactoring of these models
# from .azure_groups import ContactGroupMembership, ContactGroupOwnership, DeviceGroupMembership