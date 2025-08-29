from django.urls import path, include

app_name = 'netbox_azure_groups'

urlpatterns = [
    # API URLs only for now - will add UI views once container starts
    path('api/', include('netbox_azure_groups.api.urls')),
]