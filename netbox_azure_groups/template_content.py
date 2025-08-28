import logging
from netbox.plugins import PluginTemplateExtension
# Temporarily disabled during refactoring
# from .models import ContactGroupMembership, ContactGroupOwnership, DeviceGroupMembership

logger = logging.getLogger(__name__)


class ContactAzureGroupsExtension(PluginTemplateExtension):
    model = 'tenancy.contact'

    def full_width_page(self):
        contact = self.context['object']
        
        # Validate this is actually a Contact object, not a Device
        from tenancy.models import Contact
        if not isinstance(contact, Contact):
            logger.warning(f"ContactAzureGroupsExtension called on non-contact: {type(contact).__name__} {contact.pk} ({contact.name}) - SKIPPING")
            return ""
        
        logger.warning(f"ContactAzureGroupsExtension.full_width_page() called for contact {contact.pk} ({contact.name})")
        
        # Get groups this contact is a member of (direct ForeignKey relationship)
        memberships = contact.azure_group_memberships.select_related('group')
        
        # Get groups this contact owns (direct ForeignKey relationship)
        ownerships = contact.azure_group_ownerships.select_related('group')
        
        logger.warning(f"Found {memberships.count()} memberships and {ownerships.count()} ownerships for contact {contact.pk}")
        
        return self.render('netbox_azure_groups/inc/contact_groups.html', {
            'contact': contact,
            'group_memberships': memberships,
            'group_ownerships': ownerships,
        })


class DeviceAzureGroupsExtension(PluginTemplateExtension):
    model = 'dcim.device'

    def full_width_page(self):
        device = self.context['object']
        
        # Validate this is actually a Device object, not a Contact
        from dcim.models import Device
        if not isinstance(device, Device):
            logger.warning(f"DeviceAzureGroupsExtension called on non-device: {type(device).__name__} {device.pk} ({device.name}) - SKIPPING")
            return ""
        
        logger.warning(f"DeviceAzureGroupsExtension.full_width_page() called for device {device.pk} ({device.name})")
        
        # Get groups this device is a member of (direct ForeignKey relationship)
        memberships = device.azure_group_memberships.select_related('group')
        
        logger.warning(f"Found {memberships.count()} memberships for device {device.pk}")
        
        return self.render('netbox_azure_groups/inc/device_groups.html', {
            'device': device,
            'group_memberships': memberships,
        })


# Temporarily disable template extensions during refactoring
template_extensions = []
# template_extensions = [ContactAzureGroupsExtension, DeviceAzureGroupsExtension]