#!/usr/bin/env python3
"""
Add template variables to Grafana dashboards
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import GrafanaClient, VariableManager, DatasourceManager
from dotenv import load_dotenv

load_dotenv()


def add_query_variable(
    dashboard_uid: str,
    name: str,
    query: str,
    datasource_name: str,
    multi: bool = False,
    label: str = None
):
    """
    Add a query variable to dashboard

    Args:
        dashboard_uid: Dashboard UID
        name: Variable name
        query: Query string (e.g., "label_values(job)")
        datasource_name: Name of data source
        multi: Allow multiple values
        label: Display label
    """
    client = GrafanaClient()
    var_mgr = VariableManager(client)
    ds_mgr = DatasourceManager(client)

    # Get datasource
    datasource = ds_mgr.get_datasource_by_name(datasource_name)
    if not datasource:
        print(f"❌ Error: Data source '{datasource_name}' not found")
        return

    # Create variable
    variable = var_mgr.create_query_variable(
        name=name,
        query=query,
        datasource_uid=datasource["uid"],
        multi=multi,
        label=label
    )

    # Add to dashboard
    result = var_mgr.add_variable_to_dashboard(dashboard_uid, variable)
    print(f"✓ Added query variable '${name}' to dashboard {dashboard_uid}")


def add_custom_variable(
    dashboard_uid: str,
    name: str,
    values: list,
    multi: bool = False
):
    """
    Add a custom variable to dashboard

    Args:
        dashboard_uid: Dashboard UID
        name: Variable name
        values: List of values
        multi: Allow multiple values
    """
    client = GrafanaClient()
    var_mgr = VariableManager(client)

    variable = var_mgr.create_custom_variable(
        name=name,
        values=values,
        multi=multi
    )

    result = var_mgr.add_variable_to_dashboard(dashboard_uid, variable)
    print(f"✓ Added custom variable '${name}' to dashboard {dashboard_uid}")


def add_interval_variable(
    dashboard_uid: str,
    name: str = "interval"
):
    """
    Add an interval variable to dashboard

    Args:
        dashboard_uid: Dashboard UID
        name: Variable name (default: "interval")
    """
    client = GrafanaClient()
    var_mgr = VariableManager(client)

    variable = var_mgr.create_interval_variable(name=name)

    result = var_mgr.add_variable_to_dashboard(dashboard_uid, variable)
    print(f"✓ Added interval variable '${name}' to dashboard {dashboard_uid}")


def add_constant_variable(
    dashboard_uid: str,
    name: str,
    value: str
):
    """
    Add a constant variable to dashboard

    Args:
        dashboard_uid: Dashboard UID
        name: Variable name
        value: Constant value
    """
    client = GrafanaClient()
    var_mgr = VariableManager(client)

    variable = var_mgr.create_constant_variable(
        name=name,
        value=value
    )

    result = var_mgr.add_variable_to_dashboard(dashboard_uid, variable)
    print(f"✓ Added constant variable '${name}' to dashboard {dashboard_uid}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add variable to Grafana dashboard")
    parser.add_argument("dashboard_uid", help="Dashboard UID")
    parser.add_argument("name", help="Variable name")
    parser.add_argument("--type", choices=["query", "custom", "interval", "constant"],
                        default="query", help="Variable type (default: query)")

    # Query variable args
    parser.add_argument("--query", help="Query string (for query type)")
    parser.add_argument("--datasource", help="Data source name (for query type)")
    parser.add_argument("--multi", action="store_true", help="Allow multiple values")
    parser.add_argument("--label", help="Display label")

    # Custom variable args
    parser.add_argument("--values", help="Comma-separated values (for custom type)")

    # Constant variable args
    parser.add_argument("--value", help="Constant value (for constant type)")

    args = parser.parse_args()

    if args.type == "query":
        if not args.query or not args.datasource:
            print("❌ Error: --query and --datasource required for query type")
            sys.exit(1)
        add_query_variable(
            args.dashboard_uid,
            args.name,
            args.query,
            args.datasource,
            args.multi,
            args.label
        )

    elif args.type == "custom":
        if not args.values:
            print("❌ Error: --values required for custom type")
            sys.exit(1)
        values = [v.strip() for v in args.values.split(",")]
        add_custom_variable(
            args.dashboard_uid,
            args.name,
            values,
            args.multi
        )

    elif args.type == "interval":
        add_interval_variable(args.dashboard_uid, args.name)

    elif args.type == "constant":
        if not args.value:
            print("❌ Error: --value required for constant type")
            sys.exit(1)
        add_constant_variable(
            args.dashboard_uid,
            args.name,
            args.value
        )
