"""
Datasource Component
Manages data source references within a dashboard
"""

from typing import Optional, Dict, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..dashboard_v2 import Dashboard


class DatasourceComponent:
    """
    Component for managing data sources in a dashboard

    Usage:
        dashboard = Dashboard.get(client, "abc123")
        dashboard.datasources.add("Prometheus-Prod")
        dashboard.datasources.replace("Prometheus-Old", "Prometheus-New")
        dashboard.datasources.remove("Prometheus-Old")
        dashboard.save()
    """

    def __init__(self, dashboard: 'Dashboard'):
        """
        Initialize datasource component

        Args:
            dashboard: Parent Dashboard object
        """
        self.dashboard = dashboard

    def add(
        self,
        datasource_name: str,
        apply_to_panels: bool = True,
        apply_to_variables: bool = True
    ) -> None:
        """
        Add or update data source in dashboard

        Args:
            datasource_name: Name of data source to add
            apply_to_panels: Apply to all panels
            apply_to_variables: Apply to query variables
        """
        client = self.dashboard.client
        datasource = client.get_datasource_by_name(datasource_name)

        if not datasource:
            raise ValueError(f"Data source '{datasource_name}' not found")

        datasource_uid = datasource.get("uid")
        datasource_type = datasource.get("type")
        data = self.dashboard._load_data()

        if apply_to_panels:
            for panel in data.get("panels", []):
                if "targets" in panel:
                    for target in panel["targets"]:
                        target["datasource"] = {
                            "uid": datasource_uid,
                            "type": datasource_type
                        }

        if apply_to_variables:
            for variable in data.get("templating", {}).get("list", []):
                if variable.get("type") == "query":
                    variable["datasource"] = {
                        "uid": datasource_uid,
                        "type": datasource_type
                    }

    def remove(self, datasource_name: str) -> None:
        """
        Remove data source references from dashboard

        Args:
            datasource_name: Name of data source to remove
        """
        client = self.dashboard.client
        datasource = client.get_datasource_by_name(datasource_name)

        if not datasource:
            raise ValueError(f"Data source '{datasource_name}' not found")

        datasource_uid = datasource.get("uid")
        data = self.dashboard._load_data()

        # Remove from panels
        for panel in data.get("panels", []):
            if "targets" in panel:
                targets = [
                    t for t in panel["targets"]
                    if t.get("datasource", {}).get("uid") != datasource_uid
                ]
                panel["targets"] = targets

        # Remove from variables
        for variable in data.get("templating", {}).get("list", []):
            if variable.get("type") == "query":
                if variable.get("datasource", {}).get("uid") == datasource_uid:
                    # Remove variable that depends on this datasource
                    variables = data["templating"]["list"]
                    variables.remove(variable)

    def replace(
        self,
        old_datasource_name: str,
        new_datasource_name: str
    ) -> None:
        """
        Replace old data source with new one in dashboard

        Args:
            old_datasource_name: Name of data source to replace
            new_datasource_name: Name of replacement data source
        """
        client = self.dashboard.client
        new_datasource = client.get_datasource_by_name(new_datasource_name)

        if not new_datasource:
            raise ValueError(f"New data source '{new_datasource_name}' not found")

        old_datasource = client.get_datasource_by_name(old_datasource_name)
        if not old_datasource:
            raise ValueError(f"Old data source '{old_datasource_name}' not found")

        old_uid = old_datasource.get("uid")
        new_uid = new_datasource.get("uid")
        new_type = new_datasource.get("type")

        data = self.dashboard._load_data()

        # Replace in panels
        for panel in data.get("panels", []):
            if "targets" in panel:
                for target in panel["targets"]:
                    if target.get("datasource", {}).get("uid") == old_uid:
                        target["datasource"] = {"uid": new_uid, "type": new_type}

        # Replace in variables
        for variable in data.get("templating", {}).get("list", []):
            if variable.get("type") == "query":
                if variable.get("datasource", {}).get("uid") == old_uid:
                    variable["datasource"] = {"uid": new_uid, "type": new_type}

    def list_used(self) -> List[Dict[str, Any]]:
        """
        List all data sources used in this dashboard

        Returns:
            List of unique data sources being used
        """
        data = self.dashboard._load_data()
        used_datasources = {}

        # Collect from panels
        for panel in data.get("panels", []):
            for target in panel.get("targets", []):
                ds = target.get("datasource", {})
                if isinstance(ds, dict) and "uid" in ds:
                    used_datasources[ds["uid"]] = {
                        "uid": ds["uid"],
                        "type": ds.get("type", "unknown")
                    }

        # Collect from variables
        for variable in data.get("templating", {}).get("list", []):
            ds = variable.get("datasource", {})
            if isinstance(ds, dict) and "uid" in ds:
                used_datasources[ds["uid"]] = {
                    "uid": ds["uid"],
                    "type": ds.get("type", "unknown")
                }

        return list(used_datasources.values())

    def edit(
        self,
        datasource_name: str,
        **updates
    ) -> None:
        """
        Edit data source configuration in dashboard targets

        Args:
            datasource_name: Name of data source
            **updates: Fields to update (e.g., query modifications)
        """
        client = self.dashboard.client
        datasource = client.get_datasource_by_name(datasource_name)

        if not datasource:
            raise ValueError(f"Data source '{datasource_name}' not found")

        datasource_uid = datasource.get("uid")
        data = self.dashboard._load_data()

        for panel in data.get("panels", []):
            for target in panel.get("targets", []):
                if target.get("datasource", {}).get("uid") == datasource_uid:
                    # Apply updates to target
                    for key, value in updates.items():
                        target[key] = value
