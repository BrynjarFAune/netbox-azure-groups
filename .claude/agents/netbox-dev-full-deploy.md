# NetBox Full Deploy Agent

## Purpose
Complete end-to-end deployment workflow for Azure Groups plugin on NetBox dev server brynjar@10.0.123.5.

## Context
This agent handles the complete deployment pipeline for the netbox-azure-groups plugin on the NetBox development server.

## Workflow
1. Commit and push current Azure Groups plugin code to GitHub
2. Deploy plugin code to NetBox dev server
3. Run any pending migrations for Azure Groups
4. Restart NetBox containers
5. Verify everything is working correctly

## Usage
Invoke with `/netbox-dev-full-deploy` for complete Azure Groups plugin deployment pipeline.

## Commands to Execute
```bash
# 1. Commit and push Azure Groups plugin code
git add -A
git commit -m "feat: Enhance Azure Groups plugin with advanced features"
git push origin main

# 2. Deploy to NetBox dev server
ssh brynjar@10.0.123.5 "cd netbox-docker/plugins/netbox-azure-groups && git pull origin main"

# 3. Run Azure Groups migrations
ssh brynjar@10.0.123.5 "cd netbox-docker && docker compose exec netbox python manage.py makemigrations netbox_azure_groups"
ssh brynjar@10.0.123.5 "cd netbox-docker && docker compose exec netbox python manage.py migrate netbox_azure_groups"

# 4. Rebuild and restart NetBox containers
ssh brynjar@10.0.123.5 "cd netbox-docker && docker compose build netbox"
ssh brynjar@10.0.123.5 "cd netbox-docker && docker compose down && docker compose up -d"

# 5. Verify deployment on dev server
ssh brynjar@10.0.123.5 "cd netbox-docker && docker compose ps"
ssh brynjar@10.0.123.5 "cd netbox-docker && docker compose logs netbox | tail -20"
```

## Success Criteria
- Azure Groups plugin code committed and pushed to GitHub
- Plugin code updated on NetBox dev server
- Azure Groups migrations created and applied successfully
- Docker containers rebuilt and running
- NetBox accessible with Azure Groups plugin enhancements active

## Error Handling
- If migration fails, show detailed error output
- If container build fails, show build logs
- If containers don't start, show startup logs
- Provide rollback steps if deployment fails