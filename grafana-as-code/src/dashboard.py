"""
Dashboard Management Module
Operations for managing Grafana dashboards

This module provides both the legacy DashboardManager class and the new Dashboard class.
"""

from typing import Dict, List, Any, Optional
from .client import GrafanaClient

# Import the new OO Dashboard class from dashboard_v2
from .dashboard_v2 import Dashboard as _DashboardV2

# Export Dashboard as the new OO API
Dashboard = _DashboardV2


# Legacy API (still available for backward compatibility)
class DashboardManager:
    """Manager for dashboard operations"""

    def __init__(self, client: GrafanaClient):
        """
        Initialize dashboard manager

        Args:
            client: Grafana API client instance
        """
        self.client = client

    def get_dashboard(self, uid: str) -> Dict[str, Any]:
        """
        Get dashboard JSON by UID

        Args:
            uid: Dashboard UID

        Returns:
            Dashboard JSON
        """
        return self.client.get_dashboard_by_uid(uid)

    def update_dashboard(
        self,
        uid: str,
        dashboard: Dict[str, Any],
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update existing dashboard

        Args:
            uid: Dashboard UID
            dashboard: Updated dashboard JSON
            message: Commit message

        Returns:
            Update response
        """
        return self.client.update_dashboard(
            dashboard=dashboard,
            message=message or f"Updated dashboard {uid}"
        )

    def create_dashboard(
        self,
        dashboard: Dict[str, Any],
        folder_uid: Optional[str] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create new dashboard

        Args:
            dashboard: Dashboard JSON
            folder_uid: Folder UID to place dashboard in
            message: Commit message

        Returns:
            Create response
        """
        if folder_uid:
            dashboard["folderUid"] = folder_uid

        return self.client.update_dashboard(
            dashboard=dashboard,
            message=message or "Created new dashboard",
            overwrite=False
        )

    def delete_dashboard(self, uid: str) -> Dict[str, Any]:
        """
        Delete dashboard by UID

        Args:
            uid: Dashboard UID

        Returns:
            Delete response
        """
        return self.client.delete_dashboard(uid)

    def list_dashboards(
        self,
        folder_uid: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List dashboards with optional filters

        Args:
            folder_uid: Filter by folder UID
            tag: Filter by tag

        Returns:
            List of dashboard metadata
        """
        dashboards = self.client.list_dashboards(folder_uid=folder_uid)
        if tag:
            dashboards = [
                d for d in dashboards
                if tag in d.get("tags", [])
            ]
        return dashboards

    def find_dashboards_by_title(self, title: str) -> List[Dict[str, Any]]:
        """
        Find dashboards by title (partial match)

        Args:
            title: Title to search for

        Returns:
            List of matching dashboards
        """
        dashboards = self.client.list_dashboards()
        return [
            d for d in dashboards
            if title.lower() in d.get("title", "").lower()
        ]

    def add_datasource_to_panels(
        self,
        uid: str,
        datasource_name: str,
        panel_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Add or update data source for panels in dashboard

        Args:
            uid: Dashboard UID
            datasource_name: Name of data source to apply
            panel_ids: List of panel IDs to update (None = all panels)

        Returns:
            Update response
        """
        dashboard = self.get_dashboard(uid)
        datasource = self.client.get_datasource_by_name(datasource_name)

        if not datasource:
            raise ValueError(f"Data source '{datasource_name}' not found")

        datasource_uid = datasource.get("uid")
        updated = False

        # Update panels
        for panel in dashboard.get("panels", []):
            if panel_ids is None or panel.get("id") in panel_ids:
                if "targets" in panel:
                    for target in panel["targets"]:
                        target["datasource"] = {"uid": datasource_uid, "type": datasource.get("type")}
                    updated = True

        if updated:
            return self.update_dashboard(
                uid,
                dashboard,
                message=f"Updated data source to {datasource_name}"
            )

        return {"status": "no changes needed"}

    def add_datasource_to_variables(
        self,
        uid: str,
        datasource_name: str,
        variable_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add or update data source for query variables

        Args:
            uid: Dashboard UID
            datasource_name: Name of data source to apply
            variable_names: List of variable names to update (None = all query variables)

        Returns:
            Update response
        """
        dashboard = self.get_dashboard(uid)
        datasource = self.client.get_datasource_by_name(datasource_name)

        if not datasource:
            raise ValueError(f"Data source '{datasource_name}' not found")

        datasource_uid = datasource.get("uid")
        updated = False

        # Update template variables
        for variable in dashboard.get("templating", {}).get("list", []):
            if variable.get("type") == "query":
                if variable_names is None or variable.get("name") in variable_names:
                    variable["datasource"] = {"uid": datasource_uid, "type": datasource.get("type")}
                    updated = True

        if updated:
            return self.update_dashboard(
                uid,
                dashboard,
                message=f"Updated variable data source to {datasource_name}"
            )

        return {"status": "no changes needed"}

    def batch_update_dashboards(
        self,
        dashboard_uids: List[str],
        update_func: callable,
        message: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Apply update function to multiple dashboards

        Args:
            dashboard_uids: List of dashboard UIDs to update
            update_func: Function that takes dashboard JSON and returns modified JSON
            message: Commit message

        Returns:
            List of update responses
        """
        results = []
        for uid in dashboard_uids:
            try:
                dashboard = self.get_dashboard(uid)
                updated_dashboard = update_func(dashboard)
                result = self.update_dashboard(
                    uid,
                    updated_dashboard,
                    message=message or f"Batch update dashboard {uid}"
                )
                results.append({
                    "uid": uid,
                    "status": "success",
                    "response": result
                })
            except Exception as e:
                results.append({
                    "uid": uid,
                    "status": "error",
                    "error": str(e)
                })
        return results

    def clone_dashboard(
        self,
        uid: str,
        new_title: str,
        folder_uid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Clone existing dashboard

        Args:
            uid: Source dashboard UID
            new_title: Title for new dashboard
            folder_uid: Target folder UID

        Returns:
            Create response
        """
        dashboard = self.get_dashboard(uid)
        dashboard["title"] = new_title
        dashboard.pop("uid", None)
        dashboard.pop("id", None)
        dashboard.pop("version", None)

        return self.create_dashboard(dashboard, folder_uid=folder_uid)

    def export_dashboard(self, uid: str, path: str) -> None:
        """
        Export dashboard to JSON file

        Args:
            uid: Dashboard UID
            path: File path to save dashboard JSON
        """
        import json

        dashboard = self.get_dashboard(uid)
        with open(path, 'w') as f:
            json.dump(dashboard, f, indent=2)

    def import_dashboard(
        self,
        path: str,
        folder_uid: Optional[str] = None,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Import dashboard from JSON file

        Args:
            path: Path to dashboard JSON file
            folder_uid: Folder UID to place dashboard in
            overwrite: Overwrite if exists

        Returns:
            Create/update response
        """
        import json

        with open(path, 'r') as f:
            dashboard = json.load(f)

        return self.client.update_dashboard(
            dashboard=dashboard,
            folder_uid=folder_uid,
            message=f"Imported dashboard from {path}",
            overwrite=overwrite
        )
