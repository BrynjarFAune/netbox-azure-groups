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



# Access Control Extension Models

class ResourceTypeChoices(ChoiceSet):
    WEB_APPLICATION = 'web_application'
    DATABASE = 'database'
    API_SERVICE = 'api_service'
    FILE_SHARE = 'file_share'
    PHYSICAL_LOCATION = 'physical_location'
    NETWORK_DEVICE = 'network_device'
    CLOUD_RESOURCE = 'cloud_resource'
    OTHER = 'other'
    
    CHOICES = [
        (WEB_APPLICATION, 'Web Application'),
        (DATABASE, 'Database'),
        (API_SERVICE, 'API Service'),
        (FILE_SHARE, 'File Share'),
        (PHYSICAL_LOCATION, 'Physical Location'),
        (NETWORK_DEVICE, 'Network Device'),
        (CLOUD_RESOURCE, 'Cloud Resource'),
        (OTHER, 'Other'),
    ]


class CriticalityChoices(ChoiceSet):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'
    
    CHOICES = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
        (CRITICAL, 'Critical'),
    ]


class ProtectedResource(NetBoxModel):
    """Any resource that requires access control."""
    
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text='Resource name (e.g., "HR Database", "Server Room A", "Finance Portal")'
    )
    resource_type = models.CharField(
        max_length=50,
        choices=ResourceTypeChoices,
        help_text='Type of protected resource'
    )
    description = models.TextField(
        blank=True,
        help_text='Resource description and purpose'
    )
    
    # Optional technical details
    base_url = models.URLField(
        blank=True,
        help_text='Resource URL if applicable'
    )
    ip_addresses = models.JSONField(
        default=list,
        blank=True,
        help_text='IP addresses associated with this resource'
    )
    physical_location = models.CharField(
        max_length=200,
        blank=True,
        help_text='Physical location (e.g., "Building A, Room 101")'
    )
    
    # Business context
    owner_contact = models.ForeignKey(
        'tenancy.Contact',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_resources',
        help_text='Contact responsible for this resource'
    )
    business_unit = models.CharField(
        max_length=100,
        blank=True,
        help_text='Business unit that owns this resource'
    )
    criticality = models.CharField(
        max_length=20,
        choices=CriticalityChoices,
        default=CriticalityChoices.MEDIUM,
        help_text='Business criticality of this resource'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether resource is currently active'
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Protected Resource'
        verbose_name_plural = 'Protected Resources'
        indexes = [
            models.Index(fields=['resource_type', 'is_active']),
            models.Index(fields=['criticality']),
            models.Index(fields=['owner_contact']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_azure_groups:protectedresource', args=[self.pk])


class ControlTypeChoices(ChoiceSet):
    FORTIGATE_POLICY = 'fortigate_policy'
    BADGE_READER = 'badge_reader'
    VPN_CONFIG = 'vpn_config'
    APPLICATION_RBAC = 'application_rbac'
    NETWORK_ACL = 'network_acl'
    CLOUD_IAM = 'cloud_iam'
    MANUAL_PROCESS = 'manual_process'
    OTHER = 'other'
    
    CHOICES = [
        (FORTIGATE_POLICY, 'FortiGate Firewall Policy'),
        (BADGE_READER, 'Physical Badge Reader'),
        (VPN_CONFIG, 'VPN Configuration'),
        (APPLICATION_RBAC, 'Application Role'),
        (NETWORK_ACL, 'Network ACL'),
        (CLOUD_IAM, 'Cloud IAM Policy'),
        (MANUAL_PROCESS, 'Manual Process'),
        (OTHER, 'Other'),
    ]


class AccessLevelChoices(ChoiceSet):
    READ = 'read'
    WRITE = 'write'
    ADMIN = 'admin'
    FULL = 'full'
    PHYSICAL = 'physical'
    
    CHOICES = [
        (READ, 'Read Only'),
        (WRITE, 'Read/Write'),
        (ADMIN, 'Administrative'),
        (FULL, 'Full Access'),
        (PHYSICAL, 'Physical Access'),
    ]


class AccessControlMethod(NetBoxModel):
    """How access to a resource is controlled and enforced."""
    
    resource = models.ForeignKey(
        ProtectedResource,
        on_delete=models.CASCADE,
        related_name='access_methods'
    )
    
    # What enforces the access
    control_type = models.CharField(
        max_length=50,
        choices=ControlTypeChoices,
        help_text='Type of access control mechanism'
    )
    name = models.CharField(
        max_length=200,
        help_text='Control mechanism name (e.g., "Policy-42", "Door-Controller-A")'
    )
    description = models.TextField(
        blank=True,
        help_text='How this control method works'
    )
    
    # The key connection: which Azure group provides access
    azure_group = models.ForeignKey(
        AzureGroup,
        on_delete=models.CASCADE,
        related_name='enables_access_via',
        help_text='Azure group that provides access through this method'
    )
    
    # Access details
    access_level = models.CharField(
        max_length=20,
        choices=AccessLevelChoices,
        default=AccessLevelChoices.READ,
        help_text='Level of access granted'
    )
    
    # Technical details (flexible JSON for different control types)
    configuration = models.JSONField(
        default=dict,
        blank=True,
        help_text='Type-specific configuration details'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this control method is currently active'
    )
    last_verified = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When this configuration was last verified'
    )
    
    class Meta:
        ordering = ['resource', 'name']
        verbose_name = 'Access Control Method'
        verbose_name_plural = 'Access Control Methods'
        unique_together = [['resource', 'name']]
        indexes = [
            models.Index(fields=['resource', 'is_active']),
            models.Index(fields=['control_type']),
            models.Index(fields=['azure_group']),
        ]
    
    def __str__(self):
        return f'{self.resource.name}: {self.name}'
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_azure_groups:accesscontrolmethod', args=[self.pk])


class GrantedViaChoices(ChoiceSet):
    DIRECT_MEMBERSHIP = 'direct_membership'
    NESTED_MEMBERSHIP = 'nested_membership'
    INHERITED = 'inherited'
    
    CHOICES = [
        (DIRECT_MEMBERSHIP, 'Direct Group Membership'),
        (NESTED_MEMBERSHIP, 'Nested Group Membership'),
        (INHERITED, 'Inherited Permission'),
    ]


class AccessGrant(NetBoxModel):
    """Computed/tracked access grants showing the full access chain."""
    
    # The access chain: Resource ← Control Method ← Azure Group ← Contact
    resource = models.ForeignKey(
        ProtectedResource,
        on_delete=models.CASCADE,
        related_name='access_grants'
    )
    contact = models.ForeignKey(
        'tenancy.Contact',
        on_delete=models.CASCADE,
        related_name='access_grants'
    )
    azure_group = models.ForeignKey(
        AzureGroup,
        on_delete=models.CASCADE,
        related_name='access_grants'
    )
    control_method = models.ForeignKey(
        AccessControlMethod,
        on_delete=models.CASCADE,
        related_name='access_grants'
    )
    
    # Grant metadata
    access_level = models.CharField(
        max_length=20,
        choices=AccessLevelChoices,
        help_text='Level of access granted (inherited from control method)'
    )
    granted_via = models.CharField(
        max_length=30,
        choices=GrantedViaChoices,
        default=GrantedViaChoices.DIRECT_MEMBERSHIP,
        help_text='How the access was granted'
    )
    
    # Audit info
    first_granted = models.DateTimeField(
        auto_now_add=True,
        help_text='When access was first granted'
    )
    last_verified = models.DateTimeField(
        auto_now=True,
        help_text='When access was last verified'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether access is currently active'
    )
    
    class Meta:
        ordering = ['-first_granted']
        verbose_name = 'Access Grant'
        verbose_name_plural = 'Access Grants'
        unique_together = [['resource', 'contact', 'azure_group', 'control_method']]
        indexes = [
            models.Index(fields=['resource', 'is_active']),
            models.Index(fields=['contact', 'is_active']),
            models.Index(fields=['azure_group']),
            models.Index(fields=['first_granted']),
        ]
    
    def __str__(self):
        return f'{self.contact.name} → {self.resource.name} (via {self.azure_group.name})'
    
    def get_absolute_url(self):
        return reverse('plugins:netbox_azure_groups:accessgrant', args=[self.pk])
