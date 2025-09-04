from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from .models import AzureGroup, GroupMembership, GroupOwnership, BusinessUnit, BusinessUnitMembership
from .models.azure_groups import (
    GroupTypeChoices, GroupSourceChoices, MembershipTypeChoices, BusinessUnitRoleChoices,
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


# Business Unit Forms

class BusinessUnitForm(NetBoxModelForm):
    """Form for creating and editing Business Units."""
    
    class Meta:
        model = BusinessUnit
        fields = ['name', 'description', 'parent', 'contact', 'is_active', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter parent choices to exclude self and descendants to prevent loops
        if self.instance and self.instance.pk:
            descendants = self._get_descendants(self.instance)
            self.fields['parent'].queryset = BusinessUnit.objects.exclude(
                pk__in=[self.instance.pk] + list(descendants.values_list('pk', flat=True))
            )
        
        # Add helpful descriptions
        self.fields['name'].help_text = 'Unique name for this business unit'
        self.fields['parent'].help_text = 'Parent business unit (creates hierarchy)'
        self.fields['contact'].help_text = 'Primary contact for this business unit'
    
    def _get_descendants(self, unit):
        """Get all descendants of a business unit to prevent circular references."""
        descendants = BusinessUnit.objects.filter(parent=unit)
        for child in descendants:
            descendants = descendants | self._get_descendants(child)
        return descendants


class BusinessUnitFilterForm(NetBoxModelFilterSetForm):
    model = BusinessUnit
    
    name = forms.CharField(required=False)
    parent = forms.ModelChoiceField(
        queryset=BusinessUnit.objects.all(),
        required=False,
        label='Parent Unit'
    )
    contact = forms.CharField(required=False, label='Contact Name')
    is_active = forms.BooleanField(required=False)


class BusinessUnitMembershipForm(NetBoxModelForm):
    """Form for creating and editing Business Unit Memberships."""
    
    class Meta:
        model = BusinessUnitMembership
        fields = ['business_unit', 'contact', 'role', 'start_date', 'end_date', 'is_active', 'notes', 'tags']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add helpful descriptions
        self.fields['business_unit'].help_text = 'Business unit for this membership'
        self.fields['contact'].help_text = 'Contact who is a member of this business unit'
        self.fields['role'].help_text = 'Role of the contact within this business unit'
        self.fields['start_date'].help_text = 'When this membership started (optional)'
        self.fields['end_date'].help_text = 'When this membership ends/ended (optional)'
        self.fields['notes'].help_text = 'Additional notes about this membership'
        
        # If we have a business_unit from URL params, set it as initial
        if 'initial' in kwargs and 'business_unit' in kwargs['initial']:
            self.fields['business_unit'].initial = kwargs['initial']['business_unit']


class BusinessUnitMembershipFilterForm(NetBoxModelFilterSetForm):
    model = BusinessUnitMembership
    
    business_unit = forms.ModelChoiceField(
        queryset=BusinessUnit.objects.all(),
        required=False,
        label='Business Unit'
    )
    contact = forms.CharField(required=False, label='Contact Name')
    role = forms.MultipleChoiceField(
        choices=BusinessUnitRoleChoices.CHOICES,
        required=False
    )
    is_active = forms.BooleanField(required=False)
    
    # Date range filters
    start_date_after = forms.DateField(
        required=False,
        label='Start Date After',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    start_date_before = forms.DateField(
        required=False,
        label='Start Date Before',
        widget=forms.DateInput(attrs={'type': 'date'})
    )


# Access Control Forms

class ProtectedResourceForm(NetBoxModelForm):
    """Form for creating and editing Protected Resources."""
    
    class Meta:
        model = ProtectedResource
        fields = [
            'name', 'description', 'resource_type', 'base_url',
            'ip_addresses', 'site', 'location', 'physical_location',
            'owner_contact', 'business_unit', 'criticality', 'is_active', 'tags'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'ip_addresses': forms.Textarea(attrs={
                'rows': 2, 
                'placeholder': '["server1.example.com", "server2.example.com"]'
            }),
            'base_url': forms.URLInput(attrs={
                'placeholder': 'https://example.com/resource'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add helpful placeholders and descriptions
        self.fields['name'].help_text = 'Descriptive name for this protected resource'
        self.fields['base_url'].help_text = 'Base URL for this resource if applicable'
        self.fields['ip_addresses'].help_text = 'JSON list of IP addresses associated with this resource'
        self.fields['physical_location'].help_text = 'Physical location (e.g., "Building A, Room 101")'


class ProtectedResourceFilterForm(NetBoxModelFilterSetForm):
    model = ProtectedResource
    
    name = forms.CharField(required=False)
    resource_type = forms.MultipleChoiceField(
        choices=ResourceTypeChoices.CHOICES,
        required=False
    )
    criticality = forms.MultipleChoiceField(
        choices=CriticalityChoices.CHOICES,
        required=False
    )
    business_unit = forms.CharField(required=False)
    is_active = forms.BooleanField(required=False)


class AccessControlMethodForm(NetBoxModelForm):
    """Form for creating and editing Access Control Methods."""
    
    # Add a helper field for FortiGate policy selection
    fortigate_policy = forms.ModelChoiceField(
        queryset=FortiGatePolicy.objects.all(),
        required=False,
        help_text='Select a FortiGate policy for firewall-based access control',
        empty_label='-- Select FortiGate Policy --'
    )
    
    class Meta:
        model = AccessControlMethod
        fields = [
            'resource', 'control_type', 'name', 'description', 'azure_group',
            'access_level', 'configuration', 'is_active', 'last_verified', 'tags'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'configuration': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': '{"policy_id": 123, "additional_settings": {}}'
            }),
            'last_verified': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add helpful descriptions
        self.fields['name'].help_text = 'Name of the control mechanism (e.g., "Policy-42", "Door-A")'
        self.fields['configuration'].help_text = 'JSON configuration specific to this control type'
        
        # Group resources by type for better UX
        if 'resource' in self.fields:
            self.fields['resource'].queryset = ProtectedResource.objects.select_related('owner_contact')
        
        # Group Azure groups by type 
        if 'azure_group' in self.fields:
            self.fields['azure_group'].queryset = AzureGroup.objects.filter(is_security_enabled=True)
        
        # If editing existing FortiGate policy method, populate the helper field
        if self.instance.pk and self.instance.control_type == 'fortigate_policy':
            try:
                policy_id = self.instance.configuration.get('policy_id')
                if policy_id:
                    policy = FortiGatePolicy.objects.get(policy_id=policy_id)
                    self.fields['fortigate_policy'].initial = policy
            except (FortiGatePolicy.DoesNotExist, KeyError):
                pass
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle FortiGate policy helper field
        if self.cleaned_data.get('fortigate_policy') and instance.control_type == 'fortigate_policy':
            policy = self.cleaned_data['fortigate_policy']
            # Auto-populate configuration with policy ID
            if not instance.configuration:
                instance.configuration = {}
            instance.configuration['policy_id'] = policy.policy_id
            
            # Auto-populate name if empty
            if not instance.name:
                instance.name = f"Policy-{policy.policy_id}"
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance


class AccessControlMethodFilterForm(NetBoxModelFilterSetForm):
    model = AccessControlMethod
    
    resource = forms.ModelChoiceField(
        queryset=ProtectedResource.objects.all(),
        required=False,
        label='Protected Resource'
    )
    control_type = forms.MultipleChoiceField(
        choices=ControlTypeChoices.CHOICES,
        required=False
    )
    azure_group = forms.ModelChoiceField(
        queryset=AzureGroup.objects.all(),
        required=False,
        label='Azure Group'
    )
    access_level = forms.MultipleChoiceField(
        choices=AccessLevelChoices.CHOICES,
        required=False
    )
    is_active = forms.BooleanField(required=False)


class FortiGatePolicyFilterForm(NetBoxModelFilterSetForm):
    model = FortiGatePolicy
    
    policy_id = forms.IntegerField(required=False, label='Policy ID')
    name = forms.CharField(required=False)
    action = forms.MultipleChoiceField(
        choices=[('accept', 'Accept'), ('deny', 'Deny'), ('ipsec', 'IPSec')],
        required=False
    )
    status = forms.MultipleChoiceField(
        choices=[('enable', 'Enabled'), ('disable', 'Disabled')],
        required=False
    )
    nat_enabled = forms.BooleanField(required=False, label='NAT Enabled')
    utm_status = forms.MultipleChoiceField(
        choices=[('enable', 'Enabled'), ('disable', 'Disabled')],
        required=False,
        label='UTM Status'
    )
    fortigate_host = forms.CharField(required=False, label='FortiGate Host')
    
    # Special text search field for AI descriptions
    description_search = forms.CharField(
        required=False, 
        label='Description Search',
        help_text='Search in AI-generated policy descriptions'
    )


class AccessGrantForm(NetBoxModelForm):
    """Form for creating and editing Access Grants."""
    
    class Meta:
        model = AccessGrant
        fields = [
            'resource', 'contact', 'azure_group', 'control_method',
            'access_level', 'granted_via', 'is_active', 'tags'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add helpful help text
        self.fields['resource'].help_text = 'The protected resource being accessed'
        self.fields['contact'].help_text = 'The NetBox contact receiving access'
        self.fields['azure_group'].help_text = 'The Azure AD group granting access'
        self.fields['control_method'].help_text = 'The access control method defining the rules'
        self.fields['access_level'].help_text = 'Level of access being granted'
        self.fields['granted_via'].help_text = 'Method by which access was granted'
        
        # Filter choices based on relationships
        if self.instance and self.instance.pk:
            # When editing, show the current relationships
            self.fields['control_method'].queryset = AccessControlMethod.objects.filter(
                resource=self.instance.resource
            )
        else:
            # When creating, show all available control methods
            self.fields['control_method'].queryset = AccessControlMethod.objects.all()


class AccessGrantFilterForm(NetBoxModelFilterSetForm):
    model = AccessGrant
    
    resource = forms.ModelChoiceField(
        queryset=ProtectedResource.objects.all(),
        required=False
    )
    contact = forms.CharField(required=False, label='Contact Name')
    azure_group = forms.ModelChoiceField(
        queryset=AzureGroup.objects.all(),
        required=False
    )
    control_method = forms.ModelChoiceField(
        queryset=AccessControlMethod.objects.all(),
        required=False
    )
    access_level = forms.MultipleChoiceField(
        choices=AccessLevelChoices.CHOICES,
        required=False
    )
    granted_via = forms.MultipleChoiceField(
        choices=[
            ('direct_membership', 'Direct Membership'),
            ('nested_group', 'Nested Group'),
            ('dynamic_rule', 'Dynamic Rule'),
        ],
        required=False
    )
    is_active = forms.BooleanField(required=False)