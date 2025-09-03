#!/usr/bin/env python3
"""
Create test data for NetBox Azure Groups plugin
"""
import requests
import json
from datetime import datetime

# NetBox API configuration
NETBOX_URL = "http://10.0.123.5:8000"
API_TOKEN = "0123456789abcdef0123456789abcdef01234567"  # Replace with actual token

headers = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json",
}

def create_contacts():
    """Create test contacts in NetBox"""
    contacts_data = [
        {
            "name": "John Smith",
            "email": "john.smith@example.com",
            "title": "Database Administrator",
        },
        {
            "name": "Jane Doe", 
            "email": "jane.doe@example.com",
            "title": "Network Engineer",
        },
        {
            "name": "Bob Johnson",
            "email": "bob.johnson@example.com",
            "title": "Security Analyst",
        },
        {
            "name": "Alice Williams",
            "email": "alice.williams@example.com",
            "title": "DevOps Engineer",
        },
        {
            "name": "Charlie Brown",
            "email": "charlie.brown@example.com",
            "title": "IT Manager",
        }
    ]
    
    created_contacts = []
    for contact in contacts_data:
        try:
            response = requests.post(
                f"{NETBOX_URL}/api/tenancy/contacts/",
                headers=headers,
                json=contact
            )
            if response.status_code == 201:
                created_contacts.append(response.json())
                print(f"Created contact: {contact['name']}")
            else:
                print(f"Error creating contact {contact['name']}: {response.text}")
        except Exception as e:
            print(f"Exception creating contact: {e}")
    
    return created_contacts

def add_group_members():
    """Add members to existing Azure groups"""
    # Get existing groups
    response = requests.get(f"{NETBOX_URL}/api/plugins/azure-groups/azure-groups/", headers=headers)
    groups = response.json().get('results', [])
    
    # Get contacts
    response = requests.get(f"{NETBOX_URL}/api/tenancy/contacts/", headers=headers)
    contacts = response.json().get('results', [])
    
    if not groups:
        print("No Azure groups found")
        return
    
    if not contacts:
        print("No contacts found")
        return
    
    # Create memberships for first 3 groups
    memberships_created = []
    for i, group in enumerate(groups[:3]):
        for j, contact in enumerate(contacts[:3]):
            membership_data = {
                "group": group['id'],
                "contact": contact['id'],
                "is_owner": (i == 0 and j == 0),  # Make first contact owner of first group
                "membership_type": "direct"
            }
            
            try:
                response = requests.post(
                    f"{NETBOX_URL}/api/plugins/azure-groups/group-memberships/",
                    headers=headers,
                    json=membership_data
                )
                if response.status_code == 201:
                    print(f"Added {contact['name']} to group {group['name']}")
                    memberships_created.append(response.json())
            except Exception as e:
                print(f"Error adding membership: {e}")
    
    return memberships_created

def create_access_grants():
    """Create access grants for resources"""
    # Get protected resources
    response = requests.get(f"{NETBOX_URL}/api/plugins/azure-groups/protected-resources/", headers=headers)
    resources = response.json().get('results', [])
    
    # Get access control methods
    response = requests.get(f"{NETBOX_URL}/api/plugins/azure-groups/access-control-methods/", headers=headers)
    methods = response.json().get('results', [])
    
    # Get Azure groups
    response = requests.get(f"{NETBOX_URL}/api/plugins/azure-groups/azure-groups/", headers=headers)
    groups = response.json().get('results', [])
    
    # Get contacts
    response = requests.get(f"{NETBOX_URL}/api/tenancy/contacts/", headers=headers)
    contacts = response.json().get('results', [])
    
    if not all([resources, methods, groups, contacts]):
        print("Missing required data for access grants")
        return
    
    grants_created = []
    
    # Create grants for first resource and method
    if resources and methods:
        for contact in contacts[:3]:
            grant_data = {
                "resource": resources[0]['id'],
                "contact": contact['id'],
                "azure_group": groups[0]['id'] if groups else None,
                "control_method": methods[0]['id'] if methods else None,
                "access_level": "read",
                "granted_via": "direct_membership",
                "is_active": True
            }
            
            try:
                response = requests.post(
                    f"{NETBOX_URL}/api/plugins/azure-groups/access-grants/",
                    headers=headers,
                    json=grant_data
                )
                if response.status_code == 201:
                    print(f"Created access grant for {contact['name']}")
                    grants_created.append(response.json())
            except Exception as e:
                print(f"Error creating grant: {e}")
    
    return grants_created

def main():
    print("Creating test data for NetBox Azure Groups plugin...")
    
    # Create contacts
    print("\n1. Creating test contacts...")
    contacts = create_contacts()
    
    # Add members to groups
    print("\n2. Adding members to Azure groups...")
    memberships = add_group_members()
    
    # Create access grants
    print("\n3. Creating access grants...")
    grants = create_access_grants()
    
    print("\n✅ Test data creation complete!")
    print(f"Created {len(contacts)} contacts")
    print(f"Created {len(memberships)} group memberships")
    print(f"Created {len(grants)} access grants")

if __name__ == "__main__":
    main()