"""
Grafana API Client
Base client for interacting with Grafana API
"""

import os
import requests
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GrafanaClient:
    """Base Grafana API Client"""

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize Grafana client

        Args:
            url: Grafana URL (default: from env GRAFANA_URL)
            api_key: API key for authentication (default: from env GRAFANA_API_KEY)
            username: Username for basic auth (alternative to api_key)
            password: Password for basic auth
            timeout: Request timeout in seconds
        """
        self.url = url or os.getenv("GRAFANA_URL", "http://localhost:3000")
        self.url = self.url.rstrip("/")
        self.timeout = timeout

        # Setup authentication
        self.api_key = api_key or os.getenv("GRAFANA_API_KEY")
        self.username = username or os.getenv("GRAFANA_USERNAME")
        self.password = password or os.getenv("GRAFANA_PASSWORD")

        if self.api_key:
            self.headers = {"Authorization": f"Bearer {self.api_key}"}
        elif self.username and self.password:
            self.auth = (self.username, self.password)
            self.headers = {}
        else:
            self.headers = {}
            self.auth = None

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Grafana API

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters

        Returns:
            Response JSON as dictionary

        Raises:
            requests.HTTPError: On HTTP errors
        """
        url = f"{self.url}/api{endpoint}"
        headers = {
            "Content-Type": "application/json",
            **self.headers
        }

        response = requests.request(
            method=method,
            url=url,
            json=data,
            params=params,
            headers=headers,
            auth=getattr(self, 'auth', None),
            timeout=self.timeout
        )

        response.raise_for_status()

        # Return empty dict for 204 No Content
        if response.status_code == 204:
            return {}

        return response.json()

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request"""
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """Make POST request"""
        return self._request("POST", endpoint, data=data)

    def put(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """Make PUT request"""
        return self._request("PUT", endpoint, data=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request"""
        return self._request("DELETE", endpoint)

    # Health and Info

    def health(self) -> Dict[str, Any]:
        """Get Grafana health status"""
        return self.get("/health")

    def search(
        self,
        query: str = "",
        type: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search dashboards and folders

        Args:
            query: Search query
            type: Filter by type (dash-folder, dash-db)
            tag: Filter by tag

        Returns:
            List of search results
        """
        params = {}
        if query:
            params["query"] = query
        if type:
            params["type"] = type
        if tag:
            params["tag"] = tag

        return self.get("/search", params=params)

    def list_dashboards(self, folder_uid: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all dashboards

        Args:
            folder_uid: Filter by folder UID

        Returns:
            List of dashboard metadata
        """
        results = self.search(type="dash-db")
        if folder_uid:
            results = [d for d in results if d.get("folderUid") == folder_uid]
        return results

    def list_folders(self) -> List[Dict[str, Any]]:
        """
        List all folders including nested folders.
        Uses search API to get all folders with their parentUid/folderUid relationships.
        """
        # Get all folders using search API
        search_results = self.search(type="dash-folder")

        # Transform search results to folder format with parentUid
        folders = []
        for item in search_results:
            folder_data = {
                "id": item.get("id"),
                "uid": item.get("uid"),
                "title": item.get("title"),
                "parentUid": item.get("folderUid")  # Grafana uses folderUid for parent relationship
            }
            folders.append(folder_data)

        return folders

    # Dashboard Operations

    def get_dashboard(self, uid: str) -> Dict[str, Any]:
        """
        Get dashboard by UID

        Args:
            uid: Dashboard UID

        Returns:
            Dashboard model including dashboard JSON
        """
        return self.get(f"/dashboards/uid/{uid}")

    def get_dashboard_by_uid(self, uid: str) -> Dict[str, Any]:
        """
        Get dashboard JSON by UID (shortcut)

        Args:
            uid: Dashboard UID

        Returns:
            Dashboard JSON
        """
        response = self.get_dashboard(uid)
        return response.get("dashboard", {})

    def update_dashboard(
        self,
        dashboard: Dict[str, Any],
        message: Optional[str] = None,
        overwrite: bool = True
    ) -> Dict[str, Any]:
        """
        Create/update dashboard

        Args:
            dashboard: Dashboard JSON
            message: Commit message
            overwrite: Overwrite existing dashboard

        Returns:
            Response with status, uid, url, etc.
        """
        payload = {
            "dashboard": dashboard,
            "overwrite": overwrite,
            "message": message or "Updated via API"
        }
        return self.post("/dashboards/db", payload)

    def delete_dashboard(self, uid: str) -> Dict[str, Any]:
        """
        Delete dashboard by UID

        Args:
            uid: Dashboard UID

        Returns:
            Response message
        """
        return self.delete(f"/dashboards/uid/{uid}")

    # Data Source Operations

    def list_datasources(self) -> List[Dict[str, Any]]:
        """List all data sources"""
        return self.get("/datasources")

    def get_datasource(self, datasource_id: int) -> Dict[str, Any]:
        """Get data source by ID"""
        return self.get(f"/datasources/{datasource_id}")

    def get_datasource_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get data source by name"""
        datasources = self.list_datasources()
        for ds in datasources:
            if ds.get("name") == name:
                return ds
        return None

    def create_datasource(self, datasource: Dict[str, Any]) -> Dict[str, Any]:
        """Create new data source"""
        return self.post("/datasources", datasource)

    def update_datasource(
        self,
        datasource_id: int,
        datasource: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update existing data source"""
        return self.put(f"/datasources/{datasource_id}", datasource)

    def delete_datasource(self, datasource_id: int) -> Dict[str, Any]:
        """Delete data source by ID"""
        return self.delete(f"/datasources/{datasource_id}")
