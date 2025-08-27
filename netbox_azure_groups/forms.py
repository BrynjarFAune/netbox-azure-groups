from django import forms
from django.contrib.contenttypes.models import ContentType
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms import BootstrapMixin, DatePicker, DynamicModelChoiceField
from .models import AzureGroup, GroupMembership, GroupTypeChoices


class AzureGroupForm(NetBoxModelForm):
    class Meta:
        model = AzureGroup
        fields = [
            'name', 'description', 'object_id', 'mail', 'group_type',
            'is_security_enabled', 'is_mail_enabled', 'created_datetime', 'tags'
        ]
        widgets = {
            'created_datetime': DatePicker(),
        }


class AzureGroupFilterForm(NetBoxModelFilterSetForm):
    model = AzureGroup
    
    name = forms.CharField(required=False)
    object_id = forms.CharField(required=False)
    group_type = forms.MultipleChoiceField(
        choices=GroupTypeChoices,
        required=False
    )
    is_security_enabled = forms.NullBooleanField(required=False)
    is_mail_enabled = forms.NullBooleanField(required=False)


class GroupMembershipForm(NetBoxModelForm):
    group = DynamicModelChoiceField(queryset=AzureGroup.objects.all())
    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.filter(
            app_label__in=['tenancy', 'dcim'],
            model__in=['contact', 'device']
        ),
        empty_label='Select content type'
    )

    class Meta:
        model = GroupMembership
        fields = ['group', 'content_type', 'object_id', 'member_type', 'tags']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content_type'].widget.attrs.update({'class': 'form-control'})


class GroupMembershipFilterForm(NetBoxModelFilterSetForm):
    model = GroupMembership
    
    group_id = DynamicModelChoiceField(
        queryset=AzureGroup.objects.all(),
        required=False,
        label='Group'
    )
    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.filter(
            app_label__in=['tenancy', 'dcim'],
            model__in=['contact', 'device']
        ),
        required=False,
        empty_label='All'
    )
    member_type = forms.MultipleChoiceField(
        choices=GroupMembership._meta.get_field('member_type').choices,
        required=False
    )