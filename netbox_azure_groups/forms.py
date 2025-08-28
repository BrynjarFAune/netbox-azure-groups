from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from .models import AzureGroup, GroupTypeChoices, ContactGroupMembership, ContactGroupOwnership, DeviceGroupMembership


class AzureGroupForm(NetBoxModelForm):
    class Meta:
        model = AzureGroup
        fields = [
            'name', 'description', 'object_id', 'mail', 'group_type',
            'is_security_enabled', 'is_mail_enabled', 'created_datetime', 'tags'
        ]
        widgets = {
            'created_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class AzureGroupFilterForm(NetBoxModelFilterSetForm):
    model = AzureGroup
    
    name = forms.CharField(required=False)
    object_id = forms.CharField(required=False)
    group_type = forms.MultipleChoiceField(
        choices=GroupTypeChoices.CHOICES,
        required=False
    )
    is_security_enabled = forms.BooleanField(required=False)
    is_mail_enabled = forms.BooleanField(required=False)


class ContactGroupMembershipForm(NetBoxModelForm):
    class Meta:
        model = ContactGroupMembership
        fields = ['group', 'contact', 'member_type', 'tags']


class ContactGroupMembershipFilterForm(NetBoxModelFilterSetForm):
    model = ContactGroupMembership
    
    group = forms.ModelChoiceField(
        queryset=AzureGroup.objects.all(),
        required=False,
        label='Group'
    )
    contact = forms.ModelChoiceField(
        queryset=None,  # Will be set dynamically
        required=False,
        label='Contact'
    )
    member_type = forms.MultipleChoiceField(
        choices=ContactGroupMembership._meta.get_field('member_type').choices,
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from tenancy.models import Contact
        self.fields['contact'].queryset = Contact.objects.all()


class DeviceGroupMembershipForm(NetBoxModelForm):
    class Meta:
        model = DeviceGroupMembership
        fields = ['group', 'device', 'member_type', 'tags']


class DeviceGroupMembershipFilterForm(NetBoxModelFilterSetForm):
    model = DeviceGroupMembership
    
    group = forms.ModelChoiceField(
        queryset=AzureGroup.objects.all(),
        required=False,
        label='Group'
    )
    device = forms.ModelChoiceField(
        queryset=None,  # Will be set dynamically
        required=False,
        label='Device'
    )
    member_type = forms.MultipleChoiceField(
        choices=DeviceGroupMembership._meta.get_field('member_type').choices,
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from dcim.models import Device
        self.fields['device'].queryset = Device.objects.all()


class ContactGroupOwnershipForm(NetBoxModelForm):
    class Meta:
        model = ContactGroupOwnership
        fields = ['group', 'contact', 'tags']


class ContactGroupOwnershipFilterForm(NetBoxModelFilterSetForm):
    model = ContactGroupOwnership
    
    group = forms.ModelChoiceField(
        queryset=AzureGroup.objects.all(),
        required=False,
        label='Group'
    )
    contact = forms.ModelChoiceField(
        queryset=None,  # Will be set dynamically
        required=False,
        label='Contact'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from tenancy.models import Contact
        self.fields['contact'].queryset = Contact.objects.all()