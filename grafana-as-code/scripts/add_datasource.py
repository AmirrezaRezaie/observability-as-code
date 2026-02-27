#!/usr/bin/env python3
"""
Add data source to dashboard panels and variables
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import GrafanaClient, DatasourceManager, DashboardManager
from dotenv import load_dotenv

load_dotenv()


def add_datasource_to_dashboard(
    dashboard_uid: str,
    datasource_name: str,
    update_panels: bool = True,
    update_variables: bool = True
):
    """
    Add data source to a dashboard

    Args:
        dashboard_uid: Dashboard UID
        datasource_name: Name of data source to add
        update_panels: Update data source in panels
        update_variables: Update data source in variables
    """
    client = GrafanaClient()
    dashboard_mgr = DashboardManager(client)
    ds_mgr = DatasourceManager(client)

    # Verify data source exists
    datasource = ds_mgr.get_datasource_by_name(datasource_name)
    if not datasource:
        print(f"❌ Error: Data source '{datasource_name}' not found")
        print(f"Available data sources:")
        for ds in ds_mgr.list_datasources():
            print(f"  - {ds['name']} (type: {ds['type']})")
        return

    print(f"✓ Found data source: {datasource_name}")

    if update_panels:
        result = dashboard_mgr.add_datasource_to_panels(dashboard_uid, datasource_name)
        print(f"✓ Updated panels in dashboard {dashboard_uid}")

    if update_variables:
        result = dashboard_mgr.add_datasource_to_variables(dashboard_uid, datasource_name)
        print(f"✓ Updated variables in dashboard {dashboard_uid}")


def add_datasource_to_multiple(
    dashboard_uids: list,
    datasource_name: str
):
    """Add data source to multiple dashboards"""
    client = GrafanaClient()
    ds_mgr = DatasourceManager(client)

    # Verify data source exists
    datasource = ds_mgr.get_datasource_by_name(datasource_name)
    if not datasource:
        print(f"❌ Error: Data source '{datasource_name}' not found")
        return

    for uid in dashboard_uids:
        try:
            add_datasource_to_dashboard(uid, datasource_name)
            print(f"✓ Completed dashboard {uid}")
        except Exception as e:
            print(f"❌ Failed for dashboard {uid}: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add data source to Grafana dashboards")
    parser.add_argument("dashboard_uid", help="Dashboard UID (or comma-separated for multiple)")
    parser.add_argument("datasource_name", help="Name of data source to add")
    parser.add_argument("--panels", action="store_true", default=True, help="Update panels")
    parser.add_argument("--no-panels", action="store_false", dest="panels", help="Don't update panels")
    parser.add_argument("--variables", action="store_true", default=True, help="Update variables")
    parser.add_argument("--no-variables", action="store_false", dest="variables", help="Don't update variables")

    args = parser.parse_args()

    dashboard_uids = [uid.strip() for uid in args.dashboard_uid.split(",")]

    if len(dashboard_uids) == 1:
        add_datasource_to_dashboard(
            dashboard_uids[0],
            args.datasource_name,
            update_panels=args.panels,
            update_variables=args.variables
        )
    else:
        add_datasource_to_multiple(dashboard_uids, args.datasource_name)
