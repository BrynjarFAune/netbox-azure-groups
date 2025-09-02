# NetBox Azure Groups Plugin - RBAC Extension Technical Specification

## Overview
This document provides a complete technical specification for extending the existing `netbox-azure-groups` plugin with comprehensive Role-Based Access Control (RBAC) documentation and tracking capabilities.

## Purpose
Extend the existing Azure AD groups plugin to document and track RBAC permissions across multiple systems including Azure AD, on-premises AD, AWS IAM, and other authorization systems. This is for **documentation purposes only** - not for controlling NetBox authentication.

## Architecture Decision
**Approach**: Extend the existing plugin rather than creating a separate co-dependent plugin.

**Rationale**:
- Leverages existing Azure group data structures
- Maintains single plugin for simplified deployment
- Direct relationships with existing GroupMembership models
- Unified API and UI experience

## New Django Models

### 1. RBACSystem Model
Represents systems where RBAC permissions are managed and tracked.

```python
# File: netbox_azure_groups/models/azure_groups.py (append to existing)

class RBACSystemChoices(ChoiceSet):
    AZURE_AD = 'azure_ad'
    ON_PREMISES_AD = 'on_premises_ad'
    AWS_IAM = 'aws_iam'
    GOOGLE_WORKSPACE = 'google_workspace'
    OKTA = 'okta'
    APPLICATION = 'application'
    DATABASE = 'database'
    NETWORK_DEVICE = 'network_device'
    
    CHOICES = [
        (AZURE_AD, 'Azure Active Directory'),
        (ON_PREMISES_AD, 'On-Premises Active Directory'),
        (AWS_IAM, 'AWS Identity & Access Management'),
        (GOOGLE_WORKSPACE, 'Google Workspace'),
        (OKTA, 'Okta'),
        (APPLICATION, 'Application-Specific'),
        (DATABASE, 'Database System'),
        (NETWORK_DEVICE, 'Network Device'),
    ]


class RBACSystem(NetBoxModel):
    """Systems where RBAC permissions are managed and tracked."""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='System name (e.g., "Azure AD Production", "AWS Dev Account")'
    )
    system_type = models.CharField(
        max_length=50,
        choices=RBACSystemChoices,
        help_text='Type of RBAC system'
    )
    description = models.TextField(
        blank=True,
        help_text='System description and purpose'
    )
    base_url = models.URLField(
        blank=True,
        help_text='System console/management URL'
    )
    tenant_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='Tenant/Account ID for cloud systems'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether system is currently in use'
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'RBAC System'
        verbose_name_plural = 'RBAC Systems'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_azure_groups:rbacsystem', args=[self.pk])
```

### 2. RBACPermission Model
Individual permissions/rights in RBAC systems.

```python
class PermissionTypeChoices(ChoiceSet):
    READ = 'read'
    WRITE = 'write'
    EXECUTE = 'execute'
    DELETE = 'delete'
    ADMIN = 'admin'
    OWNER = 'owner'
    CUSTOM = 'custom'
    
    CHOICES = [
        (READ, 'Read/View'),
        (WRITE, 'Write/Modify'),
        (EXECUTE, 'Execute/Run'),
        (DELETE, 'Delete/Remove'),
        (ADMIN, 'Administrative'),
        (OWNER, 'Owner'),
        (CUSTOM, 'Custom Permission'),
    ]


class RBACPermission(NetBoxModel):
    """Individual permissions/rights in RBAC systems."""
    
    name = models.CharField(
        max_length=255,
        help_text='Permission name (e.g., "Virtual Machine Contributor")'
    )
    system = models.ForeignKey(
        RBACSystem,
        on_delete=models.CASCADE,
        related_name='permissions'
    )
    permission_type = models.CharField(
        max_length=20,
        choices=PermissionTypeChoices,
        help_text='General category of permission'
    )
    description = models.TextField(
        blank=True,
        help_text='What this permission allows'
    )
    resource_scope = models.CharField(
        max_length=255,
        blank=True,
        help_text='Resources this permission applies to (e.g., "/subscriptions/xyz")'
    )
    external_id = models.CharField(
        max_length=255,
        blank=True,
        help_text='External system ID/ARN for this permission'
    )
    is_privileged = models.BooleanField(
        default=False,
        help_text='Whether this is a high-privilege permission requiring approval'
    )
    
    class Meta:
        unique_together = [['system', 'name']]
        ordering = ['system', 'name']
        verbose_name = 'RBAC Permission'
        verbose_name_plural = 'RBAC Permissions'
        indexes = [
            models.Index(fields=['system', 'permission_type']),
            models.Index(fields=['is_privileged']),
        ]
    
    def __str__(self):
        return f'{self.system.name}: {self.name}'
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_azure_groups:rbacpermission', args=[self.pk])
```

### 3. ServiceAccount Model
Service accounts and non-human identities with RBAC permissions.

```python
class ServiceAccountTypeChoices(ChoiceSet):
    USER_ASSIGNED = 'user_assigned'
    SYSTEM_ASSIGNED = 'system_assigned'
    SERVICE_PRINCIPAL = 'service_principal'
    MANAGED_IDENTITY = 'managed_identity'
    API_KEY = 'api_key'
    APPLICATION = 'application'
    
    CHOICES = [
        (USER_ASSIGNED, 'User-Assigned Identity'),
        (SYSTEM_ASSIGNED, 'System-Assigned Identity'),
        (SERVICE_PRINCIPAL, 'Service Principal'),
        (MANAGED_IDENTITY, 'Managed Identity'),
        (API_KEY, 'API Key/Token'),
        (APPLICATION, 'Application Account'),
    ]


class ServiceAccount(NetBoxModel):
    """Service accounts and non-human identities with RBAC permissions."""
    
    name = models.CharField(
        max_length=255,
        help_text='Service account name'
    )
    system = models.ForeignKey(
        RBACSystem,
        on_delete=models.CASCADE,
        related_name='service_accounts'
    )
    account_type = models.CharField(
        max_length=50,
        choices=ServiceAccountTypeChoices,
        help_text='Type of service account'
    )
    description = models.TextField(
        blank=True,
        help_text='Purpose and usage of this service account'
    )
    external_id = models.CharField(
        max_length=255,
        blank=True,
        help_text='External system ID (Object ID, ARN, etc.)'
    )
    owner = models.ForeignKey(
        'tenancy.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_service_accounts',
        help_text='Responsible person for this service account'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether account is currently active'
    )
    created_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When service account was created'
    )
    expires_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When service account expires (if applicable)'
    )
    
    class Meta:
        unique_together = [['system', 'name']]
        ordering = ['system', 'name']
        verbose_name = 'Service Account'
        verbose_name_plural = 'Service Accounts'
        indexes = [
            models.Index(fields=['system', 'is_active']),
            models.Index(fields=['expires_date']),
        ]
    
    @property
    def is_expiring_soon(self):
        """Check if account expires within 30 days."""
        if not self.expires_date:
            return False
        return self.expires_date <= timezone.now() + timedelta(days=30)
    
    def __str__(self):
        return f'{self.system.name}: {self.name}'
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_azure_groups:serviceaccount', args=[self.pk])
```

### 4. RBACAssignment Model
Tracks permission assignments to users, service accounts, or groups.

```python
class AssignmentStatusChoices(ChoiceSet):
    ACTIVE = 'active'
    EXPIRED = 'expired'
    REVOKED = 'revoked'
    PENDING = 'pending'
    
    CHOICES = [
        (ACTIVE, 'Active'),
        (EXPIRED, 'Expired'),
        (REVOKED, 'Revoked'),
        (PENDING, 'Pending Approval'),
    ]


class RBACAssignment(NetBoxModel):
    """Tracks permission assignments to users, service accounts, or groups."""
    
    # What permission is assigned
    permission = models.ForeignKey(
        RBACPermission,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    
    # Who/what has the permission (one of these will be set)
    assignee_contact = models.ForeignKey(
        'tenancy.Contact',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rbac_assignments',
        help_text='Human user with this permission'
    )
    assignee_service = models.ForeignKey(
        ServiceAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rbac_assignments',
        help_text='Service account with this permission'
    )
    assignee_device = models.ForeignKey(
        'dcim.Device',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rbac_assignments',
        help_text='Device with this permission'
    )
    
    # How permission is granted
    via_azure_group = models.ForeignKey(
        AzureGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rbac_assignments',
        help_text='Azure/AD group providing this permission'
    )
    direct_assignment = models.BooleanField(
        default=False,
        help_text='Whether permission is directly assigned (not via group)'
    )
    
    # Assignment metadata
    status = models.CharField(
        max_length=20,
        choices=AssignmentStatusChoices,
        default=AssignmentStatusChoices.ACTIVE
    )
    granted_date = models.DateTimeField(
        auto_now_add=True,
        help_text='When permission was granted'
    )
    granted_by = models.ForeignKey(
        'tenancy.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_rbac_assignments',
        help_text='Who granted this permission'
    )
    expires_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When permission expires (if time-limited)'
    )
    justification = models.TextField(
        blank=True,
        help_text='Business justification for this permission'
    )
    last_verified = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When permission was last verified as needed'
    )
    
    class Meta:
        ordering = ['-granted_date']
        verbose_name = 'RBAC Assignment'
        verbose_name_plural = 'RBAC Assignments'
        indexes = [
            models.Index(fields=['permission', 'status']),
            models.Index(fields=['expires_date']),
            models.Index(fields=['via_azure_group']),
        ]
    
    def clean(self):
        # Ensure exactly one assignee is specified
        assignees = [self.assignee_contact, self.assignee_service, self.assignee_device]
        assignee_count = sum(1 for a in assignees if a is not None)
        
        if assignee_count != 1:
            raise ValidationError("Must specify exactly one assignee (contact, service, or device)")
        
        # If via group, ensure assignee is member of that group
        if self.via_azure_group and self.assignee_contact:
            if not GroupMembership.objects.filter(
                group=self.via_azure_group, 
                contact=self.assignee_contact
            ).exists():
                raise ValidationError("Assignee must be member of the specified group")
    
    @property
    def assignee(self):
        """Get the assignee object regardless of type."""
        return self.assignee_contact or self.assignee_service or self.assignee_device
    
    @property
    def assignee_name(self):
        """Get assignee name for display."""
        assignee = self.assignee
        return assignee.name if assignee else "Unknown"
    
    @property
    def is_expiring_soon(self):
        """Check if assignment expires within 30 days."""
        if not self.expires_date:
            return False
        return self.expires_date <= timezone.now() + timedelta(days=30)
    
    def __str__(self):
        return f'{self.assignee_name} → {self.permission.name}'
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_azure_groups:rbacassignment', args=[self.pk])
```

## Database Migration

### Migration File: `0008_add_rbac_models.py`
```python
# Location: netbox_azure_groups/migrations/0008_add_rbac_models.py

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('netbox_azure_groups', '0007_fix_related_names'),
        ('tenancy', '0010_contact_link'),  # Adjust version as needed
        ('dcim', '0170_configcontext_data_schema'),  # Adjust version as needed
    ]

    operations = [
        migrations.CreateModel(
            name='RBACSystem',
            fields=[
                # Standard NetBoxModel fields
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                # RBACSystem specific fields
                ('name', models.CharField(max_length=100, unique=True)),
                ('system_type', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
                ('base_url', models.URLField(blank=True)),
                ('tenant_id', models.CharField(blank=True, max_length=100)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'RBAC System',
                'verbose_name_plural': 'RBAC Systems',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='RBACPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('name', models.CharField(max_length=255)),
                ('permission_type', models.CharField(max_length=20)),
                ('description', models.TextField(blank=True)),
                ('resource_scope', models.CharField(blank=True, max_length=255)),
                ('external_id', models.CharField(blank=True, max_length=255)),
                ('is_privileged', models.BooleanField(default=False)),
                ('system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, 
                                            related_name='permissions', to='netbox_azure_groups.rbacsystem')),
            ],
            options={
                'verbose_name': 'RBAC Permission',
                'verbose_name_plural': 'RBAC Permissions',
                'ordering': ['system', 'name'],
                'unique_together': {('system', 'name')},
            },
        ),
        migrations.CreateModel(
            name='ServiceAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('name', models.CharField(max_length=255)),
                ('account_type', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
                ('external_id', models.CharField(blank=True, max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(blank=True, null=True)),
                ('expires_date', models.DateTimeField(blank=True, null=True)),
                ('system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, 
                                            related_name='service_accounts', to='netbox_azure_groups.rbacsystem')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, 
                                           related_name='owned_service_accounts', to='tenancy.contact')),
            ],
            options={
                'verbose_name': 'Service Account',
                'verbose_name_plural': 'Service Accounts',
                'ordering': ['system', 'name'],
                'unique_together': {('system', 'name')},
            },
        ),
        migrations.CreateModel(
            name='RBACAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict)),
                ('direct_assignment', models.BooleanField(default=False)),
                ('status', models.CharField(default='active', max_length=20)),
                ('granted_date', models.DateTimeField(auto_now_add=True)),
                ('expires_date', models.DateTimeField(blank=True, null=True)),
                ('justification', models.TextField(blank=True)),
                ('last_verified', models.DateTimeField(blank=True, null=True)),
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, 
                                                related_name='assignments', to='netbox_azure_groups.rbacpermission')),
                ('assignee_contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, 
                                                      related_name='rbac_assignments', to='tenancy.contact')),
                ('assignee_service', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, 
                                                      related_name='rbac_assignments', to='netbox_azure_groups.serviceaccount')),
                ('assignee_device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, 
                                                     related_name='rbac_assignments', to='dcim.device')),
                ('via_azure_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, 
                                                     related_name='rbac_assignments', to='netbox_azure_groups.azuregroup')),
                ('granted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, 
                                                related_name='granted_rbac_assignments', to='tenancy.contact')),
            ],
            options={
                'verbose_name': 'RBAC Assignment',
                'verbose_name_plural': 'RBAC Assignments',
                'ordering': ['-granted_date'],
            },
        ),
        # Add indexes
        migrations.AddIndex(
            model_name='rbacpermission',
            index=models.Index(fields=['system', 'permission_type'], name='rbacperm_system_type_idx'),
        ),
        migrations.AddIndex(
            model_name='rbacpermission',
            index=models.Index(fields=['is_privileged'], name='rbacperm_privileged_idx'),
        ),
        migrations.AddIndex(
            model_name='serviceaccount',
            index=models.Index(fields=['system', 'is_active'], name='svcacct_system_active_idx'),
        ),
        migrations.AddIndex(
            model_name='serviceaccount',
            index=models.Index(fields=['expires_date'], name='svcacct_expires_idx'),
        ),
        migrations.AddIndex(
            model_name='rbacassignment',
            index=models.Index(fields=['permission', 'status'], name='rbacassign_perm_status_idx'),
        ),
        migrations.AddIndex(
            model_name='rbacassignment',
            index=models.Index(fields=['expires_date'], name='rbacassign_expires_idx'),
        ),
        migrations.AddIndex(
            model_name='rbacassignment',
            index=models.Index(fields=['via_azure_group'], name='rbacassign_group_idx'),
        ),
    ]
```

## API Layer

### Serializers
**File**: `netbox_azure_groups/api/serializers.py` (add to existing)

```python
from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from ..models import RBACSystem, RBACPermission, ServiceAccount, RBACAssignment
from tenancy.api.serializers import ContactSerializer

class RBACSystemSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_azure_groups-api:rbacsystem-detail'
    )
    permissions_count = serializers.IntegerField(read_only=True)
    service_accounts_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = RBACSystem
        fields = [
            'id', 'url', 'display', 'name', 'system_type', 'description',
            'base_url', 'tenant_id', 'is_active', 'permissions_count',
            'service_accounts_count', 'created', 'last_updated', 
            'custom_field_data', 'tags'
        ]

class RBACPermissionSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_azure_groups-api:rbacpermission-detail'
    )
    system = RBACSystemSerializer(read_only=True)
    system_id = serializers.PrimaryKeyRelatedField(
        queryset=RBACSystem.objects.all(),
        source='system',
        write_only=True
    )
    assignments_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = RBACPermission
        fields = [
            'id', 'url', 'display', 'name', 'system', 'system_id',
            'permission_type', 'description', 'resource_scope',
            'external_id', 'is_privileged', 'assignments_count',
            'created', 'last_updated', 'custom_field_data', 'tags'
        ]

class ServiceAccountSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_azure_groups-api:serviceaccount-detail'
    )
    system = RBACSystemSerializer(read_only=True)
    system_id = serializers.PrimaryKeyRelatedField(
        queryset=RBACSystem.objects.all(),
        source='system',
        write_only=True
    )
    owner = ContactSerializer(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(),
        source='owner',
        write_only=True,
        required=False
    )
    is_expiring_soon = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ServiceAccount
        fields = [
            'id', 'url', 'display', 'name', 'system', 'system_id',
            'account_type', 'description', 'external_id', 'owner',
            'owner_id', 'is_active', 'created_date', 'expires_date',
            'is_expiring_soon', 'created', 'last_updated',
            'custom_field_data', 'tags'
        ]

class RBACAssignmentSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_azure_groups-api:rbacassignment-detail'
    )
    permission = RBACPermissionSerializer(read_only=True)
    permission_id = serializers.PrimaryKeyRelatedField(
        queryset=RBACPermission.objects.all(),
        source='permission',
        write_only=True
    )
    assignee_name = serializers.CharField(read_only=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = RBACAssignment
        fields = [
            'id', 'url', 'display', 'permission', 'permission_id',
            'assignee_contact', 'assignee_service', 'assignee_device',
            'assignee_name', 'via_azure_group', 'direct_assignment',
            'status', 'granted_date', 'granted_by', 'expires_date',
            'justification', 'last_verified', 'is_expiring_soon',
            'created', 'last_updated', 'custom_field_data', 'tags'
        ]
```

### ViewSets
**File**: `netbox_azure_groups/api/viewsets.py` (add to existing)

```python
from django.db.models import Count
from netbox.api.viewsets import NetBoxModelViewSet
from ..models import RBACSystem, RBACPermission, ServiceAccount, RBACAssignment
from ..filtersets import (
    RBACSystemFilterSet, RBACPermissionFilterSet,
    ServiceAccountFilterSet, RBACAssignmentFilterSet
)
from .serializers import (
    RBACSystemSerializer, RBACPermissionSerializer,
    ServiceAccountSerializer, RBACAssignmentSerializer
)

class RBACSystemViewSet(NetBoxModelViewSet):
    queryset = RBACSystem.objects.prefetch_related('tags').annotate(
        permissions_count=Count('permissions', distinct=True),
        service_accounts_count=Count('service_accounts', distinct=True)
    )
    serializer_class = RBACSystemSerializer
    filterset_class = RBACSystemFilterSet

class RBACPermissionViewSet(NetBoxModelViewSet):
    queryset = RBACPermission.objects.prefetch_related('tags', 'system').annotate(
        assignments_count=Count('assignments', distinct=True)
    )
    serializer_class = RBACPermissionSerializer
    filterset_class = RBACPermissionFilterSet

class ServiceAccountViewSet(NetBoxModelViewSet):
    queryset = ServiceAccount.objects.prefetch_related('tags', 'system', 'owner')
    serializer_class = ServiceAccountSerializer
    filterset_class = ServiceAccountFilterSet

class RBACAssignmentViewSet(NetBoxModelViewSet):
    queryset = RBACAssignment.objects.prefetch_related(
        'tags', 'permission__system', 'assignee_contact',
        'assignee_service', 'assignee_device', 'via_azure_group',
        'granted_by'
    )
    serializer_class = RBACAssignmentSerializer
    filterset_class = RBACAssignmentFilterSet
    
    @action(detail=False, methods=['post'])
    def bulk_sync(self, request):
        """Bulk create/update RBAC assignments from external sync tools."""
        # Implementation for bulk sync operations
        pass
```

### URL Configuration
**File**: `netbox_azure_groups/api/urls.py` (add to existing router)

```python
# Add to existing router configuration
router.register('rbac-systems', views.RBACSystemViewSet)
router.register('rbac-permissions', views.RBACPermissionViewSet)
router.register('service-accounts', views.ServiceAccountViewSet)
router.register('rbac-assignments', views.RBACAssignmentViewSet)
```

## FilterSets
**File**: `netbox_azure_groups/filtersets.py` (add to existing)

```python
import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from tenancy.models import Contact
from dcim.models import Device
from .models import (
    RBACSystem, RBACPermission, ServiceAccount, RBACAssignment,
    RBACSystemChoices, PermissionTypeChoices, ServiceAccountTypeChoices,
    AssignmentStatusChoices
)

class RBACSystemFilterSet(NetBoxModelFilterSet):
    system_type = django_filters.MultipleChoiceFilter(
        choices=RBACSystemChoices
    )
    is_active = django_filters.BooleanFilter()
    
    class Meta:
        model = RBACSystem
        fields = ['id', 'name', 'system_type', 'is_active', 'tenant_id']

class RBACPermissionFilterSet(NetBoxModelFilterSet):
    system = django_filters.ModelMultipleChoiceFilter(
        queryset=RBACSystem.objects.all()
    )
    permission_type = django_filters.MultipleChoiceFilter(
        choices=PermissionTypeChoices
    )
    is_privileged = django_filters.BooleanFilter()
    
    class Meta:
        model = RBACPermission
        fields = ['id', 'name', 'system', 'permission_type', 'is_privileged', 'resource_scope']

class ServiceAccountFilterSet(NetBoxModelFilterSet):
    system = django_filters.ModelMultipleChoiceFilter(
        queryset=RBACSystem.objects.all()
    )
    account_type = django_filters.MultipleChoiceFilter(
        choices=ServiceAccountTypeChoices
    )
    owner = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all()
    )
    is_active = django_filters.BooleanFilter()
    expires_date = django_filters.DateFilter()
    expires_date__gte = django_filters.DateFilter(field_name='expires_date', lookup_expr='gte')
    expires_date__lte = django_filters.DateFilter(field_name='expires_date', lookup_expr='lte')
    
    class Meta:
        model = ServiceAccount
        fields = ['id', 'name', 'system', 'account_type', 'owner', 'is_active', 'external_id']

class RBACAssignmentFilterSet(NetBoxModelFilterSet):
    permission = django_filters.ModelMultipleChoiceFilter(
        queryset=RBACPermission.objects.all()
    )
    system = django_filters.ModelMultipleChoiceFilter(
        field_name='permission__system',
        queryset=RBACSystem.objects.all()
    )
    assignee_contact = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all()
    )
    assignee_service = django_filters.ModelMultipleChoiceFilter(
        queryset=ServiceAccount.objects.all()
    )
    assignee_device = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all()
    )
    via_azure_group = django_filters.ModelMultipleChoiceFilter(
        queryset=AzureGroup.objects.all()
    )
    status = django_filters.MultipleChoiceFilter(
        choices=AssignmentStatusChoices
    )
    expires_date = django_filters.DateFilter()
    expires_date__gte = django_filters.DateFilter(field_name='expires_date', lookup_expr='gte')
    expires_date__lte = django_filters.DateFilter(field_name='expires_date', lookup_expr='lte')
    granted_date = django_filters.DateFilter()
    granted_date__gte = django_filters.DateFilter(field_name='granted_date', lookup_expr='gte')
    granted_date__lte = django_filters.DateFilter(field_name='granted_date', lookup_expr='lte')
    
    class Meta:
        model = RBACAssignment
        fields = ['id', 'permission', 'status', 'direct_assignment', 'granted_by']
```

## Web Interface

### Navigation Menu
**File**: `netbox_azure_groups/navigation.py` (extend existing)

```python
from utilities.choices import ButtonColorChoices
from netbox.plugins import PluginMenuButton, PluginMenuItem, PluginMenu

# Add RBAC section to plugin menu
menu_items = (
    PluginMenuItem(
        link='plugins:netbox_azure_groups:azuregroup_list',
        link_text='Azure Groups',
        permissions=['netbox_azure_groups.view_azuregroup'],
        buttons=[
            PluginMenuButton(
                link='plugins:netbox_azure_groups:azuregroup_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
                permissions=['netbox_azure_groups.add_azuregroup']
            ),
        ]
    ),
    PluginMenuItem(
        link='plugins:netbox_azure_groups:groupmembership_list',
        link_text='Group Memberships',
        permissions=['netbox_azure_groups.view_groupmembership'],
    ),
    # RBAC Menu Items
    PluginMenuItem(
        link='plugins:netbox_azure_groups:rbacsystem_list',
        link_text='RBAC Systems',
        permissions=['netbox_azure_groups.view_rbacsystem'],
        buttons=[
            PluginMenuButton(
                link='plugins:netbox_azure_groups:rbacsystem_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
                permissions=['netbox_azure_groups.add_rbacsystem']
            ),
        ]
    ),
    PluginMenuItem(
        link='plugins:netbox_azure_groups:rbacpermission_list',
        link_text='Permissions',
        permissions=['netbox_azure_groups.view_rbacpermission'],
        buttons=[
            PluginMenuButton(
                link='plugins:netbox_azure_groups:rbacpermission_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
                permissions=['netbox_azure_groups.add_rbacpermission']
            ),
        ]
    ),
    PluginMenuItem(
        link='plugins:netbox_azure_groups:serviceaccount_list',
        link_text='Service Accounts',
        permissions=['netbox_azure_groups.view_serviceaccount'],
        buttons=[
            PluginMenuButton(
                link='plugins:netbox_azure_groups:serviceaccount_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
                permissions=['netbox_azure_groups.add_serviceaccount']
            ),
        ]
    ),
    PluginMenuItem(
        link='plugins:netbox_azure_groups:rbacassignment_list',
        link_text='RBAC Assignments',
        permissions=['netbox_azure_groups.view_rbacassignment'],
        buttons=[
            PluginMenuButton(
                link='plugins:netbox_azure_groups:rbacassignment_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
                permissions=['netbox_azure_groups.add_rbacassignment']
            ),
        ]
    ),
    PluginMenuItem(
        link='plugins:netbox_azure_groups:rbac_dashboard',
        link_text='RBAC Dashboard',
        permissions=['netbox_azure_groups.view_rbacassignment'],
    ),
)

menu = PluginMenu(
    label='Azure Groups & RBAC',
    icon_class='mdi mdi-microsoft-azure',
    groups=(
        ('Group Management', menu_items[:2]),
        ('RBAC Documentation', menu_items[2:]),
    ),
)
```

### Template Examples

#### RBAC Dashboard
**File**: `netbox_azure_groups/templates/netbox_azure_groups/rbac_dashboard.html`

```html
{% extends 'base/layout.html' %}
{% load helpers %}

{% block title %}RBAC Dashboard{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <h1>RBAC Dashboard</h1>
    </div>
</div>

<div class="row mt-3">
    <!-- System Statistics -->
    <div class="col-md-3">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="card-title mb-0">
                    <i class="mdi mdi-shield-account"></i> Systems
                </h5>
            </div>
            <div class="card-body text-center">
                <h2>{{ systems_count }}</h2>
                <p class="text-muted mb-0">Active RBAC Systems</p>
            </div>
        </div>
    </div>
    
    <!-- Permission Statistics -->
    <div class="col-md-3">
        <div class="card">
            <div class="card-header bg-info text-white">
                <h5 class="card-title mb-0">
                    <i class="mdi mdi-key-variant"></i> Permissions
                </h5>
            </div>
            <div class="card-body text-center">
                <h2>{{ permissions_count }}</h2>
                <p class="text-muted mb-0">Tracked Permissions</p>
            </div>
        </div>
    </div>
    
    <!-- Assignment Statistics -->
    <div class="col-md-3">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5 class="card-title mb-0">
                    <i class="mdi mdi-account-key"></i> Assignments
                </h5>
            </div>
            <div class="card-body text-center">
                <h2>{{ active_assignments_count }}</h2>
                <p class="text-muted mb-0">Active Assignments</p>
            </div>
        </div>
    </div>
    
    <!-- Expiring Soon -->
    <div class="col-md-3">
        <div class="card">
            <div class="card-header bg-warning text-white">
                <h5 class="card-title mb-0">
                    <i class="mdi mdi-clock-alert"></i> Expiring
                </h5>
            </div>
            <div class="card-body text-center">
                <h2>{{ expiring_count }}</h2>
                <p class="text-muted mb-0">Within 30 Days</p>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <!-- Recent Assignments -->
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title">Recent Assignments</h5>
            </div>
            <div class="card-body">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Assignee</th>
                            <th>Permission</th>
                            <th>System</th>
                            <th>Granted</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for assignment in recent_assignments %}
                        <tr>
                            <td>
                                <a href="{{ assignment.get_absolute_url }}">
                                    {{ assignment.assignee_name }}
                                </a>
                            </td>
                            <td>{{ assignment.permission.name }}</td>
                            <td>{{ assignment.permission.system.name }}</td>
                            <td>{{ assignment.granted_date|date:"Y-m-d" }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <!-- Privileged Permissions -->
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title">Privileged Permissions</h5>
            </div>
            <div class="card-body">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Permission</th>
                            <th>System</th>
                            <th>Active Assignments</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for permission in privileged_permissions %}
                        <tr>
                            <td>
                                <a href="{{ permission.get_absolute_url }}">
                                    {{ permission.name }}
                                </a>
                            </td>
                            <td>{{ permission.system.name }}</td>
                            <td>
                                <span class="badge badge-danger">
                                    {{ permission.assignments_count }}
                                </span>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<!-- Expiring Assignments -->
<div class="row mt-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header bg-warning">
                <h5 class="card-title text-white">Assignments Expiring Soon</h5>
            </div>
            <div class="card-body">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Assignee</th>
                            <th>Permission</th>
                            <th>System</th>
                            <th>Expires</th>
                            <th>Days Remaining</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for assignment in expiring_assignments %}
                        <tr>
                            <td>
                                <a href="{{ assignment.get_absolute_url }}">
                                    {{ assignment.assignee_name }}
                                </a>
                            </td>
                            <td>{{ assignment.permission.name }}</td>
                            <td>{{ assignment.permission.system.name }}</td>
                            <td>{{ assignment.expires_date|date:"Y-m-d" }}</td>
                            <td>
                                <span class="badge badge-warning">
                                    {{ assignment.days_until_expiry }} days
                                </span>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Add new model classes to `models/azure_groups.py`
- [ ] Create migration file `0008_add_rbac_models.py`
- [ ] Update model imports in `models/__init__.py`
- [ ] Run migrations and verify database schema
- [ ] Update admin registration for new models

### Phase 2: API Layer (Week 2)
- [ ] Implement serializers in `api/serializers.py`
- [ ] Create viewsets in `api/viewsets.py`
- [ ] Add URL patterns in `api/urls.py`
- [ ] Implement filtersets in `filtersets.py`
- [ ] Test all API endpoints with curl/Postman
- [ ] Document API endpoints

### Phase 3: Web Interface (Week 3)
- [ ] Create list/detail templates for each model
- [ ] Implement forms for CRUD operations
- [ ] Add table classes for list views
- [ ] Update navigation menu
- [ ] Create RBAC dashboard
- [ ] Test web interface functionality

### Phase 4: Integration (Week 4)
- [ ] Add RBAC sections to contact detail pages
- [ ] Add RBAC sections to device detail pages
- [ ] Show permissions granted via groups
- [ ] Implement permission assignment workflows
- [ ] Add template content hooks
- [ ] Create relationship visualizations

### Phase 5: Advanced Features (Week 5+)
- [ ] Bulk permission assignment tools
- [ ] Automated expiration notifications
- [ ] Compliance reporting views
- [ ] External sync tool integration
- [ ] Permission approval workflows
- [ ] Audit trail implementation

## Testing Requirements

### Unit Tests
```python
# netbox_azure_groups/tests/test_rbac_models.py
class RBACModelTests(TestCase):
    def test_rbac_assignment_validation(self):
        """Test assignment requires exactly one assignee"""
        
    def test_service_account_expiration(self):
        """Test service account expiration detection"""
        
    def test_permission_via_group(self):
        """Test permission assignment via group membership"""
        
    def test_assignment_status_transitions(self):
        """Test assignment status state changes"""
```

### API Tests
```python
# netbox_azure_groups/tests/test_rbac_api.py
class RBACAPITests(APITestCase):
    def test_rbac_system_crud(self):
        """Test RBAC system CRUD operations"""
        
    def test_bulk_assignment_sync(self):
        """Test bulk assignment synchronization"""
        
    def test_permission_filtering(self):
        """Test permission filtering by system and type"""
        
    def test_expiring_assignments_filter(self):
        """Test filtering assignments by expiration date"""
```

## Configuration
**File**: `netbox_azure_groups/__init__.py`

```python
# Add to plugin config
class NetBoxAzureGroupsConfig(PluginConfig):
    name = 'netbox_azure_groups'
    verbose_name = 'NetBox Azure Groups & RBAC'
    description = 'Track Azure AD groups and RBAC permissions'
    version = '2.0.0'  # Bump version for RBAC features
    author = 'Your Name'
    base_url = 'azure-groups'
    min_version = '3.0.0'
    max_version = '3.9.99'
    default_settings = {
        'rbac_assignment_approval_required': False,
        'rbac_assignment_default_expiry_days': 365,
        'rbac_privileged_permissions_require_justification': True,
        'rbac_expiration_warning_days': 30,
    }

config = NetBoxAzureGroupsConfig
```

## Dependencies
Update `setup.py` or `pyproject.toml`:
```python
install_requires=[
    'netbox>=3.0.0',
    # No additional dependencies required
]
```

## Notes for Implementation

1. **Database Indexes**: Ensure all foreign keys and commonly filtered fields have indexes
2. **Performance**: Use `select_related()` and `prefetch_related()` in querysets
3. **Validation**: Implement proper model validation in `clean()` methods
4. **Permissions**: Follow NetBox permission model for all new models
5. **Audit Trail**: All models inherit from NetBoxModel for automatic audit logging
6. **Custom Fields**: All models support custom fields through NetBoxModel
7. **Tags**: All models support tags through NetBoxModel
8. **Bulk Operations**: API supports bulk create/update/delete operations
9. **GraphQL**: Consider adding GraphQL support if needed
10. **Webhooks**: New models will trigger NetBox webhooks automatically

## Security Considerations

1. **Permission Validation**: Ensure users can only view/modify assignments they have access to
2. **Sensitive Data**: Mark privileged permissions and handle appropriately
3. **Audit Logging**: All RBAC changes should be logged
4. **Expiration Handling**: Implement automated status updates for expired assignments
5. **API Security**: Follow NetBox API permission model

## Future Enhancements

1. **Approval Workflows**: Add approval process for privileged permissions
2. **Notifications**: Email/webhook notifications for expiring assignments
3. **Compliance Reports**: Generate compliance reports for auditors
4. **Integration APIs**: Webhooks for external RBAC systems
5. **Visualization**: Network diagrams showing permission flows
6. **Risk Scoring**: Calculate risk scores based on permission combinations
7. **Recommendation Engine**: Suggest permission optimizations