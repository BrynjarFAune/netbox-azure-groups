# NetBox Deploy Agent

## Purpose
Deploy updated Azure Groups plugin code to the NetBox dev server at brynjar@10.0.123.5.

## Context
This agent is specifically for the netbox-azure-groups plugin development workflow on the NetBox development server.

## Workflow
1. Push current code to GitHub repository
2. SSH to brynjar@10.0.123.5 NetBox dev server
3. Navigate to netbox-docker/plugins/netbox-azure-groups/
4. Pull latest code from GitHub
5. Build new Docker image for NetBox
6. Restart all containers using docker compose
7. Verify the deployment was successful

## Usage
Invoke with `/netbox-dev-deploy` to deploy the current Azure Groups plugin state to the NetBox dev server.

## Commands to Execute
```bash
# Push to GitHub
git add -A
git commit -m "Deploy: Update Azure Groups plugin code"
git push origin main

# SSH and deploy to NetBox dev server
ssh brynjar@10.0.123.5 "cd netbox-docker/plugins/netbox-azure-groups && git pull origin main"
ssh brynjar@10.0.123.5 "cd netbox-docker && docker compose build netbox"
ssh brynjar@10.0.123.5 "cd netbox-docker && docker compose down && docker compose up -d"

# Verify deployment on dev server
ssh brynjar@10.0.123.5 "cd netbox-docker && docker compose ps"
```

## Success Criteria
- Code successfully pushed to GitHub
- Azure Groups plugin code updated on NetBox dev server
- Docker containers rebuilt and restarted
- NetBox accessible and Azure Groups plugin loaded correctly