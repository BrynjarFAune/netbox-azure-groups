  NetBox Azure AD Groups Plugin Project Description

  Project Name: netbox-azure-groups

  Purpose: Track Azure AD security groups and user memberships in NetBox for permission management and organizational visibility.

  Core Features:
  - Group Model: Custom NetBox model to store Azure AD groups (name, description, group type, object ID)
  - Group Membership: Track which users/contacts belong to which groups
  - Sync Integration: API endpoints for the sync tool to populate group data
  - Web UI: NetBox interface to view groups, members, and relationships
  - Filtering: Filter contacts/devices by group membership
  - API Access: REST API for external tools to query group information

  Technical Requirements:
  - NetBox plugin framework (Django app)
  - Database models for groups and memberships
  - REST API serializers and viewsets
  - Web templates for group management
  - Integration with existing Contact model
  - Microsoft Graph API data structure compatibility

  Deliverables:
  - Installable NetBox plugin package
  - Database migrations
  - API documentation
  - Basic web interface for group management

plugin reference / docs:
- https://netboxlabs.com/docs/netbox/plugins/development/
- https://github.com/netbox-community/netbox-plugin-tutorial

personal reference from self developed plugins: 
- https://github.com/BrynjarFAune/netbox_invoices
