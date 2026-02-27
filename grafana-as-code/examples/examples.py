"""
Grafana Dashboard Manager - Usage Examples

This file demonstrates how to use the Grafana Dashboard Manager toolkit.
"""

import os
from src import GrafanaClient, DashboardManager, DatasourceManager, PanelManager, VariableManager
from dotenv import load_dotenv

load_dotenv()


def example_list_dashboards():
    """List all dashboards"""
    client = GrafanaClient()
    dashboards = client.list_dashboards()

    print("=== All Dashboards ===")
    for dash in dashboards:
        print(f"  - {dash['title']} (UID: {dash['uid']})")


def example_get_dashboard():
    """Get and display dashboard details"""
    client = GrafanaClient()
    dashboard_mgr = DashboardManager(client)

    uid = "your-dashboard-uid"  # Replace with actual UID
    dashboard = dashboard_mgr.get_dashboard(uid)

    print(f"=== Dashboard: {dashboard.get('title')} ===")
    print(f"UID: {dashboard.get('uid')}")
    print(f"Panels: {len(dashboard.get('panels', []))}")
    print(f"Variables: {len(dashboard.get('templating', {}).get('list', []))}")


def example_add_datasource_to_dashboard():
    """Add a data source to all panels in a dashboard"""
    client = GrafanaClient()
    dashboard_mgr = DashboardManager(client)

    dashboard_uid = "your-dashboard-uid"
    datasource_name = "Prometheus-Prod"

    # Add to panels
    result = dashboard_mgr.add_datasource_to_panels(
        dashboard_uid,
        datasource_name
    )
    print(f"✓ Added data source to panels")

    # Add to variables
    result = dashboard_mgr.add_datasource_to_variables(
        dashboard_uid,
        datasource_name
    )
    print(f"✓ Added data source to variables")


def example_replace_datasource():
    """Replace data source across multiple dashboards"""
    client = GrafanaClient()
    ds_mgr = DatasourceManager(client)

    results = ds_mgr.replace_datasource_in_dashboards(
        old_datasource_name="Prometheus-Old",
        new_datasource_name="Prometheus-New",
        dashboard_uids=["dash-uid-1", "dash-uid-2", "dash-uid-3"]
    )

    for result in results:
        print(f"Dashboard {result['uid']}: {result['status']}")


def example_add_timeseries_panel():
    """Add a time series panel with metric"""
    client = GrafanaClient()
    panel_mgr = PanelManager(client)
    ds_mgr = DatasourceManager(client)

    dashboard_uid = "your-dashboard-uid"

    # Get datasource
    datasource = ds_mgr.get_datasource_by_name("Prometheus")

    # Create panel
    panel = panel_mgr.create_timeseries_panel(
        title="CPU Usage",
        expr='avg by (instance) (rate(cpu_usage_total[5m])) * 100',
        datasource_uid=datasource["uid"],
        legend_format="{{instance}}"
    )

    # Add to dashboard
    result = panel_mgr.add_panel_to_dashboard(dashboard_uid, panel)
    print(f"✓ Added time series panel")


def example_add_multiple_panels():
    """Add multiple panels from a list of metrics"""
    client = GrafanaClient()
    panel_mgr = PanelManager(client)
    ds_mgr = DatasourceManager(client)

    dashboard_uid = "your-dashboard-uid"
    datasource = ds_mgr.get_datasource_by_name("Prometheus")

    metrics = [
        {"title": "CPU Usage", "expr": "cpu_usage_percent"},
        {"title": "Memory Usage", "expr": "memory_usage_percent"},
        {"title": "Disk I/O", "expr": "rate(disk_io[5m])"},
        {"title": "Network Traffic", "expr": "rate(network_bytes[5m])"}
    ]

    for i, metric in enumerate(metrics):
        panel = panel_mgr.create_timeseries_panel(
            title=metric["title"],
            expr=metric["expr"],
            datasource_uid=datasource["uid"],
            grid_pos={
                "h": 8,
                "w": 12,
                "x": (i % 2) * 12,
                "y": (i // 2) * 8
            }
        )
        panel_mgr.add_panel_to_dashboard(dashboard_uid, panel)

    print(f"✓ Added {len(metrics)} panels")


def example_add_variable():
    """Add a query variable to dashboard"""
    client = GrafanaClient()
    var_mgr = VariableManager(client)
    ds_mgr = DatasourceManager(client)

    dashboard_uid = "your-dashboard-uid"
    datasource = ds_mgr.get_datasource_by_name("Prometheus")

    # Add query variable
    variable = var_mgr.create_query_variable(
        name="job",
        query="label_values(job)",
        datasource_uid=datasource["uid"],
        label="Job"
    )

    result = var_mgr.add_variable_to_dashboard(dashboard_uid, variable)
    print(f"✓ Added variable $job")

    # Add instance variable
    variable = var_mgr.create_query_variable(
        name="instance",
        query='label_values(instance, job="$job")',
        datasource_uid=datasource["uid"],
        multi=True
    )

    result = var_mgr.add_variable_to_dashboard(dashboard_uid, variable)
    print(f"✓ Added variable $instance")


def example_add_custom_variable():
    """Add a custom variable with predefined values"""
    client = GrafanaClient()
    var_mgr = VariableManager(client)

    dashboard_uid = "your-dashboard-uid"

    variable = var_mgr.create_custom_variable(
        name="environment",
        values=["dev", "staging", "prod"],
        multi=False
    )

    result = var_mgr.add_variable_to_dashboard(dashboard_uid, variable)
    print(f"✓ Added custom variable $environment")


def example_clone_dashboard():
    """Clone a dashboard with modifications"""
    client = GrafanaClient()
    dashboard_mgr = DashboardManager(client)

    source_uid = "source-dashboard-uid"
    result = dashboard_mgr.clone_dashboard(
        uid=source_uid,
        new_title="Production Dashboard",
        folder_uid="folder-uid"  # Optional
    )

    print(f"✓ Cloned dashboard to new UID: {result.get('uid')}")


def example_batch_update():
    """Apply update to multiple dashboards"""
    client = GrafanaClient()
    dashboard_mgr = DashboardManager(client)

    def add_tag(dashboard):
        """Add a tag to dashboard"""
        tags = dashboard.get("tags", [])
        if "production" not in tags:
            tags.append("production")
        dashboard["tags"] = tags
        return dashboard

    dashboard_uids = ["dash-1", "dash-2", "dash-3"]

    results = dashboard_mgr.batch_update_dashboards(
        dashboard_uids,
        add_tag,
        message="Added production tag"
    )

    for result in results:
        print(f"Dashboard {result['uid']}: {result['status']}")


def example_export_import_dashboard():
    """Export and import dashboard"""
    client = GrafanaClient()
    dashboard_mgr = DashboardManager(client)

    # Export
    uid = "dashboard-to-export"
    dashboard_mgr.export_dashboard(uid, "backups/dashboard.json")
    print(f"✓ Exported dashboard to file")

    # Import
    result = dashboard_mgr.import_dashboard(
        "backups/dashboard.json",
        folder_uid="new-folder",
        overwrite=False
    )
    print(f"✓ Imported dashboard to UID: {result.get('uid')}")


def example_find_datasource_usage():
    """Find all dashboards using a specific data source"""
    client = GrafanaClient()
    ds_mgr = DatasourceManager(client)

    usage = ds_mgr.find_datasource_usage("Prometheus-Prod")

    print(f"=== Dashboards using Prometheus-Prod ===")
    for item in usage:
        dash = item["dashboard"]
        print(f"  - {dash['title']} ({item['type']})")


def example_complete_workflow():
    """Complete workflow: Create dashboard with panels and variables"""
    client = GrafanaClient()
    dashboard_mgr = DashboardManager(client)
    panel_mgr = PanelManager(client)
    var_mgr = VariableManager(client)
    ds_mgr = DatasourceManager(client)

    datasource = ds_mgr.get_datasource_by_name("Prometheus")
    datasource_uid = datasource["uid"]

    # Create new dashboard
    dashboard = {
        "title": "Server Metrics",
        "tags": ["servers", "production"],
        "timezone": "browser",
        "panels": [],
        "templating": {"list": []}
    }

    result = client.update_dashboard(
        dashboard=dashboard,
        message="Created new dashboard"
    )

    dashboard_uid = result.get("uid")
    print(f"✓ Created dashboard: {dashboard_uid}")

    # Add variables
    var = var_mgr.create_query_variable(
        name="server",
        query="label_values(instance)",
        datasource_uid=datasource_uid,
        multi=True
    )
    var_mgr.add_variable_to_dashboard(dashboard_uid, var)

    var = var_mgr.create_interval_variable()
    var_mgr.add_variable_to_dashboard(dashboard_uid, var)

    # Add panels
    panel = panel_mgr.create_timeseries_panel(
        title="CPU Usage",
        expr='avg by (instance) (rate(cpu_usage_total[5m])) * 100',
        datasource_uid=datasource_uid,
        grid_pos={"h": 8, "w": 12, "x": 0, "y": 0}
    )
    panel_mgr.add_panel_to_dashboard(dashboard_uid, panel)

    panel = panel_mgr.create_stat_panel(
        title="Total Memory",
        expr="sum(memory_total_bytes)",
        datasource_uid=datasource_uid,
        grid_pos={"h": 4, "w": 6, "x": 12, "y": 0}
    )
    panel_mgr.add_panel_to_dashboard(dashboard_uid, panel)

    print(f"✓ Dashboard created successfully!")


if __name__ == "__main__":
    # Run examples
    print("Grafana Dashboard Manager - Examples\n")

    # Uncomment the example you want to run:

    # example_list_dashboards()
    # example_get_dashboard()
    # example_add_datasource_to_dashboard()
    # example_replace_datasource()
    # example_add_timeseries_panel()
    # example_add_multiple_panels()
    # example_add_variable()
    # example_add_custom_variable()
    # example_clone_dashboard()
    # example_batch_update()
    # example_export_import_dashboard()
    # example_find_datasource_usage()
    # example_complete_workflow()
