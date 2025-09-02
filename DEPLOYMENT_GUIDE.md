# NetBox Azure Groups Plugin - Deployment Guide

## Current State
- **API Layer**: ✅ Complete and deployed
- **FortiGate Integration**: ✅ Models created, needs migration
- **Database**: ✅ All access control tables exist
- **Policies**: ✅ 336 policies fetched and parsed

## Immediate Next Steps

### 1. Deploy FortiGate Model
The FortiGatePolicy model exists but needs database migration:

```bash
# Connect to server
ssh brynjar@10.0.123.5

# Create migration for FortiGate model
cd netbox-docker
docker compose exec netbox /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py makemigrations netbox_azure_groups

# Apply migration  
docker compose exec netbox /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py migrate netbox_azure_groups

# Restart to reload API
docker compose restart netbox
```

### 2. Import FortiGate Policies
Once migration is complete, import the parsed policies:

```bash
# Test API endpoint first
curl -s "http://10.0.123.5:8000/api/plugins/azure-groups/fortigate-policies/" | head -3

# Import policies (needs authentication token)
curl -X POST -H "Content-Type: application/json" -H "Authorization: Token YOUR_TOKEN" \
  http://10.0.123.5:8000/api/plugins/azure-groups/fortigate-policies/bulk-import/ \
  -d @fortigate_policies_parsed_TIMESTAMP.json
```

### 3. Test Complete System
Verify all endpoints work:

```bash
# Check all API endpoints
for endpoint in azure-groups protected-resources access-control-methods access-grants fortigate-policies; do
  echo "Testing $endpoint:"
  curl -s "http://10.0.123.5:8000/api/plugins/azure-groups/$endpoint/" | head -1
done
```

## Key API Endpoints

### Core Access Control
- `GET /api/plugins/azure-groups/protected-resources/` - Resources needing protection
- `POST /api/plugins/azure-groups/access-control-methods/` - Link groups to resources  
- `GET /api/plugins/azure-groups/access-grants/` - Who has access to what

### FortiGate Integration  
- `GET /api/plugins/azure-groups/fortigate-policies/` - All firewall policies
- `POST /api/plugins/azure-groups/fortigate-policies/bulk-import/` - Mass import
- `GET /api/plugins/azure-groups/fortigate-policies/statistics/` - Policy analytics

### Analytics
- `GET /api/plugins/azure-groups/access-grants/analytics/` - Access statistics
- `GET /api/plugins/azure-groups/azure-groups/{id}/provides-access-to/` - What resources a group enables
- `GET /api/plugins/azure-groups/protected-resources/{id}/who-has-access/` - Who can access a resource

## File Locations

### On Local Development Machine:
- `C:\Users\brynjar.aune\Proj\internal\netbox-plugin\aad-groups\` - Main project
- `fortigate_policies_raw.json` - Raw policy data from FortiGate
- `fortigate_policies_parsed_*.json` - Parsed policies ready for import
- `fortigate_import.py` - Policy parsing script

### On Server:
- `/home/brynjar/netbox-docker/plugins/netbox-azure-groups/` - Plugin code
- `/opt/netbox/netbox/netbox_azure_groups/` - Runtime plugin location (in container)

## Example Usage Workflow

1. **Create Protected Resource**:
```json
POST /api/plugins/azure-groups/protected-resources/
{
  "name": "HR Database",
  "resource_type": "database", 
  "criticality": "high",
  "owner_contact": 1
}
```

2. **Link FortiGate Policy to Resource**:
```json  
POST /api/plugins/azure-groups/access-control-methods/
{
  "resource": 1,
  "control_type": "fortigate_policy",
  "name": "Policy-42-HR-Access",
  "azure_group": 5,
  "access_level": "read"
}
```

3. **Query Access**:
```bash
# Who has access to HR Database?
GET /api/plugins/azure-groups/protected-resources/1/who-has-access/

# What can Azure group "HR-Staff" access?  
GET /api/plugins/azure-groups/azure-groups/5/provides-access-to/
```

This creates the complete access documentation chain: FortiGate Policy → Access Control Method → Protected Resource → User Access Grants.