# NetBox Migrate Agent

## Purpose
Handle Django migrations for the Azure Groups plugin on NetBox dev server brynjar@10.0.123.5.

## Context
This agent is specifically for managing database migrations for the netbox-azure-groups plugin on the NetBox development server.

## Workflow
1. SSH to brynjar@10.0.123.5 NetBox dev server
2. Navigate to netbox-docker/ directory
3. Execute migration commands inside the NetBox Docker container
4. Handle both creating and applying migrations for Azure Groups plugin
5. Provide clear status and error reporting

## Usage
- `/netbox-dev-migrate makemigrations` - Create new migrations for Azure Groups
- `/netbox-dev-migrate migrate` - Apply Azure Groups migrations
- `/netbox-dev-migrate showmigrations` - Show Azure Groups migration status

## Commands Available
```bash
# Create new migrations for Azure Groups plugin
ssh brynjar@10.0.123.5 "cd netbox-docker && docker compose exec netbox python manage.py makemigrations netbox_azure_groups"
ssh brynjar@10.0.123.5 "cd netbox-docker && docker compose exec netbox python manage.py makemigrations netbox_azure_groups --name enhance_azure_groups"

# Apply Azure Groups migrations
ssh brynjar@10.0.123.5 "cd netbox-docker && docker compose exec netbox python manage.py migrate netbox_azure_groups"
ssh brynjar@10.0.123.5 "cd netbox-docker && docker compose exec netbox python manage.py migrate netbox_azure_groups 0006_enhance_azure_groups"

# Check Azure Groups migration status
ssh brynjar@10.0.123.5 "cd netbox-docker && docker compose exec netbox python manage.py showmigrations netbox_azure_groups"

# Show all migrations (for debugging)
ssh brynjar@10.0.123.5 "cd netbox-docker && docker compose exec netbox python manage.py showmigrations"
```

## Success Criteria
- Successful SSH connection to NetBox dev server
- Migration commands execute without errors
- Azure Groups database schema updated correctly
- NetBox continues running after migration