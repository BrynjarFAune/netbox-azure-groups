import logging
from django.contrib.contenttypes.models import ContentType
from netbox.plugins import PluginTemplateExtension
from .models import GroupMembership, GroupOwnership

logger = logging.getLogger(__name__)


class ContactAzureGroupsExtension(PluginTemplateExtension):
    model = 'tenancy.contact'

    def full_width_page(self):
        contact = self.context['object']
        contact_ct = ContentType.objects.get_for_model(contact)
        
        logger.warning(f"ContactAzureGroupsExtension.full_width_page() called for contact {contact.pk} ({contact.name})")
        
        # Get groups this contact is a member of
        memberships = GroupMembership.objects.filter(
            content_type=contact_ct,
            object_id=contact.pk
        ).select_related('group')
        
        # Get groups this contact owns
        ownerships = GroupOwnership.objects.filter(
            content_type=contact_ct,
            object_id=contact.pk
        ).select_related('group')
        
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
        device_ct = ContentType.objects.get_for_model(device)
        
        logger.warning(f"DeviceAzureGroupsExtension.full_width_page() called for device {device.pk} ({device.name})")
        
        # Get groups this device is a member of
        memberships = GroupMembership.objects.filter(
            content_type=device_ct,
            object_id=device.pk
        ).select_related('group')
        
        logger.warning(f"Found {memberships.count()} memberships for device {device.pk}")
        
        return self.render('netbox_azure_groups/inc/device_groups.html', {
            'device': device,
            'group_memberships': memberships,
        })


template_extensions = [ContactAzureGroupsExtension, DeviceAzureGroupsExtension]