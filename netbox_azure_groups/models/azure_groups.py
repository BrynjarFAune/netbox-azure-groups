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


