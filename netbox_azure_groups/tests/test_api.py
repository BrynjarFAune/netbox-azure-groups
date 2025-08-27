from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from dcim.models import Device, DeviceType, Manufacturer, Site
from tenancy.models import Contact
from users.models import User
from ..models import AzureGroup, GroupMembership


class AzureGroupAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.client.force_authenticate(user=self.user)
        
        self.group_data = {
            'name': 'Test Group',
            'description': 'A test Azure AD group',
            'object_id': '12345678-1234-1234-1234-123456789012',
            'mail': 'test@example.com',
            'group_type': 'security',
            'is_security_enabled': True,
            'is_mail_enabled': False,
        }

    def test_get_azure_groups_list(self):
        """Test retrieving a list of Azure groups"""
        group = AzureGroup.objects.create(**self.group_data)
        url = reverse('plugins-api:netbox_azure_groups-api:azuregroup-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Group')

    def test_get_azure_group_detail(self):
        """Test retrieving a single Azure group"""
        group = AzureGroup.objects.create(**self.group_data)
        url = reverse('plugins-api:netbox_azure_groups-api:azuregroup-detail', kwargs={'pk': group.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Group')
        self.assertEqual(response.data['object_id'], '12345678-1234-1234-1234-123456789012')

    def test_create_azure_group(self):
        """Test creating an Azure group via API"""
        url = reverse('plugins-api:netbox_azure_groups-api:azuregroup-list')
        response = self.client.post(url, self.group_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(AzureGroup.objects.filter(name='Test Group').exists())

    def test_update_azure_group(self):
        """Test updating an Azure group via API"""
        group = AzureGroup.objects.create(**self.group_data)
        url = reverse('plugins-api:netbox_azure_groups-api:azuregroup-detail', kwargs={'pk': group.pk})
        
        updated_data = self.group_data.copy()
        updated_data['name'] = 'Updated Group'
        response = self.client.put(url, updated_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        group.refresh_from_db()
        self.assertEqual(group.name, 'Updated Group')

    def test_delete_azure_group(self):
        """Test deleting an Azure group via API"""
        group = AzureGroup.objects.create(**self.group_data)
        url = reverse('plugins-api:netbox_azure_groups-api:azuregroup-detail', kwargs={'pk': group.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(AzureGroup.objects.filter(pk=group.pk).exists())


class GroupMembershipAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.client.force_authenticate(user=self.user)
        
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
        
        self.contact_ct = ContentType.objects.get_for_model(Contact)

    def test_get_memberships_list(self):
        """Test retrieving a list of group memberships"""
        membership = GroupMembership.objects.create(
            group=self.group,
            content_type=self.contact_ct,
            object_id=self.contact.pk,
            member_type='direct'
        )
        
        url = reverse('plugins-api:netbox_azure_groups-api:groupmembership-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['group_id'], self.group.pk)

    def test_get_membership_detail(self):
        """Test retrieving a single group membership"""
        membership = GroupMembership.objects.create(
            group=self.group,
            content_type=self.contact_ct,
            object_id=self.contact.pk,
            member_type='direct'
        )
        
        url = reverse('plugins-api:netbox_azure_groups-api:groupmembership-detail', kwargs={'pk': membership.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['group_id'], self.group.pk)
        self.assertEqual(response.data['object_id'], self.contact.pk)

    def test_create_membership(self):
        """Test creating a group membership via API"""
        url = reverse('plugins-api:netbox_azure_groups-api:groupmembership-list')
        data = {
            'group_id': self.group.pk,
            'content_type': self.contact_ct.pk,
            'object_id': self.contact.pk,
            'member_type': 'direct'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(GroupMembership.objects.filter(
            group=self.group,
            content_type=self.contact_ct,
            object_id=self.contact.pk
        ).exists())

    def test_delete_membership(self):
        """Test deleting a group membership via API"""
        membership = GroupMembership.objects.create(
            group=self.group,
            content_type=self.contact_ct,
            object_id=self.contact.pk,
            member_type='direct'
        )
        
        url = reverse('plugins-api:netbox_azure_groups-api:groupmembership-detail', kwargs={'pk': membership.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(GroupMembership.objects.filter(pk=membership.pk).exists())