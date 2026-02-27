"""
Grafana Dashboard Manager - Object-Oriented API Examples

This file demonstrates how to use the new object-oriented API
where Folder and Dashboard are objects with component managers.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Import the new OO API
from src import GrafanaClient, Folder, Dashboard

# Also import components if needed directly
from src.components import DatasourceComponent, PanelComponent, VariableComponent


def example_working_with_folders():
    """Example: Working with folders"""
    client = GrafanaClient()

    # List all folders
    folders = Folder.list_all(client)
    print("=== Folders ===")
    for folder in folders:
        print(f"  - {folder.title} (UID: {folder.uid})")

    # Get a specific folder
    folder = Folder.get(client, "my-folder-uid")
    if folder:
        print(f"\nFound folder: {folder.title}")

        # List dashboards in folder
        dashboards = folder.dashboards()
        print(f"Dashboards in {folder.title}:")
        for dash in dashboards:
            print(f"  - {dash.title}")

        # Create new dashboard in folder
        new_dashboard = folder.create_dashboard("New Dashboard", tags=["production"])
        print(f"\nCreated dashboard: {new_dashboard.uid}")

    # Create a new folder
    new_folder = Folder.create(client, "My New Folder", uid="my-new-folder")
    print(f"\nCreated folder: {new_folder.uid}")


def example_working_with_dashboards():
    """Example: Working with dashboards"""
    client = GrafanaClient()

    # Get existing dashboard
    dashboard = Dashboard.get(client, "my-dashboard-uid")
    if not dashboard:
        print("Dashboard not found")
        return

    print(f"=== Dashboard: {dashboard.title} ===")
    print(f"UID: {dashboard.uid}")
    print(f"Folder: {dashboard.folder.title if dashboard.folder else 'None'}")
    print(f"Tags: {dashboard.tags}")

    # Modify dashboard properties
    dashboard.add_tag("updated")
    dashboard.description = "Updated via API"
    dashboard.editable = True

    # Save changes
    dashboard.save("Updated tags and description")


def example_datasource_operations():
    """Example: Data source operations on a dashboard"""
    client = GrafanaClient()

    dashboard = Dashboard.get(client, "my-dashboard-uid")
    if not dashboard:
        return

    # ADD a data source to all panels and variables
    dashboard.datasources.add("Prometheus-Prod")
    print("✓ Added Prometheus-Prod to panels and variables")

    # REPLACE data source in dashboard
    dashboard.datasources.replace("Prometheus-Old", "Prometheus-New")
    print("✓ Replaced Prometheus-Old with Prometheus-New")

    # REMOVE a data source from dashboard
    dashboard.datasources.remove("Prometheus-Test")
    print("✓ Removed Prometheus-Test")

    # LIST used data sources
    used = dashboard.datasources.list_used()
    print(f"Used data sources: {[ds['uid'] for ds in used]}")

    # Save all changes
    dashboard.save("Updated data sources")


def example_panel_operations():
    """Example: Panel operations on a dashboard"""
    client = GrafanaClient()

    # Get datasource UID first
    datasource = client.get_datasource_by_name("Prometheus")
    if not datasource:
        print("Datasource not found")
        return
    datasource_uid = datasource["uid"]

    dashboard = Dashboard.get(client, "my-dashboard-uid")
    if not dashboard:
        return

    # ADD panels
    dashboard.panels.add_timeseries(
        title="CPU Usage",
        expr='avg by (instance) (rate(cpu_usage_total[5m])) * 100',
        datasource_uid=datasource_uid,
        legend_format="{{instance}}"
    )
    print("✓ Added CPU Usage time series panel")

    dashboard.panels.add_stat(
        title="Total Requests",
        expr="sum(rate(http_requests_total[5m]))",
        datasource_uid=datasource_uid
    )
    print("✓ Added Total Requests stat panel")

    dashboard.panels.add_gauge(
        title="Memory Usage",
        expr="memory_usage_percent",
        datasource_uid=datasource_uid,
        min=0,
        max=100
    )
    print("✓ Added Memory Usage gauge panel")

    # EDIT a panel
    dashboard.panels.edit(panel_id=1, title="Updated Title")
    print("✓ Edited panel 1 title")

    # EDIT a query in a panel
    dashboard.panels.edit_query(panel_id=1, target_index=0, expr="new_metric")
    print("✓ Edited query in panel 1")

    # ADD query to existing panel
    dashboard.panels.add_query(
        panel_id=1,
        expr="another_metric",
        datasource_uid=datasource_uid,
        legend_format="Second metric"
    )
    print("✓ Added query to panel 1")

    # DUPLICATE a panel
    dashboard.panels.duplicate(panel_id=1, offset_y=8)
    print("✓ Duplicated panel 1")

    # LIST all panels
    panels = dashboard.panels.list_all()
    print(f"\nTotal panels: {len(panels)}")
    for panel in panels:
        print(f"  - {panel.get('title', 'Untitled')} (ID: {panel.get('id')})")

    # REMOVE a panel
    dashboard.panels.remove(panel_id=2)
    print("\n✓ Removed panel 2")

    # Save changes
    dashboard.save("Added and modified panels")


def example_variable_operations():
    """Example: Variable operations on a dashboard"""
    client = GrafanaClient()

    # Get datasource UID
    datasource = client.get_datasource_by_name("Prometheus")
    if not datasource:
        print("Datasource not found")
        return
    datasource_uid = datasource["uid"]

    dashboard = Dashboard.get(client, "my-dashboard-uid")
    if not dashboard:
        return

    # ADD variables
    dashboard.variables.add_query(
        name="job",
        query="label_values(job)",
        datasource_uid=datasource_uid,
        label="Job"
    )
    print("✓ Added query variable $job")

    dashboard.variables.add_query(
        name="instance",
        query='label_values(instance, job="$job")',
        datasource_uid=datasource_uid,
        multi=True
    )
    print("✓ Added query variable $instance (multi)")

    dashboard.variables.add_custom(
        name="environment",
        values=["dev", "staging", "prod"],
        multi=False
    )
    print("✓ Added custom variable $environment")

    dashboard.variables.add_interval()
    print("✓ Added interval variable $interval")

    dashboard.variables.add_constant(
        name="region",
        value="us-west"
    )
    print("✓ Added constant variable $region")

    # EDIT variables
    dashboard.variables.edit("environment", multi=True)
    print("✓ Edited $environment to allow multiple values")

    dashboard.variables.edit_query("job", "label_values(job, scrape_interval='15s')")
    print("✓ Edited query for $job")

    dashboard.variables.edit_datasource("job", new_datasource_uid="new-ds-uid")
    print("✓ Edited datasource for $job")

    # LIST all variables
    variables = dashboard.variables.list_all()
    print(f"\nTotal variables: {len(variables)}")
    for var in variables:
        print(f"  - ${var.get('name')} ({var.get('type')})")

    # DUPLICATE a variable
    dashboard.variables.duplicate("job", "job_backup")
    print("\n✓ Duplicated $job as $job_backup")

    # REMOVE a variable
    dashboard.variables.remove("job_backup")
    print("✓ Removed variable $job_backup")

    # Save changes
    dashboard.save("Added and modified variables")


def example_complete_workflow():
    """Example: Complete workflow - create dashboard from scratch"""
    client = GrafanaClient()

    # Get or create folder
    folder = Folder.get(client, "monitoring")
    if not folder:
        folder = Folder.create(client, "Monitoring", uid="monitoring")
    print(f"✓ Using folder: {folder.title}")

    # Get datasource
    datasource = client.get_datasource_by_name("Prometheus")
    datasource_uid = datasource["uid"]

    # Create new dashboard
    dashboard = Dashboard.create(
        client,
        "Server Metrics Dashboard",
        folder=folder,
        tags=["servers", "production"]
    )
    print(f"✓ Created dashboard: {dashboard.title}")

    # Add variables
    dashboard.variables.add_interval()
    dashboard.variables.add_query(
        name="server",
        query="label_values(instance)",
        datasource_uid=datasource_uid,
        multi=True
    )
    print("✓ Added variables")

    # Add panels
    metrics = [
        ("CPU Usage", "rate(cpu_usage_total[5m]) * 100"),
        ("Memory Usage", "memory_usage_percent"),
        ("Disk I/O", "rate(disk_io_bytes[5m])"),
        ("Network Traffic", "rate(network_bytes[5m])")
    ]

    for i, (title, expr) in enumerate(metrics):
        dashboard.panels.add_timeseries(
            title=title,
            expr=expr,
            datasource_uid=datasource_uid,
            grid_pos={
                "h": 8,
                "w": 12,
                "x": (i % 2) * 12,
                "y": (i // 2) * 8
            }
        )
    print(f"✓ Added {len(metrics)} panels")

    # Save everything
    dashboard.save("Created initial dashboard")
    print("✓ Dashboard saved!")


def example_batch_operations():
    """Example: Batch operations on multiple dashboards"""
    client = GrafanaClient()

    folder = Folder.get(client, "production")
    if not folder:
        print("Folder not found")
        return

    # Apply operation to all dashboards in folder
    def add_tag(dash: Dashboard):
        dash.add_tag("production")
        return "added tag"

    results = folder.apply_to_all_dashboards(add_tag)

    print("=== Batch Results ===")
    for result in results:
        status = result["status"]
        uid = result["dashboard"]
        if status == "success":
            print(f"✓ {uid}: {result['result']}")
        else:
            print(f"❌ {uid}: {result.get('error')}")


def example_duplicate_dashboard():
    """Example: Duplicate dashboard to new folder"""
    client = GrafanaClient()

    source_dashboard = Dashboard.get(client, "source-dashboard-uid")
    if not source_dashboard:
        print("Source dashboard not found")
        return

    # Get target folder
    target_folder = Folder.get(client, "staging")
    if not target_folder:
        target_folder = Folder.create(client, "Staging", uid="staging")

    # Duplicate dashboard
    new_dashboard = source_dashboard.duplicate(
        new_title="Staging Dashboard",
        folder=target_folder
    )

    print(f"✓ Duplicated dashboard to: {new_dashboard.uid}")


def example_export_import():
    """Example: Export and import dashboard"""
    client = GrafanaClient()

    # Export
    dashboard = Dashboard.get(client, "my-dashboard-uid")
    dashboard.export("backups/my-dashboard.json")
    print("✓ Exported dashboard")

    # Import (this would create/update a dashboard)
    # Note: Import is done via client directly
    import json
    with open("backups/my-dashboard.json", 'r') as f:
        dashboard_data = json.load(f)

    result = client.update_dashboard(
        dashboard=dashboard_data,
        message="Imported from backup",
        overwrite=False
    )
    print(f"✓ Imported dashboard as: {result['uid']}")


if __name__ == "__main__":
    import sys

    print("Grafana Dashboard Manager - OO API Examples\n")

    examples = {
        "folders": example_working_with_folders,
        "dashboards": example_working_with_dashboards,
        "datasources": example_datasource_operations,
        "panels": example_panel_operations,
        "variables": example_variable_operations,
        "complete": example_complete_workflow,
        "batch": example_batch_operations,
        "duplicate": example_duplicate_dashboard,
        "export": example_export_import,
    }

    if len(sys.argv) > 1:
        example_name = sys.argv[1]
        if example_name in examples:
            examples[example_name]()
        else:
            print(f"Unknown example: {example_name}")
            print(f"Available: {', '.join(examples.keys())}")
    else:
        print("Usage: python oo_examples.py <example_name>")
        print(f"Available examples: {', '.join(examples.keys())}")
