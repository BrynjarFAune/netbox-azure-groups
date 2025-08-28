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
    
    # Group Memberships
    path('group-memberships/', views.GroupMembershipListView.as_view(), name='groupmembership_list'),
    path('group-memberships/add/', views.GroupMembershipEditView.as_view(), name='groupmembership_add'),
    path('group-memberships/<int:pk>/', views.GroupMembershipView.as_view(), name='groupmembership'),
    path('group-memberships/<int:pk>/edit/', views.GroupMembershipEditView.as_view(), name='groupmembership_edit'),
    path('group-memberships/<int:pk>/delete/', views.GroupMembershipDeleteView.as_view(), name='groupmembership_delete'),
    path('group-memberships/<int:pk>/changelog/', views.GroupMembershipChangeLogView.as_view(), name='groupmembership_changelog'),
    
    # API URLs
    path('api/', include('netbox_azure_groups.api.urls')),
]