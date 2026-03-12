#!/usr/bin/env python3
"""
Grafana Dashboard Manager CLI
Command-line interface for managing Grafana dashboards, folders, and components
"""

import argparse
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from . import GrafanaClient, Folder, Dashboard


def cmd_list_folders(args):
    """List all folders"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    folders = Folder.list_all(client)

    if args.json:
        import json
        print(json.dumps([{"uid": f.uid, "title": f.title} for f in folders], indent=2))
    else:
        print(f"{'UID':<20} {'Title'}")
        print("-" * 50)
        for folder in folders:
            print(f"{folder.uid:<20} {folder.title}")


def cmd_create_folder(args):
    """Create a new folder"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    folder = Folder.create(client, args.title, uid=args.uid)
    print(f"✓ Created folder: {folder.title} (UID: {folder.uid})")


def cmd_folder_tree(args):
    """Print folder tree structure"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)

    if args.uid:
        # Print tree starting from specific folder
        folder = Folder.find(client, args.uid)
        if not folder:
            print(f"❌ Folder '{args.uid}' not found")
            return
        folder.print_tree()
    else:
        # Print full folder tree
        root = Folder.build_tree(client)
        root.print_tree()


def cmd_folder_apply(args):
    """Apply operation to all dashboards in folder tree"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    folder = Folder.find(client, args.uid)

    if not folder:
        print(f"❌ Folder '{args.uid}' not found")
        return

    # Define operations
    def apply_operation(dashboard):
        if args.operation == "add-tag":
            dashboard.add_tag(args.value)
            dashboard.save(f"Added tag: {args.value}")
            return f"Added tag '{args.value}'"

        elif args.operation == "remove-tag":
            dashboard.remove_tag(args.value)
            dashboard.save(f"Removed tag: {args.value}")
            return f"Removed tag '{args.value}'"

        elif args.operation == "add-datasource":
            dashboard.datasources.add(args.value)
            dashboard.save(f"Added datasource: {args.value}")
            return f"Added datasource '{args.value}'"

        elif args.operation == "replace-datasource":
            old, new = args.value.split(",", 1)
            dashboard.datasources.replace(old, new)
            dashboard.save(f"Replaced datasource: {old} -> {new}")
            return f"Replaced datasource '{old}' with '{new}'"

        elif args.operation == "add-variable":
            # Format: name|query|datasource_uid|regex (using | as delimiter to allow commas in query)
            parts = args.value.split("|", 3)
            if len(parts) < 3:
                raise ValueError("Format: name|query|datasource_uid|regex (use | as delimiter, regex is optional)")
            regex = parts[3] if len(parts) > 3 else None
            dashboard.variables.add_query(
                name=parts[0],
                query=parts[1],
                datasource_uid=parts[2],
                regex=regex
            )
            dashboard.save(f"Added variable: {parts[0]}")
            return f"Added variable '${parts[0]}'"

        else:
            raise ValueError(f"Unknown operation: {args.operation}")

    # Apply to all dashboards in folder tree
    results = folder.apply_to_tree(apply_operation, recursive=not args.no_recursive)

    # Print results
    print(f"\nResults for folder tree: {folder.title}")
    print("-" * 80)

    success_count = 0
    error_count = 0

    for result in results:
        folder_name = result.get("folder", "Unknown")
        dash_title = result.get("dashboard_title", "Unknown")
        status = result.get("status")

        if status == "success":
            print(f"✓ [{folder_name}] {dash_title}: {result.get('result', 'Done')}")
            success_count += 1
        else:
            print(f"❌ [{folder_name}] {dash_title}: {result.get('error', 'Error')}")
            error_count += 1

    print("-" * 80)
    print(f"Total: {success_count} successful, {error_count} failed")


def cmd_folder_list_dashboards(args):
    """List all dashboards in folder and sub-folders"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    folder = Folder.find(client, args.uid)

    if not folder:
        print(f"❌ Folder '{args.uid}' not found")
        return

    if args.recursive:
        dashboards = folder.all_dashboards_recursive()
        source = f"folder tree '{folder.title}' (recursive)"
    else:
        dashboards = folder.dashboards()
        source = f"folder '{folder.title}'"

    if args.json:
        import json
        print(json.dumps([{
            "uid": d.uid,
            "title": d.title
        } for d in dashboards], indent=2))
    else:
        print(f"Dashboards in {source}:")
        print(f"{'UID':<25} {'Title'}")
        print("-" * 80)
        for dash in dashboards:
            print(f"{dash.uid:<25} {dash.title}")
        print(f"Total: {len(dashboards)} dashboards")


def cmd_folder_debug(args):
    """Debug: Show raw folder data from API"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    folders = client.list_folders()

    import json
    print("Raw folder data from API:")
    print(json.dumps(folders, indent=2))


def cmd_list_dashboards(args):
    """List dashboards"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)

    if args.folder:
        folder = Folder.find(client, args.folder)
        if not folder:
            print(f"❌ Folder '{args.folder}' not found")
            return
        dashboards = folder.dashboards()
    else:
        dashboards = client.list_dashboards()

    if args.json:
        import json
        print(json.dumps([{"uid": d["uid"], "title": d["title"]} for d in dashboards], indent=2))
    else:
        print(f"{'UID':<20} {'Title':<40} {'Folder'}")
        print("-" * 80)
        for dash in dashboards:
            folder_title = dash.get("folderTitle", "")
            print(f"{dash['uid']:<20} {dash['title']:<40} {folder_title}")


def cmd_get_dashboard(args):
    """Get dashboard details"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.uid)

    if not dashboard:
        print(f"❌ Dashboard '{args.uid}' not found")
        return

    if args.json:
        import json
        print(json.dumps(dashboard._load_data(), indent=2))
    else:
        print(f"UID: {dashboard.uid}")
        print(f"Title: {dashboard.title}")
        print(f"Folder: {dashboard.folder.title if dashboard.folder else 'None'}")
        print(f"Tags: {', '.join(dashboard.tags)}")
        print(f"Panels: {len(dashboard.panels.list_all())}")
        print(f"Variables: {len(dashboard.variables.list_all())}")


def cmd_create_dashboard(args):
    """Create a new dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)

    folder = None
    if args.folder:
        folder = Folder.find(client, args.folder)
        if not folder:
            print(f"❌ Folder '{args.folder}' not found")
            return

    tags = args.tags.split(",") if args.tags else []
    dashboard = Dashboard.create(client, args.title, folder=folder, tags=tags)

    print(f"✓ Created dashboard: {dashboard.title} (UID: {dashboard.uid})")


def cmd_duplicate_dashboard(args):
    """Duplicate a dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    source = Dashboard.find(client, args.uid)

    if not source:
        print(f"❌ Dashboard '{args.uid}' not found")
        return

    folder = None
    if args.folder:
        folder = Folder.find(client, args.folder)

    new_dashboard = source.duplicate(args.title, folder=folder)
    print(f"✓ Duplicated dashboard: {new_dashboard.uid}")


def cmd_delete_dashboard(args):
    """Delete a dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.uid)

    if not dashboard:
        print(f"❌ Dashboard '{args.uid}' not found")
        return

    if not args.force:
        confirm = input(f"Delete dashboard '{dashboard.title}'? (y/N): ")
        if confirm.lower() != 'y':
            print("Cancelled")
            return

    dashboard.delete()
    print(f"✓ Deleted dashboard: {args.uid}")


def cmd_export_dashboard(args):
    """Export dashboard to file"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.uid)

    if not dashboard:
        print(f"❌ Dashboard '{args.uid}' not found")
        return

    if not args.force:
        confirm = input(f"Delete dashboard '{dashboard.title}'? (y/N): ")
        if confirm.lower() != 'y':
            print("Cancelled")
            return

    dashboard.delete()
    print(f"✓ Deleted dashboard: {args.uid}")


def cmd_export_dashboard(args):
    """Export dashboard to file"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.uid)

    if not dashboard:
        print(f"❌ Dashboard '{args.uid}' not found")
        return

    dashboard.export(args.file)
    print(f"✓ Exported dashboard to: {args.file}")


# ============================================================================
# Datasource Commands
# ============================================================================

def cmd_ds_add(args):
    """Add datasource to dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.dashboard)

    if not dashboard:
        print(f"❌ Dashboard '{args.dashboard}' not found")
        return

    dashboard.datasources.add(args.datasource)
    dashboard.save(f"Added datasource {args.datasource}")
    print(f"✓ Added datasource '{args.datasource}' to dashboard")


def cmd_ds_replace(args):
    """Replace datasource in dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.dashboard)

    if not dashboard:
        print(f"❌ Dashboard '{args.dashboard}' not found")
        return

    dashboard.datasources.replace(args.old, args.new)
    dashboard.save(f"Replaced datasource {args.old} with {args.new}")
    print(f"✓ Replaced '{args.old}' with '{args.new}'")


def cmd_ds_remove(args):
    """Remove datasource from dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.dashboard)

    if not dashboard:
        print(f"❌ Dashboard '{args.dashboard}' not found")
        return

    dashboard.datasources.remove(args.datasource)
    dashboard.save(f"Removed datasource {args.datasource}")
    print(f"✓ Removed datasource '{args.datasource}'")


def cmd_ds_list(args):
    """List datasources used in dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.dashboard)

    if not dashboard:
        print(f"❌ Dashboard '{args.dashboard}' not found")
        return

    used = dashboard.datasources.list_used()
    print(f"Datasources in '{dashboard.title}':")
    for ds in used:
        print(f"  - {ds['uid']} ({ds['type']})")


# ============================================================================
# Panel Commands
# ============================================================================

def cmd_panel_add_timeseries(args):
    """Add timeseries panel to dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.dashboard)

    if not dashboard:
        print(f"❌ Dashboard '{args.dashboard}' not found")
        return

    dashboard.panels.add_timeseries(
        title=args.title,
        expr=args.expr,
        datasource_uid=args.datasource,
        legend_format=args.legend
    )
    dashboard.save(f"Added panel: {args.title}")
    print(f"✓ Added timeseries panel '{args.title}'")


def cmd_panel_add_stat(args):
    """Add stat panel to dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.dashboard)

    if not dashboard:
        print(f"❌ Dashboard '{args.dashboard}' not found")
        return

    dashboard.panels.add_stat(
        title=args.title,
        expr=args.expr,
        datasource_uid=args.datasource
    )
    dashboard.save(f"Added panel: {args.title}")
    print(f"✓ Added stat panel '{args.title}'")


def cmd_panel_add_gauge(args):
    """Add gauge panel to dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.dashboard)

    if not dashboard:
        print(f"❌ Dashboard '{args.dashboard}' not found")
        return

    dashboard.panels.add_gauge(
        title=args.title,
        expr=args.expr,
        datasource_uid=args.datasource,
        min=args.min,
        max=args.max
    )
    dashboard.save(f"Added panel: {args.title}")
    print(f"✓ Added gauge panel '{args.title}'")


def cmd_panel_list(args):
    """List panels in dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.dashboard)

    if not dashboard:
        print(f"❌ Dashboard '{args.dashboard}' not found")
        return

    panels = dashboard.panels.list_all()
    print(f"Panels in '{dashboard.title}':")
    print(f"{'ID':<6} {'Type':<15} {'Title'}")
    print("-" * 60)
    for panel in panels:
        panel_type = panel.get("type", "unknown")
        title = panel.get("title", "Untitled")
        panel_id = panel.get("id", "")
        print(f"{panel_id:<6} {panel_type:<15} {title}")


def cmd_panel_remove(args):
    """Remove panel from dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.dashboard)

    if not dashboard:
        print(f"❌ Dashboard '{args.dashboard}' not found")
        return

    dashboard.panels.remove(args.panel_id)
    dashboard.save(f"Removed panel {args.panel_id}")
    print(f"✓ Removed panel {args.panel_id}")


# ============================================================================
# Variable Commands
# ============================================================================

def cmd_var_add_query(args):
    """Add query variable to dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.dashboard)

    if not dashboard:
        print(f"❌ Dashboard '{args.dashboard}' not found")
        return

    dashboard.variables.add_query(
        name=args.name,
        query=args.query,
        datasource_uid=args.datasource,
        multi=args.multi,
        label=args.label,
        regex=args.regex
    )
    dashboard.save(f"Added variable: {args.name}")
    print(f"✓ Added query variable '${args.name}'")


def cmd_var_add_custom(args):
    """Add custom variable to dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.dashboard)

    if not dashboard:
        print(f"❌ Dashboard '{args.dashboard}' not found")
        return

    values = args.values.split(",")
    dashboard.variables.add_custom(
        name=args.name,
        values=values,
        multi=args.multi
    )
    dashboard.save(f"Added variable: {args.name}")
    print(f"✓ Added custom variable '${args.name}'")


def cmd_var_add_interval(args):
    """Add interval variable to dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.dashboard)

    if not dashboard:
        print(f"❌ Dashboard '{args.dashboard}' not found")
        return

    dashboard.variables.add_interval(name=args.name)
    dashboard.save(f"Added variable: {args.name}")
    print(f"✓ Added interval variable '${args.name}'")


def cmd_var_add_constant(args):
    """Add constant variable to dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.dashboard)

    if not dashboard:
        print(f"❌ Dashboard '{args.dashboard}' not found")
        return

    dashboard.variables.add_constant(
        name=args.name,
        value=args.value
    )
    dashboard.save(f"Added variable: {args.name}")
    print(f"✓ Added constant variable '${args.name}'")


def cmd_var_list(args):
    """List variables in dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.dashboard)

    if not dashboard:
        print(f"❌ Dashboard '{args.dashboard}' not found")
        return

    variables = dashboard.variables.list_all()
    print(f"Variables in '{dashboard.title}':")
    print(f"{'Name':<20} {'Type':<15} {'Multi'}")
    print("-" * 50)
    for var in variables:
        name = var.get("name", "")
        var_type = var.get("type", "unknown")
        multi = var.get("multi", False)
        print(f"${name:<19} {var_type:<15} {multi}")


def cmd_var_remove(args):
    """Remove variable from dashboard"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.dashboard)

    if not dashboard:
        print(f"❌ Dashboard '{args.dashboard}' not found")
        return

    dashboard.variables.remove(args.name)
    dashboard.save(f"Removed variable: {args.name}")
    print(f"✓ Removed variable '${args.name}'")


def cmd_var_edit_regex(args):
    """Edit regex on existing variable"""
    client = GrafanaClient(url=args.url, api_key=args.api_key)
    dashboard = Dashboard.find(client, args.dashboard)

    if not dashboard:
        print(f"❌ Dashboard '{args.dashboard}' not found")
        return

    dashboard.variables.edit(args.name, regex=args.regex)
    dashboard.save(f"Updated regex for variable: {args.name}")
    print(f"✓ Updated regex for '${args.name}' to: {args.regex}")


# ============================================================================
# Main CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Grafana Dashboard Manager CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List folders
  python cli.py folder list

  # Create folder
  python cli.py folder create "My Folder" --uid my-folder

  # Show folder tree
  python cli.py folder tree
  python cli.py folder tree --uid monitoring

  # List dashboards in folder (recursive)
  python cli.py folder list-dashboards monitoring --recursive

  # Apply operation to all dashboards in folder tree
  python cli.py folder apply monitoring add-tag "production"
  python cli.py folder apply monitoring replace-datasource "Prometheus-Old,Prometheus-New"
  python cli.py folder apply overview add-variable "job|label_values(job)|ds-uid"
  python cli.py folder apply overview add-variable "namespace|label_values(kube_pod_info,namespace)|ds-uid|/^(dev|prod)$/"

  # List dashboards
  python cli.py dashboard list

  # Get dashboard details
  python cli.py dashboard get abc123

  # Create dashboard
  python cli.py dashboard create "My Dashboard" --folder monitoring --tags prod

  # Add datasource
  python cli.py ds add abc123 Prometheus-Prod

  # Replace datasource
  python cli.py ds replace abc123 Prometheus-Old Prometheus-New

  # Add timeseries panel
  python cli.py panel add-timeseries abc123 "CPU Usage" --expr "cpu_usage" --datasource uid123

  # Add query variable
  python cli.py var add-query abc123 job --query "label_values(job)" --datasource uid123

  # Add query variable with regex
  python cli.py var add-query abc123 namespace --query "label_values(kube_pod_info,namespace)" --datasource uid123 --regex "/.*prod.*/"

  # Edit regex on existing variable
  python cli.py var edit-regex abc123 namespace "/.*Production.*/"
        """
    )

    # Global options
    parser.add_argument("--url", default=os.getenv("GRAFANA_URL", "http://localhost:3000"),
                        help="Grafana URL (default: from env GRAFANA_URL)")
    parser.add_argument("--api-key", default=os.getenv("GRAFANA_API_KEY"),
                        help="Grafana API key (default: from env GRAFANA_API_KEY)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ============================================================================
    # Folder commands
    # ============================================================================
    folder_parser = subparsers.add_parser("folder", help="Manage folders")
    folder_subparsers = folder_parser.add_subparsers(dest="subcommand")

    # folder list
    list_folders_parser = folder_subparsers.add_parser("list", help="List all folders")
    list_folders_parser.set_defaults(func=cmd_list_folders)

    # folder create
    create_folder_parser = folder_subparsers.add_parser("create", help="Create new folder")
    create_folder_parser.add_argument("title", help="Folder title")
    create_folder_parser.add_argument("--uid", help="Folder UID")
    create_folder_parser.set_defaults(func=cmd_create_folder)

    # folder tree
    tree_folder_parser = folder_subparsers.add_parser("tree", help="Show folder tree structure")
    tree_folder_parser.add_argument("--uid", help="Root folder UID (shows full tree if not specified)")
    tree_folder_parser.set_defaults(func=cmd_folder_tree)

    # folder apply
    apply_folder_parser = folder_subparsers.add_parser("apply", help="Apply operation to all dashboards in folder tree")
    apply_folder_parser.add_argument("uid", help="Folder UID")
    apply_folder_parser.add_argument("operation", choices=[
        "add-tag", "remove-tag", "add-datasource", "replace-datasource", "add-variable"
    ], help="Operation to perform")
    apply_folder_parser.add_argument("value", help="Operation value (tag name, datasource name, etc.)")
    apply_folder_parser.add_argument("--no-recursive", action="store_true", help="Only apply to this folder, not sub-folders")
    apply_folder_parser.set_defaults(func=cmd_folder_apply)

    # folder list-dashboards
    list_dash_folder_parser = folder_subparsers.add_parser("list-dashboards", help="List dashboards in folder")
    list_dash_folder_parser.add_argument("uid", help="Folder UID")
    list_dash_folder_parser.add_argument("--recursive", "-r", action="store_true", help="Include sub-folders")
    list_dash_folder_parser.set_defaults(func=cmd_folder_list_dashboards)

    # folder debug
    debug_folder_parser = folder_subparsers.add_parser("debug", help="Debug: Show raw folder data from API")
    debug_folder_parser.set_defaults(func=cmd_folder_debug)

    # ============================================================================
    # Dashboard commands
    # ============================================================================
    dash_parser = subparsers.add_parser("dashboard", help="Manage dashboards")
    dash_subparsers = dash_parser.add_subparsers(dest="subcommand")

    # dashboard list
    list_dash_parser = dash_subparsers.add_parser("list", help="List dashboards")
    list_dash_parser.add_argument("--folder", help="Filter by folder UID")
    list_dash_parser.set_defaults(func=cmd_list_dashboards)

    # dashboard get
    get_dash_parser = dash_subparsers.add_parser("get", help="Get dashboard details")
    get_dash_parser.add_argument("uid", help="Dashboard UID")
    get_dash_parser.set_defaults(func=cmd_get_dashboard)

    # dashboard create
    create_dash_parser = dash_subparsers.add_parser("create", help="Create dashboard")
    create_dash_parser.add_argument("title", help="Dashboard title")
    create_dash_parser.add_argument("--folder", help="Folder UID")
    create_dash_parser.add_argument("--tags", help="Comma-separated tags")
    create_dash_parser.set_defaults(func=cmd_create_dashboard)

    # dashboard duplicate
    dup_dash_parser = dash_subparsers.add_parser("duplicate", help="Duplicate dashboard")
    dup_dash_parser.add_argument("uid", help="Source dashboard UID")
    dup_dash_parser.add_argument("title", help="New dashboard title")
    dup_dash_parser.add_argument("--folder", help="Target folder UID")
    dup_dash_parser.set_defaults(func=cmd_duplicate_dashboard)

    # dashboard delete
    del_dash_parser = dash_subparsers.add_parser("delete", help="Delete dashboard")
    del_dash_parser.add_argument("uid", help="Dashboard UID")
    del_dash_parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    del_dash_parser.set_defaults(func=cmd_delete_dashboard)

    # dashboard export
    export_dash_parser = dash_subparsers.add_parser("export", help="Export dashboard")
    export_dash_parser.add_argument("uid", help="Dashboard UID")
    export_dash_parser.add_argument("file", help="Output file path")
    export_dash_parser.set_defaults(func=cmd_export_dashboard)

    # ============================================================================
    # Datasource commands
    # ============================================================================
    ds_parser = subparsers.add_parser("ds", help="Manage datasources in dashboards")
    ds_subparsers = ds_parser.add_subparsers(dest="subcommand")

    # ds add
    ds_add_parser = ds_subparsers.add_parser("add", help="Add datasource to dashboard")
    ds_add_parser.add_argument("dashboard", help="Dashboard UID")
    ds_add_parser.add_argument("datasource", help="Datasource name")
    ds_add_parser.set_defaults(func=cmd_ds_add)

    # ds replace
    ds_replace_parser = ds_subparsers.add_parser("replace", help="Replace datasource")
    ds_replace_parser.add_argument("dashboard", help="Dashboard UID")
    ds_replace_parser.add_argument("old", help="Old datasource name")
    ds_replace_parser.add_argument("new", help="New datasource name")
    ds_replace_parser.set_defaults(func=cmd_ds_replace)

    # ds remove
    ds_remove_parser = ds_subparsers.add_parser("remove", help="Remove datasource")
    ds_remove_parser.add_argument("dashboard", help="Dashboard UID")
    ds_remove_parser.add_argument("datasource", help="Datasource name")
    ds_remove_parser.set_defaults(func=cmd_ds_remove)

    # ds list
    ds_list_parser = ds_subparsers.add_parser("list", help="List datasources in dashboard")
    ds_list_parser.add_argument("dashboard", help="Dashboard UID")
    ds_list_parser.set_defaults(func=cmd_ds_list)

    # ============================================================================
    # Panel commands
    # ============================================================================
    panel_parser = subparsers.add_parser("panel", help="Manage panels")
    panel_subparsers = panel_parser.add_subparsers(dest="subcommand")

    # panel add-timeseries
    panel_ts_parser = panel_subparsers.add_parser("add-timeseries", help="Add timeseries panel")
    panel_ts_parser.add_argument("dashboard", help="Dashboard UID")
    panel_ts_parser.add_argument("title", help="Panel title")
    panel_ts_parser.add_argument("--expr", required=True, help="PromQL expression")
    panel_ts_parser.add_argument("--datasource", required=True, help="Datasource UID")
    panel_ts_parser.add_argument("--legend", help="Legend format")
    panel_ts_parser.set_defaults(func=cmd_panel_add_timeseries)

    # panel add-stat
    panel_stat_parser = panel_subparsers.add_parser("add-stat", help="Add stat panel")
    panel_stat_parser.add_argument("dashboard", help="Dashboard UID")
    panel_stat_parser.add_argument("title", help="Panel title")
    panel_stat_parser.add_argument("--expr", required=True, help="PromQL expression")
    panel_stat_parser.add_argument("--datasource", required=True, help="Datasource UID")
    panel_stat_parser.set_defaults(func=cmd_panel_add_stat)

    # panel add-gauge
    panel_gauge_parser = panel_subparsers.add_parser("add-gauge", help="Add gauge panel")
    panel_gauge_parser.add_argument("dashboard", help="Dashboard UID")
    panel_gauge_parser.add_argument("title", help="Panel title")
    panel_gauge_parser.add_argument("--expr", required=True, help="PromQL expression")
    panel_gauge_parser.add_argument("--datasource", required=True, help="Datasource UID")
    panel_gauge_parser.add_argument("--min", type=float, default=0, help="Min value")
    panel_gauge_parser.add_argument("--max", type=float, default=100, help="Max value")
    panel_gauge_parser.set_defaults(func=cmd_panel_add_gauge)

    # panel list
    panel_list_parser = panel_subparsers.add_parser("list", help="List panels")
    panel_list_parser.add_argument("dashboard", help="Dashboard UID")
    panel_list_parser.set_defaults(func=cmd_panel_list)

    # panel remove
    panel_remove_parser = panel_subparsers.add_parser("remove", help="Remove panel")
    panel_remove_parser.add_argument("dashboard", help="Dashboard UID")
    panel_remove_parser.add_argument("panel_id", type=int, help="Panel ID")
    panel_remove_parser.set_defaults(func=cmd_panel_remove)

    # ============================================================================
    # Variable commands
    # ============================================================================
    var_parser = subparsers.add_parser("var", help="Manage variables")
    var_subparsers = var_parser.add_subparsers(dest="subcommand")

    # var add-query
    var_query_parser = var_subparsers.add_parser("add-query", help="Add query variable")
    var_query_parser.add_argument("dashboard", help="Dashboard UID")
    var_query_parser.add_argument("name", help="Variable name")
    var_query_parser.add_argument("--query", required=True, help="Query string")
    var_query_parser.add_argument("--datasource", required=True, help="Datasource UID")
    var_query_parser.add_argument("--multi", action="store_true", help="Allow multiple values")
    var_query_parser.add_argument("--label", help="Display label")
    var_query_parser.add_argument("--regex", help="Regex pattern (e.g., /.*prod.*/)")
    var_query_parser.set_defaults(func=cmd_var_add_query)

    # var add-custom
    var_custom_parser = var_subparsers.add_parser("add-custom", help="Add custom variable")
    var_custom_parser.add_argument("dashboard", help="Dashboard UID")
    var_custom_parser.add_argument("name", help="Variable name")
    var_custom_parser.add_argument("--values", required=True, help="Comma-separated values")
    var_custom_parser.add_argument("--multi", action="store_true", help="Allow multiple values")
    var_custom_parser.set_defaults(func=cmd_var_add_custom)

    # var add-interval
    var_interval_parser = var_subparsers.add_parser("add-interval", help="Add interval variable")
    var_interval_parser.add_argument("dashboard", help="Dashboard UID")
    var_interval_parser.add_argument("--name", default="interval", help="Variable name")
    var_interval_parser.set_defaults(func=cmd_var_add_interval)

    # var add-constant
    var_constant_parser = var_subparsers.add_parser("add-constant", help="Add constant variable")
    var_constant_parser.add_argument("dashboard", help="Dashboard UID")
    var_constant_parser.add_argument("name", help="Variable name")
    var_constant_parser.add_argument("--value", required=True, help="Constant value")
    var_constant_parser.set_defaults(func=cmd_var_add_constant)

    # var list
    var_list_parser = var_subparsers.add_parser("list", help="List variables")
    var_list_parser.add_argument("dashboard", help="Dashboard UID")
    var_list_parser.set_defaults(func=cmd_var_list)

    # var remove
    var_remove_parser = var_subparsers.add_parser("remove", help="Remove variable")
    var_remove_parser.add_argument("dashboard", help="Dashboard UID")
    var_remove_parser.add_argument("name", help="Variable name")
    var_remove_parser.set_defaults(func=cmd_var_remove)

    # var edit-regex
    var_regex_parser = var_subparsers.add_parser("edit-regex", help="Edit regex on variable")
    var_regex_parser.add_argument("dashboard", help="Dashboard UID")
    var_regex_parser.add_argument("name", help="Variable name")
    var_regex_parser.add_argument("regex", help="Regex pattern (e.g., /.*prod.*/)")
    var_regex_parser.set_defaults(func=cmd_var_edit_regex)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    if hasattr(args, "func"):
        try:
            args.func(args)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
