# NetBox Azure AD Groups Plugin

A NetBox plugin for managing Azure Active Directory groups and their memberships with NetBox contacts and devices.

## Features

- **Azure AD Group Management**: Track Azure AD security groups with metadata
- **Multi-Entity Memberships**: Support for both contacts and devices in groups
- **Many-to-Many Relations**: Entities can belong to multiple groups
- **REST API**: Full API support for automation and sync tools
- **Web Interface**: NetBox-integrated UI for group management
- **Microsoft Graph Compatible**: Data structure compatible with Microsoft Graph API

## Installation

1. Install the plugin:
```bash
pip install netbox-azure-groups
```

2. Add to NetBox configuration:
```python
# configuration.py
PLUGINS = [
    'netbox_azure_groups',
]
```

3. Run migrations:
```bash
python manage.py migrate
```

## Usage

### API Endpoints

- `GET/POST /api/plugins/azure-groups/azure-groups/` - Azure AD groups
- `GET/POST /api/plugins/azure-groups/group-memberships/` - Group memberships

### Web Interface

Navigate to **Plugins > Azure AD Groups** in NetBox to manage groups and memberships.

## Development

This plugin supports NetBox 3.0+ and follows NetBox plugin development standards.

## License

Apache 2.0