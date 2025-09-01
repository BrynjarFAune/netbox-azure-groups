from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from netbox.models import NetBoxModel
from utilities.choices import ChoiceSet
import uuid


class GroupTypeChoices(ChoiceSet):
    SECURITY = 'security'
    MICROSOFT365 = 'microsoft365'
    MAIL_SECURITY = 'mail_security'
    DISTRIBUTION = 'distribution'
    DYNAMIC_SECURITY = 'dynamic_security'
    DYNAMIC_M365 = 'dynamic_m365'
    
    CHOICES = [
        (SECURITY, 'Security Group'),
        (MICROSOFT365, 'Microsoft 365 Group'),
        (MAIL_SECURITY, 'Mail-Enabled Security'),
        (DISTRIBUTION, 'Distribution List'),
        (DYNAMIC_SECURITY, 'Dynamic Security'),
        (DYNAMIC_M365, 'Dynamic Microsoft 365'),
    ]


class GroupSourceChoices(ChoiceSet):
    AZURE_AD = 'azure_ad'
    ON_PREMISES = 'on_premises'
    EXTERNAL = 'external'
    
    CHOICES = [
        (AZURE_AD, 'Azure AD Native'),
        (ON_PREMISES, 'On-Premises AD'),
        (EXTERNAL, 'External Directory'),
    ]


class MembershipTypeChoices(ChoiceSet):
    ASSIGNED = 'assigned'
    DYNAMIC = 'dynamic'
    
    CHOICES = [
        (ASSIGNED, 'Assigned'),
        (DYNAMIC, 'Dynamic'),
    ]


class AzureGroup(NetBoxModel):
    """
    Azure AD group representation in NetBox.
    """
    # Azure AD Identity
    object_id = models.CharField(
        max_length=36,
        unique=True,
        help_text="Azure AD object GUID"
    )
    name = models.CharField(
        max_length=256, 
        db_index=True,
        help_text='Group display name'
    )
    description = models.TextField(
        blank=True,
        help_text='Group description'
    )
    
    # Classification
    group_type = models.CharField(
        max_length=50,
        choices=GroupTypeChoices,
        db_index=True,
        default=GroupTypeChoices.SECURITY,
        help_text='Type of Azure AD group'
    )
    source = models.CharField(
        max_length=50,
        choices=GroupSourceChoices,
        db_index=True,
        default=GroupSourceChoices.AZURE_AD,
        help_text="Where group is mastered"
    )
    
    # Azure AD Properties
    is_security_enabled = models.BooleanField(
        default=False,
        help_text='Whether the group is security-enabled'
    )
    is_mail_enabled = models.BooleanField(
        default=False,
        help_text='Whether the group is mail-enabled'
    )
    mail = models.EmailField(
        blank=True,
        db_index=True,
        help_text='Group email address'
    )
    
    # Dynamic Membership
    membership_type = models.CharField(
        max_length=20,
        choices=MembershipTypeChoices,
        default=MembershipTypeChoices.ASSIGNED,
        help_text='Type of membership assignment'
    )
    membership_rule = models.TextField(
        blank=True,
        help_text="Azure AD dynamic membership rule"
    )
    
    # Statistics (denormalized for performance)
    member_count = models.IntegerField(
        default=0,
        help_text='Total number of members'
    )
    owner_count = models.IntegerField(
        default=0,
        help_text='Total number of owners'
    )
    
    # Azure AD Timestamps
    azure_created = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the group was created in Azure AD'
    )
    azure_modified = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the group was last modified in Azure AD'
    )
    
    # Plugin Tracking
    last_sync = models.DateTimeField(
        auto_now=True,
        help_text='When the group data was last synchronized'
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag for audit retention"
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Azure Group'
        verbose_name_plural = 'Azure Groups'
        indexes = [
            models.Index(fields=['source', 'group_type']),
            models.Index(fields=['last_sync']),
        ]

    def clean(self):
        # Validate UUID format for object_id
        if self.object_id:
            try:
                uuid.UUID(self.object_id)
            except ValueError:
                raise ValidationError({'object_id': 'Invalid UUID format'})
        
        # Enforce read-only for on-premises groups
        if self.pk and self.source == GroupSourceChoices.ON_PREMISES:
            original = AzureGroup.objects.get(pk=self.pk)
            allowed_fields = {'tags', 'custom_field_data', 'comments'}
            for field in self._meta.fields:
                if field.name not in allowed_fields:
                    if getattr(self, field.name) != getattr(original, field.name):
                        raise ValidationError(
                            f"Cannot modify {field.name}: On-premises groups are read-only"
                        )
    
    @property
    def is_stale(self):
        """Check if data is older than 24 hours."""
        return self.last_sync < timezone.now() - timedelta(hours=24)
    
    @property
    def can_modify(self):
        """Check if group properties can be modified."""
        return self.source != GroupSourceChoices.ON_PREMISES

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse('plugins:netbox_azure_groups:azuregroup', args=[self.pk])


class GroupMembership(NetBoxModel):
    """Many-to-many relationship between groups and contacts/devices."""
    
    group = models.ForeignKey(
        AzureGroup,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    
    # Member can be contact OR device
    contact = models.ForeignKey(
        'tenancy.Contact',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='azure_group_memberships'
    )
    device = models.ForeignKey(
        'dcim.Device',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='azure_group_memberships'
    )
    
    membership_type = models.CharField(
        max_length=20,
        choices=[
            ('direct', 'Direct Member'),
            ('nested', 'Via Nested Group'),
            ('dynamic', 'Dynamic Rule Match'),
        ],
        default='direct'
    )
    
    # For nested memberships, store the path
    nested_via = models.JSONField(
        blank=True,
        null=True,
        help_text="Group IDs traversed for nested membership"
    )
    
    
    class Meta:
        ordering = ['pk']
        unique_together = [
            ['group', 'contact'],
            ['group', 'device'],
        ]
        indexes = [
            models.Index(fields=['group', 'membership_type']),
        ]
        verbose_name = 'Group Membership'
        verbose_name_plural = 'Group Memberships'
    
    def clean(self):
        # Ensure either contact OR device, not both
        if not (self.contact or self.device):
            raise ValidationError("Must specify either contact or device")
        if self.contact and self.device:
            raise ValidationError("Cannot specify both contact and device")

    def __str__(self) -> str:
        member = self.contact or self.device
        return f'{self.group.name} - {member.name}'

    def get_absolute_url(self) -> str:
        # No detail view for memberships, return to group detail
        return self.group.get_absolute_url()


class GroupOwnership(NetBoxModel):
    """Group ownership tracking separate from membership."""
    
    group = models.ForeignKey(
        AzureGroup,
        on_delete=models.CASCADE,
        related_name='ownerships'
    )
    contact = models.ForeignKey(
        'tenancy.Contact',
        on_delete=models.CASCADE,
        related_name='owned_azure_groups'
    )
    assigned_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['pk']
        unique_together = [['group', 'contact']]
        verbose_name = 'Group Ownership'
        verbose_name_plural = 'Group Ownerships'

    def __str__(self) -> str:
        return f'{self.group.name} - Owner: {self.contact.name}'

    def get_absolute_url(self) -> str:
        # No detail view for ownerships, return to group detail
        return self.group.get_absolute_url()


# RBAC Extension Models

class RBACSystemChoices(ChoiceSet):
    AZURE_AD = 'azure_ad'
    ON_PREMISES_AD = 'on_premises_ad'
    FORTIGATE = 'fortigate'
    
    CHOICES = [
        (AZURE_AD, 'Azure Active Directory'),
        (ON_PREMISES_AD, 'On-Premises Active Directory'),
        (FORTIGATE, 'FortiGate Firewall'),
    ]


class RBACSystem(NetBoxModel):
    """Systems where RBAC permissions are managed and tracked."""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='System name (e.g., "Azure AD Production", "FortiGate HQ")'
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


class PermissionTypeChoices(ChoiceSet):
    READ = 'read'
    WRITE = 'write'
    EXECUTE = 'execute'
    DELETE = 'delete'
    ADMIN = 'admin'
    OWNER = 'owner'
    CUSTOM = 'custom'
    
    CHOICES = [
        (READ, 'Read'),
        (WRITE, 'Write'),
        (EXECUTE, 'Execute'),
        (DELETE, 'Delete'),
        (ADMIN, 'Administrator'),
        (OWNER, 'Owner'),
        (CUSTOM, 'Custom'),
    ]


class RBACPermission(NetBoxModel):
    """Individual permissions/rights in RBAC systems."""
    
    rbac_system = models.ForeignKey(
        RBACSystem,
        on_delete=models.CASCADE,
        related_name='permissions'
    )
    name = models.CharField(
        max_length=200,
        help_text='Permission or role name'
    )
    permission_type = models.CharField(
        max_length=20,
        choices=PermissionTypeChoices,
        default=PermissionTypeChoices.CUSTOM,
        help_text='Type of permission'
    )
    description = models.TextField(
        blank=True,
        help_text='What this permission grants access to'
    )
    resource_path = models.CharField(
        max_length=500,
        blank=True,
        help_text='Resource path or scope (e.g., "/subscriptions/...", "OU=Users")'
    )
    is_privileged = models.BooleanField(
        default=False,
        help_text='Whether this is a privileged/admin permission'
    )
    
    class Meta:
        ordering = ['rbac_system', 'name']
        unique_together = [['rbac_system', 'name']]
        verbose_name = 'RBAC Permission'
        verbose_name_plural = 'RBAC Permissions'
        indexes = [
            models.Index(fields=['rbac_system', 'is_privileged']),
        ]
    
    def __str__(self):
        return f'{self.rbac_system.name}: {self.name}'
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_azure_groups:rbacpermission', args=[self.pk])


class ServiceAccount(NetBoxModel):
    """Service accounts and non-human identities."""
    
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text='Service account name'
    )
    object_id = models.CharField(
        max_length=36,
        blank=True,
        help_text='Azure AD object GUID or system-specific ID'
    )
    principal_name = models.CharField(
        max_length=200,
        blank=True,
        help_text='UPN or principal name'
    )
    description = models.TextField(
        blank=True,
        help_text='Purpose and usage description'
    )
    owner_contact = models.ForeignKey(
        'tenancy.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_service_accounts',
        help_text='Contact responsible for this service account'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether account is active'
    )
    created_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the service account was created'
    )
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last authentication or usage'
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Service Account'
        verbose_name_plural = 'Service Accounts'
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['owner_contact']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_azure_groups:serviceaccount', args=[self.pk])


class AssignmentTypeChoices(ChoiceSet):
    DIRECT = 'direct'
    GROUP_INHERITED = 'group_inherited'
    ROLE_ASSIGNMENT = 'role_assignment'
    
    CHOICES = [
        (DIRECT, 'Direct Assignment'),
        (GROUP_INHERITED, 'Inherited via Group'),
        (ROLE_ASSIGNMENT, 'Role Assignment'),
    ]


class RBACAssignment(NetBoxModel):
    """Links permissions to assignees with metadata."""
    
    permission = models.ForeignKey(
        RBACPermission,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    
    # Assignee can be contact, device, or service account
    contact = models.ForeignKey(
        'tenancy.Contact',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rbac_assignments'
    )
    device = models.ForeignKey(
        'dcim.Device',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rbac_assignments'
    )
    service_account = models.ForeignKey(
        ServiceAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rbac_assignments'
    )
    
    assignment_type = models.CharField(
        max_length=20,
        choices=AssignmentTypeChoices,
        default=AssignmentTypeChoices.DIRECT,
        help_text='How the permission was assigned'
    )
    
    # Link to Azure group if inherited
    azure_group = models.ForeignKey(
        AzureGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rbac_assignments',
        help_text='Azure group providing this permission (if applicable)'
    )
    
    justification = models.TextField(
        blank=True,
        help_text='Business justification for this permission'
    )
    assigned_date = models.DateTimeField(
        auto_now_add=True,
        help_text='When permission was assigned'
    )
    expires_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When permission expires (optional)'
    )
    assigned_by = models.ForeignKey(
        'tenancy.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_rbac_permissions',
        help_text='Who assigned this permission'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether assignment is currently active'
    )
    
    class Meta:
        ordering = ['-assigned_date']
        verbose_name = 'RBAC Assignment'
        verbose_name_plural = 'RBAC Assignments'
        indexes = [
            models.Index(fields=['permission', 'is_active']),
            models.Index(fields=['expires_date']),
            models.Index(fields=['assigned_date']),
        ]
    
    def clean(self):
        # Ensure exactly one assignee is specified
        assignees = [self.contact, self.device, self.service_account]
        assignee_count = sum(1 for a in assignees if a is not None)
        
        if assignee_count == 0:
            raise ValidationError("Must specify one assignee (contact, device, or service account)")
        if assignee_count > 1:
            raise ValidationError("Cannot specify multiple assignees")
    
    @property
    def assignee(self):
        """Return the assigned entity (contact, device, or service account)."""
        return self.contact or self.device or self.service_account
    
    @property
    def is_expired(self):
        """Check if assignment has expired."""
        if not self.expires_date:
            return False
        return timezone.now() > self.expires_date
    
    @property
    def is_expiring_soon(self):
        """Check if assignment expires within 30 days."""
        if not self.expires_date:
            return False
        return timezone.now() + timedelta(days=30) > self.expires_date
    
    def __str__(self):
        assignee = self.assignee
        return f'{assignee.name if assignee else "Unknown"} - {self.permission.name}'
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_azure_groups:rbacassignment', args=[self.pk])
