from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from .models import AzureGroup, GroupMembership, GroupOwnership
from .models.azure_groups import (
    GroupTypeChoices, GroupSourceChoices, MembershipTypeChoices,
    ProtectedResource, AccessControlMethod, AccessGrant, FortiGatePolicy,
    ResourceTypeChoices, CriticalityChoices, ControlTypeChoices, AccessLevelChoices
)


class AzureGroupForm(NetBoxModelForm):
    """Read-only form for Azure Groups - only allows viewing and deletion."""
    
    class Meta:
        model = AzureGroup
        fields = [
            'object_id', 'name', 'description', 'group_type', 'source',
            'is_security_enabled', 'is_mail_enabled', 'mail', 'membership_type', 
            'membership_rule', 'member_count', 'owner_count', 'azure_created',
            'azure_modified', 'tags'
        ]
        widgets = {
            'azure_created': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'azure_modified': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'membership_rule': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make ALL fields read-only except tags
        # Groups are immutable and managed by external systems
        readonly_fields = set(self.fields.keys()) - {'tags'}
        
        for field_name in readonly_fields:
            field = self.fields[field_name]
            field.disabled = True
            
            # Add visual styling and help text
            base_help = field.help_text or ''
            if self.instance.pk and self.instance.source == GroupSourceChoices.ON_PREMISES:
                field.help_text = f"{base_help} (Managed by On-Premises AD)".strip()
            else:
                field.help_text = f"{base_help} (Managed by Azure AD)".strip()
            
            # Add visual indicator
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({
                    'class': f"{field.widget.attrs.get('class', '')} bg-light text-muted".strip(),
                    'title': 'This field is read-only - groups are managed externally'
                })
        
        # Hide membership rule unless it's a dynamic group
        if self.instance.pk and self.instance.membership_type != MembershipTypeChoices.DYNAMIC:
            self.fields['membership_rule'].widget = forms.HiddenInput()


class AzureGroupFilterForm(NetBoxModelFilterSetForm):
    model = AzureGroup
    
    name = forms.CharField(required=False)
    object_id = forms.CharField(required=False)
    group_type = forms.MultipleChoiceField(
        choices=GroupTypeChoices.CHOICES,
        required=False
    )
    source = forms.MultipleChoiceField(
        choices=GroupSourceChoices.CHOICES,
        required=False
    )
    membership_type = forms.MultipleChoiceField(
        choices=MembershipTypeChoices.CHOICES,
        required=False
    )
    is_security_enabled = forms.BooleanField(required=False)
    is_mail_enabled = forms.BooleanField(required=False)
    is_deleted = forms.BooleanField(required=False)


class GroupMembershipForm(NetBoxModelForm):
    """Read-only form for Group Memberships - managed externally."""
    
    class Meta:
        model = GroupMembership
        fields = ['group', 'contact', 'device', 'membership_type', 'nested_via']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields read-only - memberships are managed externally
        for field_name, field in self.fields.items():
            field.disabled = True
            field.help_text = f"{field.help_text or ''} (Managed externally)".strip()


class GroupMembershipFilterForm(NetBoxModelFilterSetForm):
    model = GroupMembership
    
    group = forms.ModelChoiceField(
        queryset=AzureGroup.objects.all(),
        required=False,
        label='Group'
    )
    membership_type = forms.MultipleChoiceField(
        choices=[
            ('direct', 'Direct Member'),
            ('nested', 'Via Nested Group'), 
            ('dynamic', 'Dynamic Rule Match'),
        ],
        required=False
    )


class GroupOwnershipForm(NetBoxModelForm):
    """Read-only form for Group Ownerships - managed externally."""
    
    class Meta:
        model = GroupOwnership
        fields = ['group', 'contact']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields read-only - ownerships are managed externally
        for field_name, field in self.fields.items():
            field.disabled = True
            field.help_text = f"{field.help_text or ''} (Managed externally)".strip()


class GroupOwnershipFilterForm(NetBoxModelFilterSetForm):
    model = GroupOwnership
    
    group = forms.ModelChoiceField(
        queryset=AzureGroup.objects.all(),
        required=False,
        label='Group'
    )


# Access Control Forms

class ProtectedResourceForm(NetBoxModelForm):
    """Form for creating and editing Protected Resources."""
    
    class Meta:
        model = ProtectedResource
        fields = [
            'name', 'description', 'resource_type', 'environment',
            'server_name', 'resource_url', 'ip_addresses', 'physical_location',
            'owner_contact', 'business_unit', 'criticality', 'is_active', 'tags'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'ip_addresses': forms.Textarea(attrs={
                'rows': 2, 
                'placeholder': '["192.168.1.10", "192.168.1.11"]'
            }),
            'resource_url': forms.URLInput(attrs={
                'placeholder': 'https://example.com/resource'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add helpful placeholders and descriptions
        self.fields['name'].help_text = 'Descriptive name for this protected resource'
        self.fields['server_name'].help_text = 'Server hostname if applicable'
        self.fields['ip_addresses'].help_text = 'JSON list of IP addresses associated with this resource'
        self.fields['physical_location'].help_text = 'Physical location (e.g., "Building A, Room 101")'


class ProtectedResourceFilterForm(NetBoxModelFilterSetForm):
    model = ProtectedResource
    
    name = forms.CharField(required=False)
    resource_type = forms.MultipleChoiceField(
        choices=ResourceTypeChoices.CHOICES,
        required=False
    )
    environment = forms.CharField(required=False)
    criticality = forms.MultipleChoiceField(
        choices=CriticalityChoices.CHOICES,
        required=False
    )
    business_unit = forms.CharField(required=False)
    is_active = forms.BooleanField(required=False)