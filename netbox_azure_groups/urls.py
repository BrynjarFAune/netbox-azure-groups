from django.urls import path, include
from . import views

app_name = 'netbox_azure_groups'

urlpatterns = [
    path('azure-groups/', views.AzureGroupListView.as_view(), name='azuregroup_list'),
    path('azure-groups/add/', views.AzureGroupEditView.as_view(), name='azuregroup_add'),
    path('azure-groups/<int:pk>/', views.AzureGroupView.as_view(), name='azuregroup_detail'),
    path('azure-groups/<int:pk>/edit/', views.AzureGroupEditView.as_view(), name='azuregroup_edit'),
    path('azure-groups/<int:pk>/delete/', views.AzureGroupDeleteView.as_view(), name='azuregroup_delete'),
    
    path('group-memberships/', views.GroupMembershipListView.as_view(), name='groupmembership_list'),
    path('group-memberships/add/', views.GroupMembershipEditView.as_view(), name='groupmembership_add'),
    path('group-memberships/<int:pk>/', views.GroupMembershipView.as_view(), name='groupmembership_detail'),
    path('group-memberships/<int:pk>/edit/', views.GroupMembershipEditView.as_view(), name='groupmembership_edit'),
    path('group-memberships/<int:pk>/delete/', views.GroupMembershipDeleteView.as_view(), name='groupmembership_delete'),
    
    # API URLs
    path('api/', include('netbox_azure_groups.api.urls')),
]