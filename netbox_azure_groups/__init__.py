from netbox.plugins import PluginConfig

class AzureGroupsConfig(PluginConfig):
    name = 'netbox_azure_groups'
    verbose_name = 'Azure AD Groups'
    description = 'Manage Azure AD groups and memberships in NetBox'
    version = '0.1.0'
    author = 'Brynjar F. Aune'
    author_email = 'brynjar.aune@example.com'
    base_url = 'azure-groups'
    required_settings = []
    default_settings = {}
    caching_config = {}

config = AzureGroupsConfig