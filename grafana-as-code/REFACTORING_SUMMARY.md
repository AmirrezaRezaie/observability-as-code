# Grafana Dashboard Manager - Refactoring Summary

## Overview

The project has been refactored to use an **Object-Oriented API** where:
- **Folder** and **Dashboard** are main objects
- Each has **component managers** (datasources, panels, variables)
- Each component has **add/remove/edit** methods

## Architecture

### Core Objects

```
GrafanaClient (API Client)
    ↓
Folder (represents a Grafana folder)
    ├── dashboards() → List[Dashboard]
    ├── create_dashboard()
    └── apply_to_all_dashboards()
    ↓
Dashboard (represents a dashboard)
    ├── datasources (DatasourceComponent)
    ├── panels (PanelComponent)
    └── variables (VariableComponent)
```

### Component Pattern

Each component follows a consistent pattern:
- **Add** methods: `add_*()` - Add new items
- **Remove** methods: `remove()`, `clear()` - Remove items
- **Edit** methods: `edit()`, `edit_*()` - Modify items
- **List** methods: `list_all()`, `get()` - Query items

## File Structure

```
src/
├── client.py              # GrafanaClient - Base API client
├── folder.py              # Folder - Folder object
├── dashboard_v2.py        # Dashboard - Dashboard object (new)
├── dashboard.py           # DashboardManager - Legacy API
├── datasource.py          # DatasourceManager - Legacy API
├── panel.py               # PanelManager - Legacy API
├── variable.py            # VariableManager - Legacy API
└── components/
    ├── __init__.py        # Component exports
    ├── datasource.py      # DatasourceComponent
    ├── panel.py           # PanelComponent
    └── variable.py        # VariableComponent
```

## Usage Examples

### Folder Operations

```python
from src import GrafanaClient, Folder

client = GrafanaClient()

# List folders
folders = Folder.list_all(client)

# Create folder
folder = Folder.create(client, "My Folder", uid="my-folder")

# Get folder
folder = Folder.get(client, "folder-uid")

# List dashboards in folder
dashboards = folder.dashboards()

# Create dashboard in folder
dashboard = folder.create_dashboard("My Dashboard")

# Apply operation to all dashboards
results = folder.apply_to_all_dashboards(lambda d: (d.add_tag("batch"), "done"))
```

### Dashboard Operations

```python
from src import GrafanaClient, Dashboard

client = GrafanaClient()

# Get dashboard
dashboard = Dashboard.get(client, "dashboard-uid")

# Create dashboard
dashboard = Dashboard.create(client, "My Dashboard")

# Modify properties
dashboard.add_tag("production")
dashboard.description = "Production metrics"

# Save changes
dashboard.save("Updated dashboard")

# Duplicate
new_dashboard = dashboard.duplicate("Staging Dashboard")

# Export
dashboard.export("backups/dashboard.json")
```

### Data Source Component

```python
dashboard = Dashboard.get(client, "dashboard-uid")

# ADD
dashboard.datasources.add("Prometheus-Prod")

# REPLACE
dashboard.datasources.replace("Prometheus-Old", "Prometheus-New")

# REMOVE
dashboard.datasources.remove("Prometheus-Test")

# LIST
used = dashboard.datasources.list_used()

# Save
dashboard.save()
```

### Panel Component

```python
dashboard = Dashboard.get(client, "dashboard-uid")
datasource_uid = client.get_datasource_by_name("Prometheus")["uid"]

# ADD panels
dashboard.panels.add_timeseries(
    title="CPU Usage",
    expr="rate(cpu_usage_total[5m]) * 100",
    datasource_uid=datasource_uid
)

dashboard.panels.add_stat(
    title="Total Requests",
    expr="sum(rate(http_requests_total[5m]))",
    datasource_uid=datasource_uid
)

dashboard.panels.add_gauge(
    title="Memory",
    expr="memory_usage",
    datasource_uid=datasource_uid,
    min=0, max=100
)

# EDIT panel
dashboard.panels.edit(panel_id=1, title="New Title")
dashboard.panels.edit_query(panel_id=1, target_index=0, expr="new_metric")

# ADD query to panel
dashboard.panels.add_query(panel_id=1, expr="another_metric", datasource_uid=datasource_uid)

# DUPLICATE panel
dashboard.panels.duplicate(panel_id=1)

# LIST panels
panels = dashboard.panels.list_all()

# REMOVE panel
dashboard.panels.remove(panel_id=2)

# Save
dashboard.save()
```

### Variable Component

```python
dashboard = Dashboard.get(client, "dashboard-uid")
datasource_uid = client.get_datasource_by_name("Prometheus")["uid"]

# ADD variables
dashboard.variables.add_query(
    name="job",
    query="label_values(job)",
    datasource_uid=datasource_uid
)

dashboard.variables.add_custom(
    name="environment",
    values=["dev", "staging", "prod"]
)

dashboard.variables.add_interval()
dashboard.variables.add_constant(name="region", value="us-west")

# EDIT variables
dashboard.variables.edit("env", multi=True)
dashboard.variables.edit_query("job", "new_query")
dashboard.variables.edit_datasource("job", new_datasource_uid="...")

# LIST variables
variables = dashboard.variables.list_all()

# DUPLICATE variable
dashboard.variables.duplicate("job", "job_backup")

# REMOVE variable
dashboard.variables.remove("job_backup")

# Save
dashboard.save()
```

## Key Benefits

1. **Intuitive API**: Objects and methods match mental model
2. **Fluent Interface**: Chain operations naturally
3. **Type Safety**: TYPE_CHECKING used for circular imports
4. **Lazy Loading**: Components loaded only when accessed
5. **Backward Compatible**: Legacy API still available
6. **Consistent Patterns**: All components follow add/remove/edit pattern

## Migration from Legacy API

### Old API
```python
from src import GrafanaClient, DashboardManager, PanelManager

client = GrafanaClient()
dash_manager = DashboardManager(client)
panel_manager = PanelManager(client)

# Get dashboard JSON
dashboard_data = dash_manager.get_dashboard("uid")

# Create panel
panel = panel_manager.create_timeseries_panel(...)
result = panel_manager.add_panel_to_dashboard("uid", panel)
```

### New API
```python
from src import GrafanaClient, Dashboard

client = GrafanaClient()
dashboard = Dashboard.get(client, "uid")

# Create panel
dashboard.panels.add_timeseries(...)

# Save
dashboard.save()
```

## Documentation

- **README.md**: Quick start guide
- **docs/OO_API_REFERENCE.md**: Complete API reference
- **examples/oo_examples.py**: Usage examples
