from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase
from dcim.models import Device, DeviceType, Manufacturer, Site
from tenancy.models import Contact
from ..models import AzureGroup, GroupMembership


class AzureGroupTestCase(TestCase):

    def setUp(self):
        self.group_data = {
            'name': 'Test Group',
            'description': 'A test Azure AD group',
            'object_id': '12345678-1234-1234-1234-123456789012',
            'mail': 'test@example.com',
            'group_type': 'security',
            'is_security_enabled': True,
            'is_mail_enabled': False,
        }

    def test_azure_group_creation(self):
        """Test creating an Azure group"""
        group = AzureGroup.objects.create(**self.group_data)
        self.assertEqual(group.name, 'Test Group')
        self.assertEqual(group.object_id, '12345678-1234-1234-1234-123456789012')
        self.assertEqual(str(group), 'Test Group')

    def test_azure_group_unique_object_id(self):
        """Test that object_id must be unique"""
        AzureGroup.objects.create(**self.group_data)
        
        # Try to create another group with same object_id
        duplicate_data = self.group_data.copy()
        duplicate_data['name'] = 'Another Group'
        
        with self.assertRaises(ValidationError):
            group = AzureGroup(**duplicate_data)
            group.full_clean()

    def test_azure_group_get_absolute_url(self):
        """Test the get_absolute_url method"""
        group = AzureGroup.objects.create(**self.group_data)
        expected_url = f'/plugins/azure-groups/azure-groups/{group.pk}/'
        self.assertEqual(group.get_absolute_url(), expected_url)


class GroupMembershipTestCase(TestCase):

    def setUp(self):
        # Create test group
        self.group = AzureGroup.objects.create(
            name='Test Group',
            object_id='12345678-1234-1234-1234-123456789012',
            group_type='security'
        )
        
        # Create test contact
        self.contact = Contact.objects.create(
            name='Test Contact',
            email='contact@example.com'
        )
        
        # Create test device
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer', slug='test-manufacturer')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Test Device Type',
            slug='test-device-type'
        )
        site = Site.objects.create(name='Test Site', slug='test-site')
        self.device = Device.objects.create(
            name='Test Device',
            device_type=device_type,
            site=site
        )
        
        self.contact_ct = ContentType.objects.get_for_model(Contact)
        self.device_ct = ContentType.objects.get_for_model(Device)

    def test_group_membership_contact(self):
        """Test creating a group membership for a contact"""
        membership = GroupMembership.objects.create(
            group=self.group,
            content_type=self.contact_ct,
            object_id=self.contact.pk,
            member_type='direct'
        )
        
        self.assertEqual(membership.group, self.group)
        self.assertEqual(membership.member, self.contact)
        self.assertEqual(membership.member_type, 'direct')
        self.assertEqual(str(membership), f'{self.group.name} - {self.contact.name}')

    def test_group_membership_device(self):
        """Test creating a group membership for a device"""
        membership = GroupMembership.objects.create(
            group=self.group,
            content_type=self.device_ct,
            object_id=self.device.pk,
            member_type='nested'
        )
        
        self.assertEqual(membership.group, self.group)
        self.assertEqual(membership.member, self.device)
        self.assertEqual(membership.member_type, 'nested')

    def test_unique_membership_constraint(self):
        """Test that the unique constraint works"""
        # Create first membership
        GroupMembership.objects.create(
            group=self.group,
            content_type=self.contact_ct,
            object_id=self.contact.pk,
            member_type='direct'
        )
        
        # Try to create duplicate membership
        with self.assertRaises(Exception):  # IntegrityError in real usage
            GroupMembership.objects.create(
                group=self.group,
                content_type=self.contact_ct,
                object_id=self.contact.pk,
                member_type='nested'  # Different member_type, but same group+content_type+object_id
            )

    def test_group_membership_get_absolute_url(self):
        """Test the get_absolute_url method"""
        membership = GroupMembership.objects.create(
            group=self.group,
            content_type=self.contact_ct,
            object_id=self.contact.pk
        )
        expected_url = f'/plugins/azure-groups/group-memberships/{membership.pk}/'
        self.assertEqual(membership.get_absolute_url(), expected_url)