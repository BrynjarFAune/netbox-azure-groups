from django.urls import path, include
from . import views

app_name = 'netbox_azure_groups'

urlpatterns = [
    # Azure Groups
    path('azure-groups/', views.AzureGroupListView.as_view(), name='azuregroup_list'),
    path('azure-groups/add/', views.AzureGroupEditView.as_view(), name='azuregroup_add'),
    path('azure-groups/<int:pk>/', views.AzureGroupView.as_view(), name='azuregroup'),
    path('azure-groups/<int:pk>/edit/', views.AzureGroupEditView.as_view(), name='azuregroup_edit'),
    path('azure-groups/<int:pk>/delete/', views.AzureGroupDeleteView.as_view(), name='azuregroup_delete'),
    path('azure-groups/<int:pk>/changelog/', views.AzureGroupChangeLogView.as_view(), name='azuregroup_changelog'),
    
    # Contact Group Memberships
    path('contact-group-memberships/add/', views.ContactGroupMembershipEditView.as_view(), name='contactgroupmembership_add'),
    path('contact-group-memberships/<int:pk>/', views.ContactGroupMembershipView.as_view(), name='contactgroupmembership'),
    path('contact-group-memberships/<int:pk>/edit/', views.ContactGroupMembershipEditView.as_view(), name='contactgroupmembership_edit'),
    path('contact-group-memberships/<int:pk>/delete/', views.ContactGroupMembershipDeleteView.as_view(), name='contactgroupmembership_delete'),
    path('contact-group-memberships/<int:pk>/changelog/', views.ContactGroupMembershipChangeLogView.as_view(), name='contactgroupmembership_changelog'),
    
    # Device Group Memberships
    path('device-group-memberships/add/', views.DeviceGroupMembershipEditView.as_view(), name='devicegroupmembership_add'),
    path('device-group-memberships/<int:pk>/', views.DeviceGroupMembershipView.as_view(), name='devicegroupmembership'),
    path('device-group-memberships/<int:pk>/edit/', views.DeviceGroupMembershipEditView.as_view(), name='devicegroupmembership_edit'),
    path('device-group-memberships/<int:pk>/delete/', views.DeviceGroupMembershipDeleteView.as_view(), name='devicegroupmembership_delete'),
    path('device-group-memberships/<int:pk>/changelog/', views.DeviceGroupMembershipChangeLogView.as_view(), name='devicegroupmembership_changelog'),
    
    # Contact Group Ownerships  
    path('contact-group-ownerships/add/', views.ContactGroupOwnershipEditView.as_view(), name='contactgroupownership_add'),
    path('contact-group-ownerships/<int:pk>/', views.ContactGroupOwnershipView.as_view(), name='contactgroupownership'),
    path('contact-group-ownerships/<int:pk>/edit/', views.ContactGroupOwnershipEditView.as_view(), name='contactgroupownership_edit'),
    path('contact-group-ownerships/<int:pk>/delete/', views.ContactGroupOwnershipDeleteView.as_view(), name='contactgroupownership_delete'),
    path('contact-group-ownerships/<int:pk>/changelog/', views.ContactGroupOwnershipChangeLogView.as_view(), name='contactgroupownership_changelog'),
    
    # API URLs
    path('api/', include('netbox_azure_groups.api.urls')),
]