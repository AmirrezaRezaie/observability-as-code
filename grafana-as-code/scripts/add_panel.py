#!/usr/bin/env python3
"""
Add panels to Grafana dashboards
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import GrafanaClient, PanelManager, DatasourceManager
from dotenv import load_dotenv

load_dotenv()


def add_timeseries_panel(
    dashboard_uid: str,
    title: str,
    expr: str,
    datasource_name: str,
    legend_format: str = None
):
    """
    Add a time series panel to dashboard

    Args:
        dashboard_uid: Dashboard UID
        title: Panel title
        expr: PromQL expression
        datasource_name: Name of data source
        legend_format: Legend format (e.g., "{{instance}}")
    """
    client = GrafanaClient()
    panel_mgr = PanelManager(client)
    ds_mgr = DatasourceManager(client)

    # Get datasource
    datasource = ds_mgr.get_datasource_by_name(datasource_name)
    if not datasource:
        print(f"❌ Error: Data source '{datasource_name}' not found")
        return

    # Create panel
    panel = panel_mgr.create_timeseries_panel(
        title=title,
        expr=expr,
        datasource_uid=datasource["uid"],
        legend_format=legend_format
    )

    # Add to dashboard
    result = panel_mgr.add_panel_to_dashboard(dashboard_uid, panel)
    print(f"✓ Added time series panel '{title}' to dashboard {dashboard_uid}")


def add_stat_panel(
    dashboard_uid: str,
    title: str,
    expr: str,
    datasource_name: str
):
    """
    Add a stat panel to dashboard

    Args:
        dashboard_uid: Dashboard UID
        title: Panel title
        expr: PromQL expression
        datasource_name: Name of data source
    """
    client = GrafanaClient()
    panel_mgr = PanelManager(client)
    ds_mgr = DatasourceManager(client)

    datasource = ds_mgr.get_datasource_by_name(datasource_name)
    if not datasource:
        print(f"❌ Error: Data source '{datasource_name}' not found")
        return

    panel = panel_mgr.create_stat_panel(
        title=title,
        expr=expr,
        datasource_uid=datasource["uid"]
    )

    result = panel_mgr.add_panel_to_dashboard(dashboard_uid, panel)
    print(f"✓ Added stat panel '{title}' to dashboard {dashboard_uid}")


def add_gauge_panel(
    dashboard_uid: str,
    title: str,
    expr: str,
    datasource_name: str,
    min_val: float = 0,
    max_val: float = 100
):
    """
    Add a gauge panel to dashboard

    Args:
        dashboard_uid: Dashboard UID
        title: Panel title
        expr: PromQL expression
        datasource_name: Name of data source
        min_val: Minimum value
        max_val: Maximum value
    """
    client = GrafanaClient()
    panel_mgr = PanelManager(client)
    ds_mgr = DatasourceManager(client)

    datasource = ds_mgr.get_datasource_by_name(datasource_name)
    if not datasource:
        print(f"❌ Error: Data source '{datasource_name}' not found")
        return

    panel = panel_mgr.create_gauge_panel(
        title=title,
        expr=expr,
        datasource_uid=datasource["uid"],
        min=min_val,
        max=max_val
    )

    result = panel_mgr.add_panel_to_dashboard(dashboard_uid, panel)
    print(f"✓ Added gauge panel '{title}' to dashboard {dashboard_uid}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add panel to Grafana dashboard")
    parser.add_argument("dashboard_uid", help="Dashboard UID")
    parser.add_argument("title", help="Panel title")
    parser.add_argument("expr", help="Metric expression (PromQL)")
    parser.add_argument("datasource", help="Data source name")
    parser.add_argument("--type", choices=["timeseries", "stat", "gauge"], default="timeseries",
                        help="Panel type (default: timeseries)")
    parser.add_argument("--legend", help="Legend format (e.g., '{{instance}}')")
    parser.add_argument("--min", type=float, default=0, help="Min value for gauge (default: 0)")
    parser.add_argument("--max", type=float, default=100, help="Max value for gauge (default: 100)")

    args = parser.parse_args()

    if args.type == "timeseries":
        add_timeseries_panel(
            args.dashboard_uid,
            args.title,
            args.expr,
            args.datasource,
            args.legend
        )
    elif args.type == "stat":
        add_stat_panel(
            args.dashboard_uid,
            args.title,
            args.expr,
            args.datasource
        )
    elif args.type == "gauge":
        add_gauge_panel(
            args.dashboard_uid,
            args.title,
            args.expr,
            args.datasource,
            args.min,
            args.max
        )
