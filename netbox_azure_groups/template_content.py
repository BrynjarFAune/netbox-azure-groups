from django.contrib.contenttypes.models import ContentType
from netbox.plugins import PluginTemplateExtension
from .models import GroupMembership, GroupOwnership


class ContactAzureGroupsExtension(PluginTemplateExtension):
    model = 'tenancy.contact'

    def full_width_page(self):
        contact = self.context['object']
        contact_ct = ContentType.objects.get_for_model(contact)
        
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
        
        # Get groups this device is a member of
        memberships = GroupMembership.objects.filter(
            content_type=device_ct,
            object_id=device.pk
        ).select_related('group')
        
        return self.render('netbox_azure_groups/inc/device_groups.html', {
            'device': device,
            'group_memberships': memberships,
        })


# Temporarily disable to eliminate duplicate auto-display
template_extensions = []
# template_extensions = [ContactAzureGroupsExtension, DeviceAzureGroupsExtension]