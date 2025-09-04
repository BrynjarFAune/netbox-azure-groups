# NetBox Access Control Plugin

A comprehensive NetBox plugin for access control management with Azure AD integration and FortiGate policy support.

## Features

### Core Functionality
- **Azure AD Groups**: Import and manage Azure Active Directory groups with full metadata
- **Business Units**: Hierarchical organizational structure with inherited memberships
- **Protected Resources**: Catalog of resources requiring access control
- **Access Control Methods**: Define how access is granted (FortiGate policies, badge readers, etc.)
- **Access Grants**: Track who has access to what resources and how

### FortiGate Integration
- Import and display FortiGate firewall policies
- AI-generated policy descriptions for better understanding
- Link policies to access control methods
- Usage tracking and statistics

### Business Unit Management
- Hierarchical department structure
- Direct and inferred memberships (members from child units)
- Role-based membership (Member, Manager, Admin, Contributor, Viewer)
- Contact integration with NetBox tenancy

### Advanced Features
- Comprehensive dashboard with statistics and quick actions
- API endpoints for all models
- Filtering and search across all views
- Responsive web interface with accessibility focus

## Installation

### Requirements
- NetBox 4.0+ 
- Python 3.10+
- Django 4.2+

### Install Plugin
```bash
pip install netbox-azure-groups
```

### NetBox Configuration
Add to your NetBox `configuration.py`:
```python
PLUGINS = ['netbox_azure_groups']

PLUGINS_CONFIG = {
    'netbox_azure_groups': {
        'allow_manual_creation': False,
        'stale_threshold_hours': 24,
        'soft_delete_retention_days': 30,
        'max_members_display': 100,
        'enforce_source_restrictions': True,
        'show_sync_status': True,
        'enable_nested_membership': True,
        'auto_calculate_counts': True,
    }
}
```

### Apply Database Migrations
```bash
python manage.py migrate netbox_azure_groups
```

## Usage

### Access the Plugin
Navigate to **Plugins** → **Access Control** in your NetBox interface.

### Dashboard
The main dashboard provides:
- System overview statistics
- Resource type breakdown
- Recent activity
- Quick action buttons

### Managing Business Units
1. Create business units representing your organizational structure
2. Set up parent-child relationships for hierarchy
3. Assign contacts as members with appropriate roles
4. View both direct and inferred memberships

### Protected Resources
1. Catalog resources that need access control
2. Define resource types, criticality levels, and ownership
3. Link resources to business units
4. Associate with NetBox sites and locations
5. Configure actual IP addresses/hostnames for resources as needed

### Access Control Methods
1. Define how access is granted (policies, physical controls, etc.)
2. Link Azure AD groups to specific resources
3. Configure access levels and technical details
4. Track verification dates

### FortiGate Integration  
1. Import policies using the FortiGate import tools
2. Browse policies with AI-generated descriptions
3. Link policies to access control methods
4. Monitor policy usage statistics

## API

All models are available via REST API:
- `/api/plugins/netbox-azure-groups/business-units/`
- `/api/plugins/netbox-azure-groups/protected-resources/`
- `/api/plugins/netbox-azure-groups/access-control-methods/`
- `/api/plugins/netbox-azure-groups/access-grants/`
- `/api/plugins/netbox-azure-groups/azure-groups/`
- `/api/plugins/netbox-azure-groups/fortigate-policies/`

## Development

### Running Tests
```bash
python manage.py test netbox_azure_groups
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

Licensed under the Apache License, Version 2.0. See LICENSE file for details.