"""
Folder Object
Represents a Grafana folder with its dashboards and management operations
"""

from typing import Optional, Dict, List, Any, TYPE_CHECKING
from .client import GrafanaClient

if TYPE_CHECKING:
    from .dashboard_v2 import Dashboard


class Folder:
    """Represents a Grafana folder containing dashboards"""

    def __init__(self, client: GrafanaClient, uid: str, title: str):
        """
        Initialize Folder object

        Args:
            client: Grafana API client
            uid: Folder UID
            title: Folder title
        """
        self.client = client
        self.uid = uid
        self.title = title

    @classmethod
    def create(cls, client: GrafanaClient, title: str, uid: Optional[str] = None) -> 'Folder':
        """
        Create a new folder

        Args:
            client: Grafana API client
            title: Folder title
            uid: Optional folder UID

        Returns:
            Folder object
        """
        data = {"title": title}
        if uid:
            data["uid"] = uid

        result = client.post("/folders", data)
        return cls(client, result["uid"], result["title"])

    @classmethod
    def get(cls, client: GrafanaClient, uid: str) -> Optional['Folder']:
        """
        Get folder by UID

        Args:
            client: Grafana API client
            uid: Folder UID

        Returns:
            Folder object or None
        """
        folders = client.list_folders()
        for folder in folders:
            if folder.get("uid") == uid:
                return cls(client, folder["uid"], folder["title"])
        return None

    @classmethod
    def find(cls, client: GrafanaClient, identifier: str) -> Optional['Folder']:
        """
        Find folder by UID or title (tries UID first, then title)

        Args:
            client: Grafana API client
            identifier: Folder UID or title

        Returns:
            Folder object or None
        """
        # Try by UID first
        folder = cls.get(client, identifier)
        if folder:
            return folder

        # Try by title
        folders = client.list_folders()
        for folder in folders:
            if folder.get("title") == identifier:
                return cls(client, folder["uid"], folder["title"])

        # Try partial title match
        for folder in folders:
            if identifier.lower() in folder.get("title", "").lower():
                return cls(client, folder["uid"], folder["title"])

        return None

    @classmethod
    def list_all(cls, client: GrafanaClient) -> List['Folder']:
        """
        List all folders

        Args:
            client: Grafana API client

        Returns:
            List of Folder objects
        """
        folders = client.list_folders()
        return [cls(client, f["uid"], f["title"]) for f in folders]

    @classmethod
    def build_tree(cls, client: GrafanaClient) -> 'FolderNode':
        """
        Build a tree structure from all folders using parentUid field or path separators.

        Grafana supports nested folders using parentUid field.
        Falls back to path separator "/" for older versions.

        Args:
            client: Grafana API client

        Returns:
            Root FolderNode containing the folder hierarchy
        """
        folders = client.list_folders()
        root = FolderNode("", None, client)

        # Check if any folder has parentUid (Grafana nested folders)
        has_parent_uid = any(f.get("parentUid") for f in folders)

        if has_parent_uid:
            # Build tree using parentUid
            folder_map = {}  # uid -> FolderNode

            # Create nodes for all folders
            for folder in folders:
                node = FolderNode(folder["title"], folder.get("uid"), client, is_real_folder=True)
                node.parent_uid = folder.get("parentUid")
                folder_map[folder["uid"]] = node

            # Build hierarchy
            for uid, node in folder_map.items():
                if node.parent_uid:
                    # Add to parent's children
                    if node.parent_uid in folder_map:
                        parent = folder_map[node.parent_uid]
                        parent.children[node.title] = node
                    else:
                        # Parent not found, add to root
                        root.children[node.title] = node
                else:
                    # Top-level folder
                    root.children[node.title] = node

        else:
            # Fallback: Build tree using "/" in folder titles
            for folder in folders:
                parts = folder["title"].split("/")
                current = root

                for part in parts:
                    if part not in current.children:
                        if part == folder["title"]:  # This is the actual folder
                            child = FolderNode(part, folder.get("uid"), client, is_real_folder=True)
                        else:  # This is a virtual path component
                            child = FolderNode(part, None, client, is_real_folder=False)
                        current.children[part] = child
                    current = current.children[part]

        return root

    def sub_folders(self, recursive: bool = False) -> List['Folder']:
        """
        Get sub-folders. Uses Grafana's parentUid for nested folders.
        Falls back to path separator "/" for older versions.

        Args:
            recursive: If True, get all nested sub-folders recursively

        Returns:
            List of Folder objects
        """
        all_folders = self.client.list_folders()

        # Check if folders have parentUid
        has_parent_uid = any(f.get("parentUid") for f in all_folders)

        if has_parent_uid:
            # Use parentUid to find sub-folders
            sub_folders = []

            if recursive:
                # Get all descendants
                to_visit = [self.uid]
                visited = set()

                while to_visit:
                    current_uid = to_visit.pop(0)
                    if current_uid in visited:
                        continue
                    visited.add(current_uid)

                    for folder_data in all_folders:
                        parent_uid = folder_data.get("parentUid")
                        if parent_uid == current_uid and folder_data.get("uid") != self.uid:
                            sub_folders.append(Folder(self.client, folder_data["uid"], folder_data["title"]))
                            if folder_data["uid"] not in visited:
                                to_visit.append(folder_data["uid"])
            else:
                # Only direct children
                for folder_data in all_folders:
                    if folder_data.get("parentUid") == self.uid:
                        sub_folders.append(Folder(self.client, folder_data["uid"], folder_data["title"]))

            return sub_folders
        else:
            # Fallback: Use "/" in folder titles
            prefix = f"{self.title}/"
            sub_folders = []
            for folder in all_folders:
                if folder["title"].startswith(prefix):
                    if recursive:
                        sub_folders.append(Folder(self.client, folder["uid"], folder["title"]))
                    else:
                        # Only direct children (one level deep)
                        relative_path = folder["title"][len(prefix):]
                        if "/" not in relative_path:
                            sub_folders.append(Folder(self.client, folder["uid"], folder["title"]))

            return sub_folders

    def all_dashboards_recursive(self) -> List['Dashboard']:
        """
        Get all dashboards in this folder and all sub-folders recursively.

        Returns:
            List of Dashboard objects
        """
        from .dashboard_v2 import Dashboard

        all_dashboards = []

        # Dashboards in this folder
        all_dashboards.extend(self.dashboards())

        # Dashboards in sub-folders
        for sub_folder in self.sub_folders(recursive=True):
            all_dashboards.extend(sub_folder.dashboards())

        return all_dashboards

    def apply_to_tree(self, func: callable, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Apply a function to all dashboards in this folder and sub-folders.

        Args:
            func: Function that takes a Dashboard object and returns result
            recursive: If True, include sub-folders recursively

        Returns:
            List of results with folder path information
        """
        results = []

        # Apply to dashboards in this folder
        for dashboard in self.dashboards():
            try:
                result = func(dashboard)
                results.append({
                    "folder": self.title,
                    "folder_uid": self.uid,
                    "dashboard": dashboard.uid,
                    "dashboard_title": dashboard.title,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                results.append({
                    "folder": self.title,
                    "folder_uid": self.uid,
                    "dashboard": dashboard.uid,
                    "dashboard_title": dashboard.title,
                    "status": "error",
                    "error": str(e)
                })

        # Recursively apply to sub-folders
        if recursive:
            for sub_folder in self.sub_folders(recursive=True):
                for dashboard in sub_folder.dashboards():
                    try:
                        result = func(dashboard)
                        results.append({
                            "folder": sub_folder.title,
                            "folder_uid": sub_folder.uid,
                            "dashboard": dashboard.uid,
                            "dashboard_title": dashboard.title,
                            "status": "success",
                            "result": result
                        })
                    except Exception as e:
                        results.append({
                            "folder": sub_folder.title,
                            "folder_uid": sub_folder.uid,
                            "dashboard": dashboard.uid,
                            "dashboard_title": dashboard.title,
                            "status": "error",
                            "error": str(e)
                        })

        return results

    def print_tree(self, indent: int = 0) -> None:
        """
        Print the folder tree structure.

        Args:
            indent: Indentation level
        """
        print("  " * indent + f"📁 {self.title} ({self.uid})")

        # Print dashboards in this folder
        for dash in self.dashboards():
            print("  " * (indent + 1) + f"📊 {dash.title} ({dash.uid})")

        # Recursively print sub-folders (direct children only)
        for sub_folder in self.sub_folders(recursive=False):
            sub_folder.print_tree(indent + 1)

    def delete(self) -> Dict[str, Any]:
        """Delete this folder"""
        return self.client.delete(f"/folders/{self.uid}")

    def refresh(self) -> None:
        """Refresh folder data from server"""
        folders = self.client.list_folders()
        for folder in folders:
            if folder.get("uid") == self.uid:
                self.title = folder["title"]
                break

    # Dashboard operations within folder

    def dashboards(self):
        """
        List all dashboards in this folder

        Returns:
            List of Dashboard objects
        """
        from .dashboard_v2 import Dashboard
        dashboards_data = self.client.list_dashboards(folder_uid=self.uid)
        return [
            Dashboard(self.client, d["uid"], d.get("title", ""), self)
            for d in dashboards_data
        ]

    def get_dashboard(self, uid: str):
        """
        Get a specific dashboard in this folder

        Args:
            uid: Dashboard UID

        Returns:
            Dashboard object or None
        """
        dashboards = self.dashboards()
        for dash in dashboards:
            if dash.uid == uid:
                return dash
        return None

    def create_dashboard(
        self,
        title: str,
        tags: Optional[List[str]] = None
    ):
        """
        Create a new dashboard in this folder

        Args:
            title: Dashboard title
            tags: Optional list of tags

        Returns:
            Dashboard object
        """
        from .dashboard_v2 import Dashboard
        dashboard_data = {
            "title": title,
            "tags": tags or [],
            "panels": [],
            "templating": {"list": []}
        }

        result = self.client.update_dashboard(
            dashboard=dashboard_data,
            message=f"Created dashboard '{title}'",
            overwrite=False
        )

        return Dashboard(
            self.client,
            result["uid"],
            title,
            self
        )

    def find_dashboards_by_title(self, title: str):
        """
        Find dashboards by title (partial match)

        Args:
            title: Title to search for

        Returns:
            List of matching Dashboard objects
        """
        dashboards = self.dashboards()
        return [
            d for d in dashboards
            if title.lower() in d.title.lower()
        ]

    # Batch operations on folder dashboards

    def apply_to_all_dashboards(self, func: callable) -> List[Dict[str, Any]]:
        """
        Apply a function to all dashboards in folder

        Args:
            func: Function that takes a Dashboard object and returns result

        Returns:
            List of results
        """
        results = []
        for dashboard in self.dashboards():
            try:
                result = func(dashboard)
                results.append({
                    "dashboard": dashboard.uid,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                results.append({
                    "dashboard": dashboard.uid,
                    "status": "error",
                    "error": str(e)
                })
        return results

    def __repr__(self) -> str:
        return f"Folder(uid='{self.uid}', title='{self.title}')"


class FolderNode:
    """
    Represents a node in the folder tree structure.
    Used for building hierarchical folder trees from Grafana's parentUid relationships.
    """

    def __init__(
        self,
        title: str,
        uid: Optional[str],
        client: GrafanaClient,
        is_real_folder: bool = False
    ):
        """
        Initialize folder node

        Args:
            title: Folder/node title
            uid: Folder UID (None for virtual path nodes)
            client: Grafana API client
            is_real_folder: True if this is an actual Grafana folder
        """
        self.title = title
        self.uid = uid
        self.client = client
        self.is_real_folder = is_real_folder
        self.parent_uid: Optional[str] = None
        self.children: Dict[str, 'FolderNode'] = {}

    def get_all_dashboards(self) -> List['Dashboard']:
        """Get all dashboards in this node and its children"""
        from .dashboard_v2 import Dashboard
        all_dashboards = []

        # If this is a real folder, get its dashboards
        if self.is_real_folder and self.uid:
            dashboards_data = self.client.list_dashboards(folder_uid=self.uid)
            all_dashboards.extend([
                Dashboard(self.client, d["uid"], d.get("title", ""), None)
                for d in dashboards_data
            ])

        # Recursively get dashboards from children
        for child in self.children.values():
            all_dashboards.extend(child.get_all_dashboards())

        return all_dashboards

    def print_tree(self, indent: int = 0) -> None:
        """Print the folder tree"""
        prefix = "📁 " if self.is_real_folder else "📂 "
        uid_info = f" ({self.uid})" if self.uid else ""
        print("  " * indent + f"{prefix}{self.title}{uid_info}")

        # Print dashboards in this folder
        if self.is_real_folder and self.uid:
            dashboards_data = self.client.list_dashboards(folder_uid=self.uid)
            for dash in dashboards_data:
                print("  " * (indent + 1) + f"  📊 {dash.get('title', 'Untitled')} ({dash.get('uid', '')})")

        # Recursively print children
        for child in self.children.values():
            child.print_tree(indent + 1)

    def get_real_folders(self) -> List[Folder]:
        """Get all real Folder objects in this tree"""
        real_folders = []

        if self.is_real_folder and self.uid:
            real_folders.append(Folder(self.client, self.uid, self.title))

        for child in self.children.values():
            real_folders.extend(child.get_real_folders())

        return real_folders
