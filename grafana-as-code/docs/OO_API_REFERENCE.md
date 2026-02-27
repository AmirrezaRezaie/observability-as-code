# Object-Oriented API Reference

## Overview

The Grafana Dashboard Manager now uses an object-oriented approach where:
- **Folder** represents a Grafana folder containing dashboards
- **Dashboard** represents a dashboard with component managers
- Each component has **add/remove/edit** methods

## Core Objects

### GrafanaClient

Base API client for authentication and HTTP requests.

```python
from src import GrafanaClient

client = GrafanaClient(
    url="http://localhost:3000",
    api_key="your-api-key"
)
```

### Folder

Represents a Grafana folder.

**Methods:**
- `Folder.list_all(client)` - List all folders
- `Folder.get(client, uid)` - Get folder by UID
- `Folder.create(client, title, uid=None)` - Create new folder
- `folder.delete()` - Delete this folder
- `folder.refresh()` - Refresh folder data from server
- `folder.dashboards()` - List all dashboards in folder
- `folder.get_dashboard(uid)` - Get specific dashboard
- `folder.create_dashboard(title, tags=None)` - Create dashboard in folder
- `folder.find_dashboards_by_title(title)` - Find dashboards by title
- `folder.apply_to_all_dashboards(func)` - Apply function to all dashboards

**Properties:**
- `folder.uid` - Folder UID
- `folder.title` - Folder title

### Dashboard

Represents a Grafana dashboard with component managers.

**Methods:**
- `Dashboard.get(client, uid)` - Get dashboard by UID
- `Dashboard.create(client, title, folder=None, tags=None)` - Create new dashboard
- `dashboard.refresh()` - Refresh dashboard data from server
- `dashboard.save(message=None)` - Save changes to server
- `dashboard.delete()` - Delete this dashboard
- `dashboard.export(path)` - Export dashboard to JSON file
- `dashboard.duplicate(new_title, folder=None)` - Duplicate dashboard

**Properties:**
- `dashboard.uid` - Dashboard UID
- `dashboard.title` - Dashboard title
- `dashboard.folder` - Parent Folder object (or None)
- `dashboard.datasources` - DatasourceComponent manager
- `dashboard.panels` - PanelComponent manager
- `dashboard.variables` - VariableComponent manager
- `dashboard.tags` - List of tags
- `dashboard.description` - Dashboard description (get/set)
- `dashboard.editable` - Editable flag (get/set)

**Tag Methods:**
- `dashboard.add_tag(tag)` - Add a tag
- `dashboard.remove_tag(tag)` - Remove a tag

## Component Managers

### DatasourceComponent

Manages data source references in a dashboard.

**Methods:**

#### Add
```python
dashboard.datasources.add(
    datasource_name,
    apply_to_panels=True,
    apply_to_variables=True
)
```

#### Remove
```python
dashboard.datasources.remove(datasource_name)
```

#### Replace
```python
dashboard.datasources.replace(old_datasource_name, new_datasource_name)
```

#### Edit
```python
dashboard.datasources.edit(datasource_name, **updates)
```

#### List
```python
used = dashboard.datasources.list_used()
```

### PanelComponent

Manages panels (graphs, stats, gauges) in a dashboard.

**Methods:**

#### Add Panels
```python
# Time series
dashboard.panels.add_timeseries(
    title="CPU Usage",
    expr="rate(cpu_usage_total[5m]) * 100",
    datasource_uid="...",
    legend_format="{{instance}}",
    grid_pos={"h": 8, "w": 12, "x": 0, "y": 0}
)

# Stat
dashboard.panels.add_stat(
    title="Total Requests",
    expr="sum(rate(http_requests_total[5m]))",
    datasource_uid="...",
    grid_pos=None  # Auto-calculate
)

# Gauge
dashboard.panels.add_gauge(
    title="Memory",
    expr="memory_usage",
    datasource_uid="...",
    min=0,
    max=100
)

# Custom panel
dashboard.panels.add_custom(panel_config)
```

#### Edit Panels
```python
# Edit panel properties
dashboard.panels.edit(panel_id=1, title="New Title")

# Edit query in panel
dashboard.panels.edit_query(panel_id=1, target_index=0, expr="new_metric")

# Add query to existing panel
dashboard.panels.add_query(
    panel_id=1,
    expr="another_metric",
    datasource_uid="...",
    legend_format="Second"
)
```

#### Duplicate Panel
```python
dashboard.panels.duplicate(panel_id=1, offset_y=8)
```

#### Remove Panels
```python
# Remove specific panel
dashboard.panels.remove(panel_id=2)

# Remove all panels
dashboard.panels.clear()
```

#### List Panels
```python
# List all panels
panels = dashboard.panels.list_all()

# Get specific panel
panel = dashboard.panels.get(panel_id=1)
```

#### Reorder
```python
dashboard.panels.reorder([3, 1, 2])  # New order
```

### VariableComponent

Manages template variables in a dashboard.

**Methods:**

#### Add Variables
```python
# Query variable
dashboard.variables.add_query(
    name="job",
    query="label_values(job)",
    datasource_uid="...",
    label="Job",
    multi=False,
    include_all=False,
    all_value=None,
    regex=None
)

# Custom variable
dashboard.variables.add_custom(
    name="environment",
    values=["dev", "staging", "prod"],
    label="Environment",
    multi=False
)

# Interval variable
dashboard.variables.add_interval(
    name="interval",
    values=["1m", "5m", "10m", "1h"]
)

# Constant variable
dashboard.variables.add_constant(
    name="region",
    value="us-west",
    label="Region"
)

# Custom variable config
dashboard.variables.add_custom(variable_config)
```

#### Edit Variables
```python
# Edit variable properties
dashboard.variables.edit("env", multi=True)

# Edit query
dashboard.variables.edit_query("job", "new_query_string")

# Edit datasource
dashboard.variables.edit_datasource("job", new_datasource_uid="...")
```

#### Duplicate Variable
```python
dashboard.variables.duplicate("job", "job_backup")
```

#### Remove Variables
```python
# Remove specific variable
dashboard.variables.remove("job")

# Remove all variables
dashboard.variables.clear()
```

#### List Variables
```python
# List all variables
variables = dashboard.variables.list_all()

# Get specific variable
variable = dashboard.variables.get("job")

# List only query variables
query_vars = dashboard.variables.get_query_variables()

# List only custom variables
custom_vars = dashboard.variables.get_custom_variables()
```

#### Reorder
```python
dashboard.variables.reorder(["interval", "job", "instance"])
```

## Workflow Examples

### Typical Dashboard Creation

```python
from src import GrafanaClient, Folder, Dashboard

client = GrafanaClient()

# 1. Get or create folder
folder = Folder.get(client, "monitoring")
if not folder:
    folder = Folder.create(client, "Monitoring", uid="monitoring")

# 2. Create dashboard
dashboard = Dashboard.create(
    client,
    "Server Metrics",
    folder=folder,
    tags=["production"]
)

# 3. Get datasource
datasource = client.get_datasource_by_name("Prometheus")
datasource_uid = datasource["uid"]

# 4. Add variables
dashboard.variables.add_interval()
dashboard.variables.add_query(
    name="server",
    query="label_values(instance)",
    datasource_uid=datasource_uid,
    multi=True
)

# 5. Add panels
dashboard.panels.add_timeseries(
    title="CPU Usage",
    expr="rate(cpu_usage_total[5m]) * 100",
    datasource_uid=datasource_uid
)

# 6. Save
dashboard.save("Created initial dashboard")
```

### Updating Existing Dashboard

```python
from src import GrafanaClient, Dashboard

client = GrafanaClient()
dashboard = Dashboard.get(client, "dashboard-uid")

# Make changes
dashboard.datasources.add("Prometheus-Prod")
dashboard.panels.add_stat(title="Errors", expr="rate(errors[5m])", datasource_uid="...")
dashboard.variables.add_custom(name="region", values=["us", "eu"])

# Save all changes at once
dashboard.save("Added new panels and variables")
```

### Batch Update Multiple Dashboards

```python
from src import GrafanaClient, Folder

client = GrafanaClient()
folder = Folder.get(client, "production")

def update_dashboard(dashboard):
    dashboard.datasources.replace("Old-DS", "New-DS")
    dashboard.add_tag("migrated")
    return "updated"

results = folder.apply_to_all_dashboards(update_dashboard)

for result in results:
    print(f"{result['dashboard']}: {result['status']}")
```
