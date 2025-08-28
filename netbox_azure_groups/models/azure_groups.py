from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from utilities.choices import ChoiceSet


class GroupTypeChoices(ChoiceSet):
    SECURITY = 'security'
    DISTRIBUTION = 'distribution'
    MICROSOFT365 = 'microsoft365'
    
    CHOICES = [
        (SECURITY, 'Security'),
        (DISTRIBUTION, 'Distribution'),
        (MICROSOFT365, 'Microsoft 365'),
    ]


class AzureGroup(NetBoxModel):
    """
    Represents an Azure AD security group
    """
    name = models.CharField(
        max_length=255,
        help_text='Group display name'
    )
    description = models.TextField(
        blank=True,
        help_text='Group description'
    )
    object_id = models.CharField(
        max_length=36,
        unique=True,
        help_text='Azure AD Object ID (GUID)'
    )
    mail = models.EmailField(
        blank=True,
        help_text='Group email address'
    )
    group_type = models.CharField(
        max_length=20,
        choices=GroupTypeChoices,
        default=GroupTypeChoices.SECURITY,
        help_text='Type of Azure AD group'
    )
    is_security_enabled = models.BooleanField(
        default=True,
        help_text='Whether the group is security-enabled'
    )
    is_mail_enabled = models.BooleanField(
        default=False,
        help_text='Whether the group is mail-enabled'
    )
    created_datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the group was created in Azure AD'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Azure Group'
        verbose_name_plural = 'Azure Groups'

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse('plugins:netbox_azure_groups:azuregroup', args=[self.pk])


class ContactGroupOwnership(NetBoxModel):
    """
    Represents ownership of an Azure AD group by a Contact
    """
    group = models.ForeignKey(
        AzureGroup,
        on_delete=models.CASCADE,
        related_name='contact_ownerships'
    )
    contact = models.ForeignKey(
        'tenancy.Contact',
        on_delete=models.CASCADE,
        related_name='azure_group_ownerships'
    )
    
    class Meta:
        ordering = ['group__name']
        verbose_name = 'Contact Group Ownership'
        verbose_name_plural = 'Contact Group Ownerships'
        unique_together = ['group', 'contact']

    def __str__(self) -> str:
        return f'{self.group.name} - Owner: {self.contact.name}'

    def get_absolute_url(self) -> str:
        return reverse('plugins:netbox_azure_groups:contactgroupownership', args=[self.pk])


class ContactGroupMembership(NetBoxModel):
    """
    Represents membership of a Contact in an Azure AD group
    """
    group = models.ForeignKey(
        AzureGroup,
        on_delete=models.CASCADE,
        related_name='contact_memberships'
    )
    contact = models.ForeignKey(
        'tenancy.Contact',
        on_delete=models.CASCADE,
        related_name='azure_group_memberships'
    )
    
    # Azure AD membership metadata
    member_type = models.CharField(
        max_length=20,
        choices=[
            ('direct', 'Direct Member'),
            ('nested', 'Nested Member'),
        ],
        default='direct',
        help_text='Type of group membership'
    )
    
    class Meta:
        ordering = ['group__name']
        verbose_name = 'Contact Group Membership'
        verbose_name_plural = 'Contact Group Memberships'
        unique_together = ['group', 'contact']

    def __str__(self) -> str:
        return f'{self.group.name} - {self.contact.name}'

    def get_absolute_url(self) -> str:
        return reverse('plugins:netbox_azure_groups:contactgroupmembership', args=[self.pk])


class DeviceGroupMembership(NetBoxModel):
    """
    Represents membership of a Device in an Azure AD group
    """
    group = models.ForeignKey(
        AzureGroup,
        on_delete=models.CASCADE,
        related_name='device_memberships'
    )
    device = models.ForeignKey(
        'dcim.Device',
        on_delete=models.CASCADE,
        related_name='azure_group_memberships'
    )
    
    # Azure AD membership metadata
    member_type = models.CharField(
        max_length=20,
        choices=[
            ('direct', 'Direct Member'),
            ('nested', 'Nested Member'),
        ],
        default='direct',
        help_text='Type of group membership'
    )
    
    class Meta:
        ordering = ['group__name']
        verbose_name = 'Device Group Membership'
        verbose_name_plural = 'Device Group Memberships'
        unique_together = ['group', 'device']

    def __str__(self) -> str:
        return f'{self.group.name} - {self.device.name}'

    def get_absolute_url(self) -> str:
        return reverse('plugins:netbox_azure_groups:devicegroupmembership', args=[self.pk])