# Temporarily simplified imports during refactoring 
from .azure_groups import AzureGroup, GroupTypeChoices
from netbox.models import NetBoxModel
from django.db import models

# Temporary dummy classes to prevent import errors during refactoring
# These will be replaced with the proper refactored models
class GroupMembership(NetBoxModel):
    """Temporary dummy class - DO NOT USE"""
    group = models.ForeignKey(AzureGroup, on_delete=models.CASCADE, related_name='memberships')
    member_type = models.CharField(max_length=20, choices=[('direct', 'Direct')])
    
    class Meta:
        managed = False
        db_table = 'netbox_azure_groups_groupmembership_temp'
    
class GroupOwnership(NetBoxModel):
    """Temporary dummy class - DO NOT USE"""
    group = models.ForeignKey(AzureGroup, on_delete=models.CASCADE, related_name='ownerships')
    
    class Meta:
        managed = False
        db_table = 'netbox_azure_groups_groupownership_temp'

__all__ = ['AzureGroup', 'GroupTypeChoices', 'GroupMembership', 'GroupOwnership']

# TODO: Complete the refactoring of these models
# from .azure_groups import ContactGroupMembership, ContactGroupOwnership, DeviceGroupMembership