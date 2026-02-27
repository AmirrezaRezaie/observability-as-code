# Grafana Dashboard Manager CLI - Quick Reference

## Setup

```bash
# Set environment variables (recommended)
export GRAFANA_URL="http://localhost:3000"
export GRAFANA_API_KEY="your-api-key-here"

# Or pass directly to each command
python cli.py --url http://localhost:3000 --api-key your-key <command>
```

## Folder Commands

```bash
# List all folders
python cli.py folder list

# Show complete folder tree
python cli.py folder tree

# Show tree for specific folder
python cli.py folder tree --uid "Overview"

# Create folder
python cli.py folder create "Monitoring" --uid monitoring

# List dashboards in folder
python cli.py folder list-dashboards Overview

# List dashboards recursively (including sub-folders)
python cli.py folder list-dashboards Overview --recursive

# In JSON format
python cli.py folder list-dashboards Overview --recursive --json
```

## Apply Operations to Folder Tree

```bash
# Add tag to all dashboards in folder tree
python cli.py folder apply Overview add-tag "production"

# Remove tag from all dashboards
python cli.py folder apply Overview remove-tag "deprecated"

# Add datasource to all dashboards
python cli.py folder apply Monitoring add-datasource "Prometheus-Prod"

# Replace datasource in all dashboards (format: old,new)
python cli.py folder apply Overview replace-datasource "Prometheus-Old,Prometheus-New"

# Add variable to all dashboards (format: name,query,datasource_uid)
python cli.py folder apply Monitoring add-variable "env,label_values(environment),ds-uid"

# Only apply to this folder (not sub-folders)
python cli.py folder apply Overview add-tag "staging" --no-recursive
```

## Dashboard Commands

```bash
# List all dashboards
python cli.py dashboard list

# List dashboards in folder
python cli.py dashboard list --folder Overview

# Get dashboard details (by UID or title)
python cli.py dashboard get 5751d9b9-be62-46f7-ae38-91b2902c444d
python cli.py dashboard get "App Service - Overview Dashboard"

# Get dashboard as JSON
python cli.py dashboard get dashboard-uid --json

# Create dashboard
python cli.py dashboard create "My Dashboard" --folder Monitoring --tags prod,monitoring

# Duplicate dashboard
python cli.py dashboard duplicate source-uid "Staging Dashboard" --folder staging

# Export dashboard
python cli.py dashboard export dashboard-uid backups/dashboard.json

# Delete dashboard
python cli.py dashboard delete dashboard-uid

# Delete without confirmation
python cli.py dashboard delete dashboard-uid --force
```

## Datasource Commands

```bash
# Add datasource to dashboard
python cli.py ds add dashboard-uid Prometheus-Prod

# Replace datasource
python cli.py ds replace dashboard-uid Prometheus-Old Prometheus-New

# Remove datasource
python cli.py ds remove dashboard-uid Prometheus-Test

# List datasources in dashboard
python cli.py ds list dashboard-uid
```

## Panel Commands

```bash
# Add timeseries panel
python cli.py panel add-timeseries dashboard-uid "CPU Usage" \
  --expr "rate(cpu_usage_total[5m]) * 100" \
  --datasource prometheus-uid \
  --legend "{{instance}}"

# Add stat panel
python cli.py panel add-stat dashboard-uid "Total Requests" \
  --expr "sum(rate(http_requests_total[5m]))" \
  --datasource prometheus-uid

# Add gauge panel
python cli.py panel add-gauge dashboard-uid "Memory %" \
  --expr "memory_usage_percent" \
  --datasource prometheus-uid \
  --min 0 --max 100

# List panels
python cli.py panel list dashboard-uid

# Remove panel
python cli.py panel remove dashboard-uid --panel_id 1
```

## Variable Commands

```bash
# Add query variable
python cli.py var add-query dashboard-uid job \
  --query "label_values(job)" \
  --datasource prometheus-uid

# Add multi-value query variable
python cli.py var add-query dashboard-uid instance \
  --query "label_values(instance)" \
  --datasource prometheus-uid \
  --multi

# Add custom variable
python cli.py var add-custom dashboard-uid env \
  --values "dev,staging,prod"

# Add interval variable
python cli.py var add-interval dashboard-uid

# Add constant variable
python cli.py var add-constant dashboard-uid region --value "us-west"

# List variables
python cli.py var list dashboard-uid

# Remove variable
python cli.py var remove dashboard-uid job
```

## Common Workflows

### Update All Dashboards in Overview Folder

```bash
# 1. View the folder structure
python cli.py folder tree

# 2. List all dashboards
python cli.py folder list-dashboards Overview --recursive

# 3. Add "production" tag to all
python cli.py folder apply Overview add-tag "production"

# 4. Replace datasource across all
python cli.py folder apply Overview replace-datasource "Test-Prometheus,Prod-Prometheus"
```

### Setup Monitoring Dashboards

```bash
# Create folder structure
python cli.py folder create "Monitoring/Backend"
python cli.py folder create "Monitoring/Frontend"

# Add common variable to all monitoring dashboards
python cli.py folder apply Monitoring add-variable "env,label_values(environment),prometheus-uid"

# Add production tag
python cli.py folder apply Monitoring add-tag "production"
```

### Migrate Datasource

```bash
# Replace datasource in all dashboards
python cli.py folder apply Overview replace-datasource "OldPrometheus,NewPrometheus"

# Verify the change
python cli.py ds list dashboard-uid
```
