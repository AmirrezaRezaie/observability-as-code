"""
Variable Component
Manages template variables within a dashboard
"""

from typing import Optional, Dict, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..dashboard_v2 import Dashboard


class VariableComponent:
    """
    Component for managing template variables in a dashboard

    Usage:
        dashboard = Dashboard.get(client, "abc123")
        dashboard.variables.add_query(name="job", query="label_values(job)")
        dashboard.variables.add_custom(name="env", values=["dev", "prod"])
        dashboard.variables.remove("job")
        dashboard.variables.edit("env", multi=True)
        dashboard.save()
    """

    def __init__(self, dashboard: 'Dashboard'):
        """
        Initialize variable component

        Args:
            dashboard: Parent Dashboard object
        """
        self.dashboard = dashboard

    # ADD operations

    def add_query(
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
        Add a query variable to dashboard

        Args:
            name: Variable name
            query: Query string (supports format: "label_values(metric,label)" or "label_values(label)")
            datasource_uid: Data source UID
            label: Display label
            multi: Allow multiple values
            include_all: Include "All" option
            all_value: Value for "All" option
            regex: Regex filter

        Returns:
            Created variable configuration
        """
        # Check if variable already exists
        if self.get(name):
            raise ValueError(f"Variable '{name}' already exists")

        # Parse label_values query to create structured format
        # Format: label_values(metric,label) or label_values(label)
        query_obj = {"refId": "StandardVariableQuery"}

        if query.startswith("label_values("):
            # Parse label_values query
            content = query[len("label_values("):-1]  # Remove "label_values(" and trailing ")"
            parts = [p.strip() for p in content.split(",")]

            if len(parts) == 2:
                # label_values(metric, label)
                query_obj["type"] = "labelValues"
                query_obj["metric"] = parts[0]
                query_obj["label"] = parts[1]
            elif len(parts) == 1:
                # label_values(label)
                query_obj["type"] = "labelValues"
                query_obj["label"] = parts[0]
            else:
                # Fallback to raw query
                query_obj["query"] = query
        else:
            # Use as raw query for other types
            query_obj["query"] = query

        variable = {
            "name": name,
            "type": "query",
            "datasource": {"uid": datasource_uid, "type": "prometheus"},
            "query": query_obj,
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

        data = self.dashboard._load_data()
        data.setdefault("templating", {}).setdefault("list", []).append(variable)
        return variable

    def add_custom(
        self,
        name: str,
        values: List[str],
        label: Optional[str] = None,
        multi: bool = False
    ) -> Dict[str, Any]:
        """
        Add a custom variable to dashboard

        Args:
            name: Variable name
            values: List of possible values
            label: Display label
            multi: Allow multiple values

        Returns:
            Created variable configuration
        """
        if self.get(name):
            raise ValueError(f"Variable '{name}' already exists")

        options = [{"text": v, "value": v, "selected": False} for v in values]

        variable = {
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

        data = self.dashboard._load_data()
        data.setdefault("templating", {}).setdefault("list", []).append(variable)
        return variable

    def add_interval(
        self,
        name: str = "interval",
        values: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add an interval variable to dashboard

        Args:
            name: Variable name
            values: List of interval options

        Returns:
            Created variable configuration
        """
        if self.get(name):
            raise ValueError(f"Variable '{name}' already exists")

        if values is None:
            values = ["1m", "5m", "10m", "30m", "1h", "6h", "12h", "1d"]

        auto = {"text": "auto", "value": "$__auto_interval", "selected": False}
        options = [auto] + [{"text": v, "value": v, "selected": False} for v in values]

        variable = {
            "name": name,
            "type": "interval",
            "multi": False,
            "label": name,
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

        data = self.dashboard._load_data()
        data.setdefault("templating", {}).setdefault("list", []).append(variable)
        return variable

    def add_constant(
        self,
        name: str,
        value: str,
        label: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a constant variable to dashboard

        Args:
            name: Variable name
            value: Constant value
            label: Display label

        Returns:
            Created variable configuration
        """
        if self.get(name):
            raise ValueError(f"Variable '{name}' already exists")

        variable = {
            "name": name,
            "type": "constant",
            "query": {"type": "constant", "value": value},
            "label": label or name,
            "current": {"text": value, "value": value, "selected": False},
            "options": [{"text": value, "value": value, "selected": True}]
        }

        data = self.dashboard._load_data()
        data.setdefault("templating", {}).setdefault("list", []).append(variable)
        return variable

    def add_raw(self, variable_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a custom variable configuration

        Args:
            variable_config: Complete variable configuration

        Returns:
            Added variable configuration
        """
        name = variable_config.get("name")
        if self.get(name):
            raise ValueError(f"Variable '{name}' already exists")

        data = self.dashboard._load_data()
        data.setdefault("templating", {}).setdefault("list", []).append(variable_config)
        return variable_config

    # REMOVE operations

    def remove(self, variable_name: str) -> None:
        """
        Remove variable from dashboard

        Args:
            variable_name: Name of variable to remove
        """
        data = self.dashboard._load_data()
        variables = data.get("templating", {}).get("list", [])

        original_count = len(variables)
        data["templating"]["list"] = [v for v in variables if v.get("name") != variable_name]

        if len(data["templating"]["list"]) == original_count:
            raise ValueError(f"Variable '{variable_name}' not found")

    def clear(self) -> None:
        """Remove all variables from dashboard"""
        data = self.dashboard._load_data()
        if "templating" in data:
            data["templating"]["list"] = []

    # EDIT operations

    def edit(self, variable_name: str, **updates) -> None:
        """
        Edit variable properties

        Args:
            variable_name: Name of variable to edit
            **updates: Fields to update (query, multi, label, etc.)
        """
        data = self.dashboard._load_data()

        for variable in data.get("templating", {}).get("list", []):
            if variable.get("name") == variable_name:
                variable.update(updates)
                return

        raise ValueError(f"Variable '{variable_name}' not found")

    def edit_datasource(
        self,
        variable_name: str,
        new_datasource_uid: str,
        new_datasource_type: str = "prometheus"
    ) -> None:
        """
        Edit data source for a query variable

        Args:
            variable_name: Name of variable
            new_datasource_uid: New data source UID
            new_datasource_type: New data source type
        """
        self.edit(variable_name, datasource={"uid": new_datasource_uid, "type": new_datasource_type})

    def edit_query(self, variable_name: str, new_query: str) -> None:
        """
        Edit query for a query variable

        Args:
            variable_name: Name of variable
            new_query: New query string
        """
        data = self.dashboard._load_data()

        for variable in data.get("templating", {}).get("list", []):
            if variable.get("name") == variable_name:
                if variable.get("type") != "query":
                    raise ValueError(f"Variable '{variable_name}' is not a query variable")
                variable["query"]["query"] = new_query
                return

        raise ValueError(f"Variable '{variable_name}' not found")

    # LIST operations

    def list_all(self) -> List[Dict[str, Any]]:
        """List all variables in dashboard"""
        return self.dashboard._load_data().get("templating", {}).get("list", [])

    def get(self, variable_name: str) -> Optional[Dict[str, Any]]:
        """Get specific variable by name"""
        for variable in self.list_all():
            if variable.get("name") == variable_name:
                return variable
        return None

    def get_query_variables(self) -> List[Dict[str, Any]]:
        """List only query variables"""
        return [v for v in self.list_all() if v.get("type") == "query"]

    def get_custom_variables(self) -> List[Dict[str, Any]]:
        """List only custom variables"""
        return [v for v in self.list_all() if v.get("type") == "custom"]

    # Other operations

    def reorder(self, variable_names: List[str]) -> None:
        """
        Reorder variables in dashboard

        Args:
            variable_names: List of variable names in desired order
        """
        data = self.dashboard._load_data()
        all_variables = data.get("templating", {}).get("list", [])

        var_map = {v.get("name"): v for v in all_variables}
        ordered = []

        for name in variable_names:
            if name in var_map:
                ordered.append(var_map[name])
                del var_map[name]

        # Add remaining variables
        ordered.extend(var_map.values())
        data["templating"]["list"] = ordered

    def duplicate(self, variable_name: str, new_name: str) -> Dict[str, Any]:
        """
        Duplicate a variable

        Args:
            variable_name: Name of variable to duplicate
            new_name: Name for duplicate

        Returns:
            New variable configuration
        """
        import copy

        source = self.get(variable_name)
        if not source:
            raise ValueError(f"Variable '{variable_name}' not found")

        if self.get(new_name):
            raise ValueError(f"Variable '{new_name}' already exists")

        new_variable = copy.deepcopy(source)
        new_variable["name"] = new_name

        data = self.dashboard._load_data()
        data.setdefault("templating", {}).setdefault("list", []).append(new_variable)
        return new_variable
