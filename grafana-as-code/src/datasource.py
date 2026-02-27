"""
Data Source Management Module
Operations for managing Grafana data sources
"""

from typing import Dict, List, Any, Optional
from .client import GrafanaClient


class DatasourceManager:
    """Manager for data source operations"""

    def __init__(self, client: GrafanaClient):
        """
        Initialize data source manager

        Args:
            client: Grafana API client instance
        """
        self.client = client

    def list_datasources(self) -> List[Dict[str, Any]]:
        """List all data sources"""
        return self.client.list_datasources()

    def get_datasource(self, datasource_id: int) -> Dict[str, Any]:
        """Get data source by ID"""
        return self.client.get_datasource(datasource_id)

    def get_datasource_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get data source by name"""
        return self.client.get_datasource_by_name(name)

    def create_datasource(
        self,
        name: str,
        type: str,
        url: str,
        access: str = "proxy",
        is_default: bool = False,
        json_data: Optional[Dict] = None,
        secure_json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create new data source

        Args:
            name: Data source name
            type: Data source type (prometheus, influxdb, etc.)
            url: Data source URL
            access: Access mode (proxy, direct)
            is_default: Set as default data source
            json_data: Additional JSON data
            secure_json_data: Secure data (passwords, tokens)

        Returns:
            Created data source
        """
        datasource = {
            "name": name,
            "type": type,
            "access": access,
            "url": url,
            "isDefault": is_default
        }

        if json_data:
            datasource["jsonData"] = json_data

        if secure_json_data:
            datasource["secureJsonData"] = secure_json_data

        return self.client.create_datasource(datasource)

    def update_datasource(
        self,
        datasource_id: int,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update existing data source

        Args:
            datasource_id: Data source ID
            **kwargs: Fields to update

        Returns:
            Updated data source
        """
        existing = self.get_datasource(datasource_id)
        updated = {**existing, **kwargs}
        return self.client.update_datasource(datasource_id, updated)

    def delete_datasource(self, datasource_id: int) -> Dict[str, Any]:
        """Delete data source by ID"""
        return self.client.delete_datasource(datasource_id)

    def find_datasource_usage(
        self,
        datasource_name: str
    ) -> List[Dict[str, Any]]:
        """
        Find all dashboards using a specific data source

        Args:
            datasource_name: Name of data source

        Returns:
            List of dashboards using the data source
        """
        dashboards = self.client.list_dashboards()
        usage = []

        for dashboard_meta in dashboards:
            try:
                dashboard = self.client.get_dashboard_by_uid(dashboard_meta["uid"])

                # Check panels
                for panel in dashboard.get("panels", []):
                    if self._panel_uses_datasource(panel, datasource_name):
                        usage.append({
                            "dashboard": dashboard_meta,
                            "type": "panel",
                            "panel_id": panel.get("id")
                        })
                        break

                # Check variables
                for variable in dashboard.get("templating", {}).get("list", []):
                    if self._variable_uses_datasource(variable, datasource_name):
                        usage.append({
                            "dashboard": dashboard_meta,
                            "type": "variable",
                            "variable_name": variable.get("name")
                        })
                        break

            except Exception:
                continue

        return usage

    def _panel_uses_datasource(
        self,
        panel: Dict[str, Any],
        datasource_name: str
    ) -> bool:
        """Check if panel uses data source"""
        for target in panel.get("targets", []):
            datasource = target.get("datasource", {})
            if isinstance(datasource, dict):
                if datasource.get("name") == datasource_name:
                    return True
                if datasource.get("uid") == datasource_name:
                    return True
        return False

    def _variable_uses_datasource(
        self,
        variable: Dict[str, Any],
        datasource_name: str
    ) -> bool:
        """Check if variable uses data source"""
        datasource = variable.get("datasource", {})
        if isinstance(datasource, dict):
            if datasource.get("name") == datasource_name:
                return True
            if datasource.get("uid") == datasource_name:
                return True
        return False

    def replace_datasource_in_dashboards(
        self,
        old_datasource_name: str,
        new_datasource_name: str,
        dashboard_uids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Replace data source in multiple dashboards

        Args:
            old_datasource_name: Name of data source to replace
            new_datasource_name: Name of replacement data source
            dashboard_uids: List of dashboard UIDs (None = all dashboards)

        Returns:
            List of update results
        """
        # Get new datasource info
        new_datasource = self.get_datasource_by_name(new_datasource_name)
        if not new_datasource:
            raise ValueError(f"New data source '{new_datasource_name}' not found")

        # Get dashboards to update
        if dashboard_uids is None:
            dashboards = self.client.list_dashboards()
            dashboard_uids = [d["uid"] for d in dashboards]

        results = []
        for uid in dashboard_uids:
            try:
                dashboard = self.client.get_dashboard_by_uid(uid)
                updated = False

                # Update panels
                for panel in dashboard.get("panels", []):
                    for target in panel.get("targets", []):
                        datasource = target.get("datasource", {})
                        if isinstance(datasource, dict):
                            if datasource.get("name") == old_datasource_name:
                                target["datasource"] = {
                                    "uid": new_datasource["uid"],
                                    "type": new_datasource["type"]
                                }
                                updated = True

                # Update variables
                for variable in dashboard.get("templating", {}).get("list", []):
                    datasource = variable.get("datasource", {})
                    if isinstance(datasource, dict):
                        if datasource.get("name") == old_datasource_name:
                            variable["datasource"] = {
                                "uid": new_datasource["uid"],
                                "type": new_datasource["type"]
                            }
                            updated = True

                if updated:
                    result = self.client.update_dashboard(
                        dashboard=dashboard,
                        message=f"Replaced {old_datasource_name} with {new_datasource_name}"
                    )
                    results.append({"uid": uid, "status": "success", "result": result})
                else:
                    results.append({"uid": uid, "status": "no changes"})

            except Exception as e:
                results.append({"uid": uid, "status": "error", "error": str(e)})

        return results

    def remove_datasource_from_dashboards(
        self,
        datasource_name: str,
        dashboard_uids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Remove data source references from dashboards
        (Note: This removes references, not the data source itself)

        Args:
            datasource_name: Name of data source to remove
            dashboard_uids: List of dashboard UIDs (None = all dashboards)

        Returns:
            List of update results
        """
        if dashboard_uids is None:
            dashboards = self.client.list_dashboards()
            dashboard_uids = [d["uid"] for d in dashboards]

        results = []
        for uid in dashboard_uids:
            try:
                dashboard = self.client.get_dashboard_by_uid(uid)
                updated = False

                # Remove from panels (remove targets using this datasource)
                panels_to_update = []
                for panel in dashboard.get("panels", []):
                    targets = []
                    for target in panel.get("targets", []):
                        datasource = target.get("datasource", {})
                        if isinstance(datasource, dict):
                            if datasource.get("name") != datasource_name:
                                targets.append(target)
                            else:
                                updated = True
                        else:
                            targets.append(target)

                    if targets:
                        panel["targets"] = targets
                        panels_to_update.append(panel)

                if updated:
                    dashboard["panels"] = panels_to_update
                    result = self.client.update_dashboard(
                        dashboard=dashboard,
                        message=f"Removed data source {datasource_name}"
                    )
                    results.append({"uid": uid, "status": "success", "result": result})
                else:
                    results.append({"uid": uid, "status": "no changes"})

            except Exception as e:
                results.append({"uid": uid, "status": "error", "error": str(e)})

        return results
