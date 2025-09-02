# NetBox RBAC Extension - Flexible Access Control Documentation System

## Project Overview

Transform the existing `netbox-azure-groups` plugin into a comprehensive access control documentation system that tracks how users gain access to protected resources through various control mechanisms (primarily FortiGate firewall policies, with future support for physical access, VPN, and other systems).

**Core Pattern**: `Protected Resource ← Access Control Method ← Azure Group ← User Membership`

## Business Use Case

- **Services/Systems** are protected by access control mechanisms
- **Primary Method**: FortiGate firewall policies that allow traffic based on Azure AD group membership
- **Access Chain**: Users get access to resources by being members of specific Azure groups that are referenced in access control policies
- **Documentation Goal**: Provide clear visibility into "who has access to what and how"
- **Future Scope**: Physical locations, VPN access, cloud resources, application permissions

## Current Status

### ✅ **Completed Foundation**
- Core Azure Groups functionality with member/owner tracking
- API endpoints for groups, memberships, ownerships
- Read-only web interface for viewing/deleting groups
- Deployment pipeline to dev server (brynjar@10.0.123.5)
- Basic RBAC models deployed (need refinement per new spec)

### 🔄 **Current Challenge**
- Existing RBAC models are too generic and don't match the actual use case
- Need to refactor to resource-centric access control documentation
- Missing database migrations for new models

## Refined Data Models

### **1. ProtectedResource**
```python
class ProtectedResource(NetBoxModel):
    """Any resource that requires access control."""
    name = models.CharField(max_length=200)  # "HR Database", "Server Room A", "Finance Portal"
    
    resource_type = models.CharField(choices=[
        ('web_application', 'Web Application'),
        ('database', 'Database'),
        ('api_service', 'API Service'), 
        ('file_share', 'File Share'),
        ('physical_location', 'Physical Location'),
        ('network_device', 'Network Device'),
        ('cloud_resource', 'Cloud Resource'),
        ('other', 'Other')
    ])
    
    description = models.TextField()
    
    # Optional technical details
    base_url = models.URLField(blank=True)
    ip_addresses = models.JSONField(default=list, blank=True)  
    physical_location = models.CharField(max_length=200, blank=True)  # "Building A, Room 101"
    
    # Business context
    owner_contact = models.ForeignKey('tenancy.Contact', related_name='owned_resources')
    business_unit = models.CharField(max_length=100, blank=True)
    criticality = models.CharField(choices=['low', 'medium', 'high', 'critical'])
    
    is_active = models.BooleanField(default=True)
```

### **2. AccessControlMethod**
```python
class AccessControlMethod(NetBoxModel):
    """How access to a resource is controlled and enforced."""
    resource = models.ForeignKey(ProtectedResource, related_name='access_methods')
    
    # What enforces the access
    control_type = models.CharField(choices=[
        ('fortigate_policy', 'FortiGate Firewall Policy'),
        ('badge_reader', 'Physical Badge Reader'),
        ('vpn_config', 'VPN Configuration'),
        ('application_rbac', 'Application Role'),
        ('network_acl', 'Network ACL'),
        ('cloud_iam', 'Cloud IAM Policy'),
        ('manual_process', 'Manual Process'),
        ('other', 'Other')
    ])
    
    name = models.CharField(max_length=200)  # "Policy-42", "Door-Controller-A", "VPN-Group-Finance"
    description = models.TextField()
    
    # The key connection: which Azure group provides access
    azure_group = models.ForeignKey(AzureGroup, related_name='enables_access_via')
    
    # Access details
    access_level = models.CharField(choices=[
        ('read', 'Read Only'),
        ('write', 'Read/Write'), 
        ('admin', 'Administrative'),
        ('full', 'Full Access'),
        ('physical', 'Physical Access')
    ])
    
    # Technical details (flexible JSON for different control types)
    configuration = models.JSONField(default=dict, blank=True)  # Store type-specific config
    
    is_active = models.BooleanField(default=True)
    last_verified = models.DateTimeField(null=True, blank=True)
```

### **3. AccessGrant**
```python
class AccessGrant(NetBoxModel):
    """Computed/tracked access grants showing the full access chain."""
    
    # The access chain
    resource = models.ForeignKey(ProtectedResource, related_name='access_grants')
    contact = models.ForeignKey('tenancy.Contact', related_name='access_grants')
    azure_group = models.ForeignKey(AzureGroup, related_name='access_grants')
    control_method = models.ForeignKey(AccessControlMethod, related_name='access_grants')
    
    # Grant metadata
    access_level = models.CharField(max_length=20)  # Inherited from control method
    granted_via = models.CharField(choices=[
        ('direct_membership', 'Direct Group Membership'),
        ('nested_membership', 'Nested Group Membership'),
        ('inherited', 'Inherited Permission')
    ])
    
    # Audit info
    first_granted = models.DateTimeField(auto_now_add=True)
    last_verified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = [['resource', 'contact', 'azure_group', 'control_method']]
```

### **4. AccessControlSystem** (Optional)
```python
class AccessControlSystem(NetBoxModel):
    """Systems that enforce access control (FortiGate, badge system, etc.)."""
    name = models.CharField(max_length=200)  # "FortiGate-HQ", "Badge-System-Building-A"
    system_type = models.CharField(choices=[
        ('fortigate', 'FortiGate Firewall'),
        ('badge_system', 'Badge/Card Reader System'),
        ('vpn_server', 'VPN Server'),
        ('identity_provider', 'Identity Provider'),
        ('other', 'Other')
    ])
    
    description = models.TextField()
    management_url = models.URLField(blank=True)
    
    # Link to NetBox devices if applicable
    netbox_device = models.ForeignKey('dcim.Device', null=True, blank=True, related_name='access_control_systems')
    
    is_active = models.BooleanField(default=True)
```

## Implementation Task List

### **Phase 1: Model Refactoring & Database Setup**
**Priority: CRITICAL - Must complete before other phases**

- [ ] **Task 1.1**: Remove existing generic RBAC models (RBACSystem, RBACPermission, ServiceAccount, RBACAssignment)
- [ ] **Task 1.2**: Implement new ProtectedResource model
- [ ] **Task 1.3**: Implement new AccessControlMethod model  
- [ ] **Task 1.4**: Implement new AccessGrant model
- [ ] **Task 1.5**: Update model imports in `__init__.py`
- [ ] **Task 1.6**: Create and apply Django migrations for new models
- [ ] **Task 1.7**: Verify database schema creation and relationships
- [ ] **Task 1.8**: Create sample test data via API

**Success Criteria**: New models deployed with working database tables and relationships

### **Phase 2: API Layer Development**
**Priority: HIGH - Enables programmatic management**

- [ ] **Task 2.1**: Create serializers for ProtectedResource, AccessControlMethod, AccessGrant
- [ ] **Task 2.2**: Implement viewsets with CRUD operations for each model
- [ ] **Task 2.3**: Add filtering capabilities (by resource type, control type, access level)
- [ ] **Task 2.4**: Register API endpoints in URL routing
- [ ] **Task 2.5**: Create custom endpoints for access analytics:
  - [ ] `/api/resources/{id}/who-has-access/` - List all users with access to resource
  - [ ] `/api/contacts/{id}/resource-access/` - List all resources contact can access
  - [ ] `/api/azure-groups/{id}/provides-access-to/` - List resources group provides access to
- [ ] **Task 2.6**: Add bulk operations for sync tool integration
- [ ] **Task 2.7**: Test API endpoints with curl/Postman

**Success Criteria**: Full REST API with filtering and custom analytics endpoints

### **Phase 3: Web Interface Development**
**Priority: MEDIUM - Enables manual management and reporting**

#### **3A: Forms and Basic Views**
- [ ] **Task 3A.1**: Create forms for ProtectedResource with validation
- [ ] **Task 3A.2**: Create forms for AccessControlMethod with Azure group selection
- [ ] **Task 3A.3**: Create forms for AccessGrant (likely read-only/computed)
- [ ] **Task 3A.4**: Build list views for all models following NetBox UI patterns
- [ ] **Task 3A.5**: Build detail views for all models with proper context
- [ ] **Task 3A.6**: Add URL patterns for all new views

#### **3B: Enhanced Detail Pages**
- [ ] **Task 3B.1**: Enhance ProtectedResource detail page with tabs:
  - [ ] Overview tab (resource details, owner, criticality)
  - [ ] Access Control tab (all control methods)
  - [ ] Who Has Access tab (all users with access + how they got it)
  - [ ] Azure Groups tab (all groups providing access)
- [ ] **Task 3B.2**: Enhance Contact detail page with new tab:
  - [ ] Resource Access tab (all resources they can access)
- [ ] **Task 3B.3**: Enhance Azure Group detail page with new tabs:
  - [ ] Provides Access tab (all resources this group grants access to)
  - [ ] Control Methods tab (all access control mechanisms using this group)

#### **3C: Navigation and Integration**
- [ ] **Task 3C.1**: Add navigation menu entries for Access Control sections
- [ ] **Task 3C.2**: Create access control dashboard showing system-wide metrics
- [ ] **Task 3C.3**: Integrate new views with existing plugin navigation

**Success Criteria**: Full web interface for managing access control documentation

### **Phase 4: Advanced Features**
**Priority: LOW - Future enhancements**

- [ ] **Task 4.1**: Implement AccessControlSystem model and management
- [ ] **Task 4.2**: Create automated access grant computation from group memberships
- [ ] **Task 4.3**: Build access analytics dashboard with charts
- [ ] **Task 4.4**: Add access verification workflows
- [ ] **Task 4.5**: Create cross-resource access correlation reports
- [ ] **Task 4.6**: Implement access grant expiration tracking
- [ ] **Task 4.7**: Add webhook integrations for external sync tools

## User Interface Design Goals

### **ProtectedResource Detail Page**
```
[Resource Name] - [Resource Type] - [Criticality Badge]

Tabs:
- Overview: Basic details, owner, business unit
- Access Control: List of all access control methods
- Who Has Access: Table of users + group + method + access level
- Azure Groups: Groups that provide access to this resource
- Audit: Access grant history and verification logs
```

### **Contact Detail Page** (Enhanced)
```
[Existing Contact Info]

New Tab:
- Resource Access: Table of resources + access level + via which group + method
```

### **Azure Group Detail Page** (Enhanced)
```
[Existing Group Info]

New Tabs:
- Provides Access: Table of resources this group grants access to
- Control Methods: Access control mechanisms using this group
```

## Success Metrics

### **Phase 1 Complete**: 25% Project Completion
- ✅ Database models refactored and deployed
- ✅ Migrations applied successfully
- ✅ Sample data created

### **Phase 2 Complete**: 60% Project Completion  
- ✅ Full REST API with analytics endpoints
- ✅ Programmatic access to all access control data
- ✅ External tool integration possible

### **Phase 3 Complete**: 90% Project Completion
- ✅ Complete web interface
- ✅ Enhanced detail pages with access control tabs
- ✅ Manual management capabilities

### **Phase 4 Complete**: 100% Project Completion
- ✅ Advanced analytics and reporting
- ✅ Automated access grant computation
- ✅ External system integrations

## Technical Architecture

### **Database Layer**
- 3-4 new Django models extending NetBoxModel
- Foreign key relationships to existing AzureGroup and Contact models
- Proper indexing for performance on access queries
- Support for custom fields and tags

### **API Layer**
- REST API endpoints for all new models
- Custom analytics endpoints for common queries
- Bulk operations for external sync tools
- Filtering and search capabilities

### **Web Interface**
- CRUD interfaces following NetBox UI patterns
- Enhanced detail pages with access control information
- Dashboard with access control metrics
- Integration with existing contact/device/group pages

## Development Environment

- **Target Server**: brynjar@10.0.123.5
- **Plugin Location**: `netbox-docker/plugins/netbox-azure-groups`
- **Local Development**: `C:\Users\brynjar.aune\Proj\internal\netbox-plugin\aad-groups`
- **Deployment Method**: Git push + Docker container rebuild with `--no-cache`

## Risk Mitigation

- **Backwards Compatibility**: All existing Azure group functionality preserved
- **Data Migration**: Plan for migrating any existing data from old RBAC models
- **Performance**: Proper indexing and query optimization for access lookups
- **Scalability**: Designed for large numbers of resources and users
- **Security**: Follow NetBox permission model and read-only UI approach

## Next Immediate Steps

1. **Start with Phase 1, Task 1.1**: Remove existing generic RBAC models
2. **Complete Phase 1 entirely** before moving to API or UI work
3. **Focus on FortiGate policy use case** first, then expand to other control types
4. **Test each phase thoroughly** before proceeding to the next

This specification provides a complete roadmap for transforming the Azure Groups plugin into a comprehensive access control documentation system that directly addresses your FortiGate + Azure AD use case while remaining flexible for future expansion.