# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial plugin structure and models
- Azure AD group management with metadata (name, description, object_id, mail, group_type)
- Group membership support for both Contacts and Devices using generic foreign keys
- Many-to-many relationships allowing unlimited group assignments per entity
- REST API with full CRUD operations for groups and memberships
- Web interface for group and membership management
- Filtering and search functionality for both groups and memberships
- Unit tests for models and API endpoints
- Django migrations for database schema
- Plugin configuration and packaging

### Features
- **Azure AD Group Model**: Track security groups, distribution lists, and Microsoft 365 groups
- **Multi-Entity Support**: Both NetBox contacts and devices can be group members
- **Flexible Memberships**: Support for direct and nested membership types
- **Microsoft Graph Compatible**: Data structure compatible with Microsoft Graph API
- **Full API Coverage**: RESTful API endpoints for automation and sync tools
- **NetBox Integration**: Seamless integration with NetBox's web interface and permissions

## [0.1.0] - 2024-XX-XX

### Added
- Initial release of NetBox Azure AD Groups plugin