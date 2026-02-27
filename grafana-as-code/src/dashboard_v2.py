"""
Dashboard Object - New Object-Oriented API
Represents a Grafana dashboard with its components
"""

import copy
from typing import Optional, Dict, List, Any, TYPE_CHECKING
from .client import GrafanaClient

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from .folder import Folder
    from .components import DatasourceComponent, PanelComponent, VariableComponent
else:
    Folder = None
    DatasourceComponent = None
    PanelComponent = None
    VariableComponent = None


class Dashboard:
    """
    Represents a Grafana dashboard with its components

    Usage:
        # Get existing dashboard
        dashboard = Dashboard.get(client, "abc123")

        # Or create new
        dashboard = Dashboard.create(client, "My Dashboard")

        # Access components
        dashboard.datasources.add("Prometheus-Prod")
        dashboard.panels.add_timeseries(title="CPU", expr="cpu_usage", datasource_uid="...")
        dashboard.variables.add_query(name="job", query="label_values(job)", datasource_uid="...")

        # Save changes
        dashboard.save()
    """

    def __init__(
        self,
        client: GrafanaClient,
        uid: str,
        title: str,
        folder: Optional['Folder'] = None
    ):
        """
        Initialize Dashboard object

        Args:
            client: Grafana API client
            uid: Dashboard UID
            title: Dashboard title
            folder: Parent Folder object
        """
        self.client = client
        self.uid = uid
        self.title = title
        self.folder = folder
        self._data: Optional[Dict[str, Any]] = None

        # Component managers (lazy loaded)
        self._datasources = None
        self._panels = None
        self._variables = None

    @classmethod
    def get(cls, client: GrafanaClient, uid: str) -> Optional['Dashboard']:
        """
        Get dashboard by UID

        Args:
            client: Grafana API client
            uid: Dashboard UID

        Returns:
            Dashboard object or None
        """
        try:
            response = client.get_dashboard(uid)
            dashboard_data = response.get("dashboard", {})
            meta = response.get("meta", {})

            # Get folder if present (import here to avoid circular dependency)
            folder = None
            if "folderUid" in meta and meta["folderUid"]:
                from .folder import Folder
                folder = Folder.get(client, meta["folderUid"])

            dashboard = cls(
                client,
                dashboard_data.get("uid", uid),
                dashboard_data.get("title", ""),
                folder
            )
            dashboard._data = dashboard_data
            return dashboard
        except Exception:
            return None

    @classmethod
    def find(cls, client: GrafanaClient, identifier: str) -> Optional['Dashboard']:
        """
        Find dashboard by UID or title

        Args:
            client: Grafana API client
            identifier: Dashboard UID or title

        Returns:
            Dashboard object or None
        """
        # Try by UID first
        dashboard = cls.get(client, identifier)
        if dashboard:
            return dashboard

        # Try by title
        dashboards = client.list_dashboards()
        for dash_meta in dashboards:
            if dash_meta.get("title") == identifier:
                return cls.get(client, dash_meta["uid"])

        # Try partial title match
        for dash_meta in dashboards:
            if identifier.lower() in dash_meta.get("title", "").lower():
                return cls.get(client, dash_meta["uid"])

        return None

    @classmethod
    def create(
        cls,
        client: GrafanaClient,
        title: str,
        folder: Optional[Folder] = None,
        tags: Optional[List[str]] = None
    ) -> 'Dashboard':
        """
        Create a new dashboard

        Args:
            client: Grafana API client
            title: Dashboard title
            folder: Folder to create dashboard in
            tags: Optional tags

        Returns:
            Dashboard object
        """
        dashboard_data = {
            "title": title,
            "tags": tags or [],
            "panels": [],
            "templating": {"list": []}
        }

        if folder:
            dashboard_data["folderUid"] = folder.uid

        result = client.update_dashboard(
            dashboard=dashboard_data,
            message=f"Created dashboard '{title}'",
            overwrite=False
        )

        return cls(
            client,
            result["uid"],
            title,
            folder
        )

    def _load_data(self) -> Dict[str, Any]:
        """Load dashboard data from server"""
        if self._data is None:
            self._data = self.client.get_dashboard_by_uid(self.uid)
        return self._data

    def refresh(self) -> None:
        """Refresh dashboard data from server"""
        self._data = None
        self._datasources = None
        self._panels = None
        self._variables = None
        self._load_data()

    def save(self, message: Optional[str] = None) -> Dict[str, Any]:
        """
        Save dashboard changes to server

        Args:
            message: Commit message

        Returns:
            Save result
        """
        return self.client.update_dashboard(
            dashboard=self._load_data(),
            message=message or f"Updated dashboard '{self.title}'"
        )

    def delete(self) -> Dict[str, Any]:
        """Delete this dashboard"""
        return self.client.delete_dashboard(self.uid)

    def export(self, path: str) -> None:
        """Export dashboard to JSON file"""
        import json
        with open(path, 'w') as f:
            json.dump(self._load_data(), f, indent=2)

    def duplicate(
        self,
        new_title: str,
        folder: Optional[Folder] = None
    ) -> 'Dashboard':
        """
        Duplicate this dashboard

        Args:
            new_title: Title for duplicate
            folder: Target folder (default: same folder)

        Returns:
            New Dashboard object
        """
        data = copy.deepcopy(self._load_data())
        data["title"] = new_title
        data.pop("uid", None)
        data.pop("id", None)
        data.pop("version", None)
        data.pop("folderUid", None)

        if folder:
            data["folderUid"] = folder.uid
        elif self.folder:
            data["folderUid"] = self.folder.uid

        result = self.client.update_dashboard(
            dashboard=data,
            message=f"Duplicated from '{self.title}'",
            overwrite=False
        )

        return Dashboard(
            self.client,
            result["uid"],
            new_title,
            folder or self.folder
        )

    # Property-based access to components

    @property
    def datasources(self):
        """Get datasources component manager"""
        if self._datasources is None:
            # Import here to avoid circular dependency
            from .components import DatasourceComponent
            self._datasources = DatasourceComponent(self)
        return self._datasources

    @property
    def panels(self):
        """Get panels component manager"""
        if self._panels is None:
            from .components import PanelComponent
            self._panels = PanelComponent(self)
        return self._panels

    @property
    def variables(self):
        """Get variables component manager"""
        if self._variables is None:
            from .components import VariableComponent
            self._variables = VariableComponent(self)
        return self._variables

    # Direct access to dashboard properties

    @property
    def tags(self) -> List[str]:
        """Get dashboard tags"""
        return self._load_data().get("tags", [])

    def add_tag(self, tag: str) -> None:
        """Add a tag to dashboard"""
        data = self._load_data()
        if "tags" not in data:
            data["tags"] = []
        if tag not in data["tags"]:
            data["tags"].append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from dashboard"""
        data = self._load_data()
        if "tags" in data and tag in data["tags"]:
            data["tags"].remove(tag)

    @property
    def description(self) -> str:
        """Get dashboard description"""
        return self._load_data().get("description", "")

    @description.setter
    def description(self, value: str) -> None:
        """Set dashboard description"""
        self._load_data()["description"] = value

    @property
    def editable(self) -> bool:
        """Get editable flag"""
        return self._load_data().get("editable", True)

    @editable.setter
    def editable(self, value: bool) -> None:
        """Set editable flag"""
        self._load_data()["editable"] = value

    def __repr__(self) -> str:
        folder_info = f", folder='{self.folder.title}'" if self.folder else ""
        return f"Dashboard(uid='{self.uid}', title='{self.title}'{folder_info})"
