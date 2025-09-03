from netbox.plugins import PluginConfig

class AccessControlConfig(PluginConfig):
    name = 'netbox_azure_groups'  # Must match Python module name
    verbose_name = 'Access Control'
    description = 'Comprehensive access control management with FortiGate integration and Azure AD groups'
    version = '1.0.0'
    author = 'Brynjar F. Aune'
    author_email = 'brynjar.aune@example.com'
    base_url = 'access-control'
    required_settings = []
    
    # Plugin-specific settings
    default_settings = {
        'allow_manual_creation': False,  # Prevent UI group creation in production
        'stale_threshold_hours': 24,     # When to show stale warnings
        'soft_delete_retention_days': 30,  # Audit trail retention
        'max_members_display': 100,       # UI pagination limit
        'enforce_source_restrictions': True,  # Enforce read-only for on-premises groups
        'show_sync_status': True,        # Display sync status badges in UI
        'enable_nested_membership': True, # Support nested group membership tracking
        'auto_calculate_counts': True,   # Automatically update member/owner counts
    }
    
    # Cache settings for performance
    caching_config = {
        'timeout': 300,  # 5 minutes
        'cache_key': 'netbox_azure_groups',
    }

config = AccessControlConfig