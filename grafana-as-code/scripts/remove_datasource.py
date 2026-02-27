#!/usr/bin/env python3
"""
Remove data source from dashboards
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import GrafanaClient, DatasourceManager
from dotenv import load_dotenv

load_dotenv()


def remove_datasource_from_dashboards(
    datasource_name: str,
    dashboard_uids: list = None
):
    """
    Remove data source references from dashboards

    Args:
        datasource_name: Name of data source to remove
        dashboard_uids: List of dashboard UIDs (None = all dashboards)
    """
    client = GrafanaClient()
    ds_mgr = DatasourceManager(client)

    print(f"Removing data source '{datasource_name}' from dashboards...")

    if dashboard_uids is None:
        # Find all dashboards using this datasource
        usage = ds_mgr.find_datasource_usage(datasource_name)
        dashboard_uids = [u["dashboard"]["uid"] for u in usage]
        print(f"Found {len(dashboard_uids)} dashboards using this data source")

    results = ds_mgr.remove_datasource_from_dashboards(datasource_name, dashboard_uids)

    for result in results:
        uid = result["uid"]
        status = result["status"]
        if status == "success":
            print(f"✓ Removed from dashboard {uid}")
        elif status == "no changes":
            print(f"- No changes needed for dashboard {uid}")
        else:
            print(f"❌ Failed for dashboard {uid}: {result.get('error')}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Remove data source from Grafana dashboards")
    parser.add_argument("datasource_name", help="Name of data source to remove")
    parser.add_argument(
        "--dashboards",
        help="Comma-separated dashboard UIDs (default: all using the datasource)"
    )

    args = parser.parse_args()

    dashboard_uids = None
    if args.dashboards:
        dashboard_uids = [uid.strip() for uid in args.dashboards.split(",")]

    remove_datasource_from_dashboards(args.datasource_name, dashboard_uids)
