"""
Variable Management Module
Operations for managing dashboard template variables
"""

from typing import Dict, List, Any, Optional
from .client import GrafanaClient


class VariableManager:
    """Manager for template variable operations"""

    def __init__(self, client: GrafanaClient):
        """
        Initialize variable manager

        Args:
            client: Grafana API client instance
        """
        self.client = client

    def create_query_variable(
        self,
        name: str,
        query: str,
        datasource_uid: str,
        label: Optional[str] = None,
        multi: bool = False,
        include_all: bool = False,
        all_value: Optional[str] = None,
        regex: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a query variable configuration

        Args:
            name: Variable name
            query: Query string
            datasource_uid: Data source UID
            label: Display label
            multi: Allow multiple values
            include_all: Include "All" option
            all_value: Value for "All" option
            regex: Regex filter

        Returns:
            Variable configuration
        """
        return {
            "name": name,
            "type": "query",
            "datasource": {"uid": datasource_uid, "type": "prometheus"},
            "query": {"query": query, "refId": "StandardVariableQuery"},
            "multi": multi,
            "includeAll": include_all,
            "allValue": all_value,
            "regex": regex,
            "label": label or name,
            "current": {
                "selected": False,
                "text": "All",
                "value": "$__all"
            },
            "options": []
        }

    def create_custom_variable(
        self,
        name: str,
        values: List[str],
        label: Optional[str] = None,
        multi: bool = False
    ) -> Dict[str, Any]:
        """
        Create a custom variable configuration

        Args:
            name: Variable name
            values: List of possible values
            label: Display label
            multi: Allow multiple values

        Returns:
            Variable configuration
        """
        options = [{"text": v, "value": v, "selected": False} for v in values]

        return {
            "name": name,
            "type": "custom",
            "multi": multi,
            "label": label or name,
            "query": values,
            "options": options,
            "current": {
                "text": values[0] if values else "",
                "value": values[0] if values else "",
                "selected": False
            }
        }

    def create_interval_variable(
        self,
        name: str = "interval",
        values: Optional[List[str]] = None,
        label: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an interval variable configuration

        Args:
            name: Variable name
            values: List of interval options
            label: Display label

        Returns:
            Variable configuration
        """
        if values is None:
            values = ["1m", "5m", "10m", "30m", "1h", "6h", "12h", "1d"]

        auto = {
            "text": "auto",
            "value": "$__auto_interval",
            "selected": False
        }

        options = [auto] + [{"text": v, "value": v, "selected": False} for v in values]

        return {
            "name": name,
            "type": "interval",
            "multi": False,
            "label": label or name,
            "query": values,
            "options": options,
            "current": {
                "text": "auto",
                "value": "$__auto_interval",
                "selected": True
            },
            "auto": True,
            "auto_count": 30,
            "auto_min": "10s"
        }

    def create_constant_variable(
        self,
        name: str,
        value: str,
        label: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a constant variable configuration

        Args:
            name: Variable name
            value: Constant value
            label: Display label

        Returns:
            Variable configuration
        """
        return {
            "name": name,
            "type": "constant",
            "query": {"type": "constant", "value": value},
            "label": label or name,
            "current": {"text": value, "value": value, "selected": False},
            "options": [{"text": value, "value": value, "selected": True}]
        }

    def add_variable_to_dashboard(
        self,
        dashboard_uid: str,
        variable_config: Dict[str, Any],
        position: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Add variable to dashboard

        Args:
            dashboard_uid: Dashboard UID
            variable_config: Variable configuration
            position: Position in list (None = append to end)

        Returns:
            Update response
        """
        dashboard = self.client.get_dashboard_by_uid(dashboard_uid)

        if "templating" not in dashboard:
            dashboard["templating"] = {}

        if "list" not in dashboard["templating"]:
            dashboard["templating"]["list"] = []

        variables = dashboard["templating"]["list"]

        # Check if variable already exists
        for var in variables:
            if var.get("name") == variable_config.get("name"):
                raise ValueError(f"Variable '{variable_config.get('name')}' already exists")

        # Add variable
        if position is not None:
            variables.insert(position, variable_config)
        else:
            variables.append(variable_config)

        return self.client.update_dashboard(
            dashboard=dashboard,
            message=f"Added variable: {variable_config.get('name')}"
        )

    def remove_variable_from_dashboard(
        self,
        dashboard_uid: str,
        variable_name: str
    ) -> Dict[str, Any]:
        """
        Remove variable from dashboard

        Args:
            dashboard_uid: Dashboard UID
            variable_name: Name of variable to remove

        Returns:
            Update response
        """
        dashboard = self.client.get_dashboard_by_uid(dashboard_uid)

        variables = dashboard.get("templating", {}).get("list", [])
        original_count = len(variables)

        variables = [v for v in variables if v.get("name") != variable_name]

        if len(variables) == original_count:
            raise ValueError(f"Variable '{variable_name}' not found")

        dashboard["templating"]["list"] = variables

        return self.client.update_dashboard(
            dashboard=dashboard,
            message=f"Removed variable: {variable_name}"
        )

    def update_variable(
        self,
        dashboard_uid: str,
        variable_name: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update existing variable

        Args:
            dashboard_uid: Dashboard UID
            variable_name: Name of variable to update
            updates: Fields to update

        Returns:
            Update response
        """
        dashboard = self.client.get_dashboard_by_uid(dashboard_uid)

        for variable in dashboard.get("templating", {}).get("list", []):
            if variable.get("name") == variable_name:
                variable.update(updates)
                return self.client.update_dashboard(
                    dashboard=dashboard,
                    message=f"Updated variable: {variable_name}"
                )

        raise ValueError(f"Variable '{variable_name}' not found")

    def list_variables(
        self,
        dashboard_uid: str
    ) -> List[Dict[str, Any]]:
        """
        List all variables in dashboard

        Args:
            dashboard_uid: Dashboard UID

        Returns:
            List of variable configurations
        """
        dashboard = self.client.get_dashboard_by_uid(dashboard_uid)
        return dashboard.get("templating", {}).get("list", [])

    def get_variable(
        self,
        dashboard_uid: str,
        variable_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get variable by name from dashboard

        Args:
            dashboard_uid: Dashboard UID
            variable_name: Name of variable

        Returns:
            Variable configuration or None
        """
        variables = self.list_variables(dashboard_uid)
        for var in variables:
            if var.get("name") == variable_name:
                return var
        return None

    def reorder_variables(
        self,
        dashboard_uid: str,
        variable_names: List[str]
    ) -> Dict[str, Any]:
        """
        Reorder variables in dashboard

        Args:
            dashboard_uid: Dashboard UID
            variable_names: List of variable names in desired order

        Returns:
            Update response
        """
        dashboard = self.client.get_dashboard_by_uid(dashboard_uid)
        all_variables = dashboard.get("templating", {}).get("list", [])

        # Create ordered list
        var_map = {v.get("name"): v for v in all_variables}
        ordered = []
        for name in variable_names:
            if name in var_map:
                ordered.append(var_map[name])
                del var_map[name]

        # Add any remaining variables
        ordered.extend(var_map.values())

        dashboard["templating"]["list"] = ordered

        return self.client.update_dashboard(
            dashboard=dashboard,
            message="Reordered variables"
        )

    def add_variable_to_multiple_dashboards(
        self,
        dashboard_uids: List[str],
        variable_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Add variable to multiple dashboards

        Args:
            dashboard_uids: List of dashboard UIDs
            variable_config: Variable configuration

        Returns:
            List of results
        """
        results = []
        for uid in dashboard_uids:
            try:
                # Check if variable already exists
                existing = self.get_variable(uid, variable_config.get("name"))
                if existing:
                    results.append({
                        "uid": uid,
                        "status": "skipped",
                        "reason": "Variable already exists"
                    })
                    continue

                result = self.add_variable_to_dashboard(uid, variable_config)
                results.append({
                    "uid": uid,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                results.append({
                    "uid": uid,
                    "status": "error",
                    "error": str(e)
                })

        return results

    def replace_variable_datasource(
        self,
        dashboard_uid: str,
        variable_name: str,
        new_datasource_uid: str,
        new_datasource_type: str = "prometheus"
    ) -> Dict[str, Any]:
        """
        Replace data source for a query variable

        Args:
            dashboard_uid: Dashboard UID
            variable_name: Name of variable
            new_datasource_uid: New data source UID
            new_datasource_type: New data source type

        Returns:
            Update response
        """
        updates = {
            "datasource": {"uid": new_datasource_uid, "type": new_datasource_type}
        }
        return self.update_variable(dashboard_uid, variable_name, updates)
