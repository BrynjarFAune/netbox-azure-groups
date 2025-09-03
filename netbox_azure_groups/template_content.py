import logging
from netbox.plugins import PluginTemplateExtension
from .models import ProtectedResource, AccessControlMethod

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
        ownerships = contact.owned_azure_groups.select_related('group')
        
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


class AccessControlExtension(PluginTemplateExtension):
    """Base class for access control template extensions"""
    
    def get_access_control_context(self, obj_name, obj_instance):
        """Get access control context for any NetBox object"""
        
        # Find protected resources that might be related to this object
        related_resources = []
        
        # Look for resources with matching names or descriptions
        name_matches = ProtectedResource.objects.filter(name__icontains=obj_name)
        related_resources.extend(name_matches)
        
        # For devices, also check by hostname/FQDN
        if hasattr(obj_instance, 'primary_ip4') and obj_instance.primary_ip4:
            ip_matches = ProtectedResource.objects.filter(base_url__icontains=str(obj_instance.primary_ip4.address.ip))
            related_resources.extend(ip_matches)
        
        # Get access control methods for these resources
        access_methods = []
        for resource in related_resources:
            methods = AccessControlMethod.objects.filter(resource=resource).select_related(
                'azure_group', 'resource'
            )
            access_methods.extend(methods)
        
        return {
            'related_resources': list(set(related_resources)),  # Remove duplicates
            'access_methods': list(set(access_methods)),
            'has_access_control': bool(related_resources or access_methods)
        }


class DeviceAccessControlExtension(AccessControlExtension):
    model = 'dcim.device'

    def right_page(self):
        device = self.context['object']
        
        from dcim.models import Device
        if not isinstance(device, Device):
            return ""
        
        context = self.get_access_control_context(device.name, device)
        context['device'] = device
        
        return self.render('netbox_azure_groups/inc/access_control_tab.html', context)


class VirtualMachineAccessControlExtension(AccessControlExtension):
    model = 'virtualization.virtualmachine'

    def right_page(self):
        vm = self.context['object']
        
        from virtualization.models import VirtualMachine
        if not isinstance(vm, VirtualMachine):
            return ""
        
        context = self.get_access_control_context(vm.name, vm)
        context['vm'] = vm
        
        return self.render('netbox_azure_groups/inc/access_control_tab.html', context)


class SiteAccessControlExtension(AccessControlExtension):
    model = 'dcim.site'

    def right_page(self):
        site = self.context['object']
        
        from dcim.models import Site
        if not isinstance(site, Site):
            return ""
        
        context = self.get_access_control_context(site.name, site)
        context['site'] = site
        
        return self.render('netbox_azure_groups/inc/access_control_tab.html', context)


class ServiceAccessControlExtension(AccessControlExtension):
    model = 'ipam.service'

    def right_page(self):
        service = self.context['object']
        
        # Import check for Service model
        try:
            from ipam.models import Service
            if not isinstance(service, Service):
                return ""
        except ImportError:
            # Service model may not exist in this NetBox version
            return ""
        
        context = self.get_access_control_context(service.name, service)
        context['service'] = service
        
        return self.render('netbox_azure_groups/inc/access_control_tab.html', context)


class ContactAccessControlExtension(PluginTemplateExtension):
    model = 'tenancy.contact'
    
    def right_page(self):
        contact = self.context['object']
        
        from tenancy.models import Contact
        if not isinstance(contact, Contact):
            return ""
        
        # Get all access grants for this contact
        access_grants = AccessGrant.objects.filter(
            contact=contact
        ).select_related(
            'resource', 'azure_group', 'control_method'
        )
        
        # Get access control methods available through groups
        group_memberships = contact.azure_group_memberships.select_related('group')
        azure_groups = [m.group for m in group_memberships]
        
        potential_methods = AccessControlMethod.objects.filter(
            azure_group__in=azure_groups, 
            is_active=True
        ).select_related('resource', 'azure_group')
        
        return self.render('netbox_azure_groups/inc/contact_access_control.html', {
            'contact': contact,
            'access_grants': access_grants,
            'potential_methods': potential_methods,
            'has_access': access_grants.exists() or potential_methods.exists()
        })


# Re-enable template extensions with new direct ForeignKey models + access control extensions
template_extensions = [
    ContactAzureGroupsExtension, 
    ContactAccessControlExtension,
    DeviceAzureGroupsExtension,
    DeviceAccessControlExtension,
    VirtualMachineAccessControlExtension, 
    SiteAccessControlExtension,
    ServiceAccessControlExtension
]