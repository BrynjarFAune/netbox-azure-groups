from django.urls import path, include
from . import views

app_name = 'netbox_azure_groups'

urlpatterns = [
    # Azure Groups - View Only (no add/edit)
    path('azure-groups/', views.AzureGroupListView.as_view(), name='azuregroup_list'),
    path('azure-groups/<int:pk>/', views.AzureGroupView.as_view(), name='azuregroup'),
    path('azure-groups/<int:pk>/delete/', views.AzureGroupDeleteView.as_view(), name='azuregroup_delete'),
    path('azure-groups/<int:pk>/changelog/', views.AzureGroupChangeLogView.as_view(), name='azuregroup_changelog'),
    
    # Protected Resources - Full CRUD
    path('protected-resources/', views.ProtectedResourceListView.as_view(), name='protectedresource_list'),
    path('protected-resources/<int:pk>/', views.ProtectedResourceView.as_view(), name='protectedresource'),
    path('protected-resources/add/', views.ProtectedResourceEditView.as_view(), name='protectedresource_add'),
    path('protected-resources/<int:pk>/edit/', views.ProtectedResourceEditView.as_view(), name='protectedresource_edit'),
    path('protected-resources/<int:pk>/delete/', views.ProtectedResourceDeleteView.as_view(), name='protectedresource_delete'),
    path('protected-resources/<int:pk>/changelog/', views.ProtectedResourceChangeLogView.as_view(), name='protectedresource_changelog'),
    
    # Access Control Methods - Full CRUD
    path('access-control-methods/', views.AccessControlMethodListView.as_view(), name='accesscontrolmethod_list'),
    path('access-control-methods/<int:pk>/', views.AccessControlMethodView.as_view(), name='accesscontrolmethod'),
    path('access-control-methods/add/', views.AccessControlMethodEditView.as_view(), name='accesscontrolmethod_add'),
    path('access-control-methods/<int:pk>/edit/', views.AccessControlMethodEditView.as_view(), name='accesscontrolmethod_edit'),
    path('access-control-methods/<int:pk>/delete/', views.AccessControlMethodDeleteView.as_view(), name='accesscontrolmethod_delete'),
    path('access-control-methods/<int:pk>/changelog/', views.AccessControlMethodChangeLogView.as_view(), name='accesscontrolmethod_changelog'),
    
    # API URLs
    path('api/', include('netbox_azure_groups.api.urls')),
]