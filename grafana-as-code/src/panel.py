"""
Panel Management Module
Operations for managing dashboard panels (graphs, stats, etc.)
"""

from typing import Dict, List, Any, Optional
from .client import GrafanaClient


class PanelManager:
    """Manager for panel operations"""

    def __init__(self, client: GrafanaClient):
        """
        Initialize panel manager

        Args:
            client: Grafana API client instance
        """
        self.client = client

    def create_timeseries_panel(
        self,
        title: str,
        expr: str,
        datasource_uid: str,
        legend_format: Optional[str] = None,
        grid_pos: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Create a time series panel configuration

        Args:
            title: Panel title
            expr: PromQL/expression for the metric
            datasource_uid: Data source UID
            legend_format: Legend format (e.g., "{{instance}}")
            grid_pos: Grid position {h, w, x, y}

        Returns:
            Panel configuration
        """
        if grid_pos is None:
            grid_pos = {"h": 8, "w": 12, "x": 0, "y": 0}

        target = {
            "datasource": {"uid": datasource_uid, "type": "prometheus"},
            "expr": expr,
            "refId": "A",
            "legendFormat": legend_format
        }

        return {
            "type": "timeseries",
            "title": title,
            "gridPos": grid_pos,
            "targets": [target],
            "options": {
                "legend": {
                    "displayMode": "list",
                    "showLegend": True,
                    "placement": "bottom"
                },
                "tooltip": {
                    "mode": "single"
                }
            },
            "fieldConfig": {
                "defaults": {
                    "unit": "short"
                }
            }
        }

    def create_stat_panel(
        self,
        title: str,
        expr: str,
        datasource_uid: str,
        grid_pos: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Create a stat panel configuration

        Args:
            title: Panel title
            expr: PromQL/expression for the metric
            datasource_uid: Data source UID
            grid_pos: Grid position {h, w, x, y}

        Returns:
            Panel configuration
        """
        if grid_pos is None:
            grid_pos = {"h": 8, "w": 6, "x": 0, "y": 0}

        target = {
            "datasource": {"uid": datasource_uid, "type": "prometheus"},
            "expr": expr,
            "refId": "A",
            "instant": True
        }

        return {
            "type": "stat",
            "title": title,
            "gridPos": grid_pos,
            "targets": [target],
            "options": {
                "graphMode": "area",
                "colorMode": "value"
            },
            "fieldConfig": {
                "defaults": {
                    "unit": "short",
                    "decimals": 2
                }
            }
        }

    def create_gauge_panel(
        self,
        title: str,
        expr: str,
        datasource_uid: str,
        min: float = 0,
        max: float = 100,
        grid_pos: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Create a gauge panel configuration

        Args:
            title: Panel title
            expr: PromQL/expression for the metric
            datasource_uid: Data source UID
            min: Minimum value
            max: Maximum value
            grid_pos: Grid position {h, w, x, y}

        Returns:
            Panel configuration
        """
        if grid_pos is None:
            grid_pos = {"h": 8, "w": 6, "x": 0, "y": 0}

        target = {
            "datasource": {"uid": datasource_uid, "type": "prometheus"},
            "expr": expr,
            "refId": "A",
            "instant": True
        }

        return {
            "type": "gauge",
            "title": title,
            "gridPos": grid_pos,
            "targets": [target],
            "options": {
                "min": min,
                "max": max,
                "showThresholdLabels": False,
                "showThresholdMarkers": True
            }
        }

    def add_panel_to_dashboard(
        self,
        dashboard_uid: str,
        panel_config: Dict[str, Any],
        position: Optional[str] = "bottom"
    ) -> Dict[str, Any]:
        """
        Add panel to dashboard

        Args:
            dashboard_uid: Dashboard UID
            panel_config: Panel configuration
            position: Where to add panel ("top", "bottom", or specific grid position)

        Returns:
            Update response
        """
        dashboard = self.client.get_dashboard_by_uid(dashboard_uid)

        # Generate new panel ID
        existing_ids = [p.get("id", 0) for p in dashboard.get("panels", [])]
        new_id = max(existing_ids) + 1 if existing_ids else 1
        panel_config["id"] = new_id

        # Calculate grid position
        if position == "bottom":
            panels = dashboard.get("panels", [])
            if panels:
                # Find bottom-most panel
                max_y = max(p.get("gridPos", {}).get("y", 0) + p.get("gridPos", {}).get("h", 0) for p in panels)
                panel_config["gridPos"]["y"] = max_y

        # Add panel
        if "panels" not in dashboard:
            dashboard["panels"] = []
        dashboard["panels"].append(panel_config)

        return self.client.update_dashboard(
            dashboard=dashboard,
            message=f"Added panel: {panel_config.get('title', 'Untitled')}"
        )

    def remove_panel_from_dashboard(
        self,
        dashboard_uid: str,
        panel_id: int
    ) -> Dict[str, Any]:
        """
        Remove panel from dashboard

        Args:
            dashboard_uid: Dashboard UID
            panel_id: Panel ID to remove

        Returns:
            Update response
        """
        dashboard = self.client.get_dashboard_by_uid(dashboard_uid)
        panels = dashboard.get("panels", [])

        original_count = len(panels)
        dashboard["panels"] = [p for p in panels if p.get("id") != panel_id]

        if len(dashboard["panels"]) == original_count:
            raise ValueError(f"Panel with ID {panel_id} not found")

        return self.client.update_dashboard(
            dashboard=dashboard,
            message=f"Removed panel {panel_id}"
        )

    def update_panel(
        self,
        dashboard_uid: str,
        panel_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update existing panel

        Args:
            dashboard_uid: Dashboard UID
            panel_id: Panel ID to update
            updates: Fields to update

        Returns:
            Update response
        """
        dashboard = self.client.get_dashboard_by_uid(dashboard_uid)

        for panel in dashboard.get("panels", []):
            if panel.get("id") == panel_id:
                panel.update(updates)
                return self.client.update_dashboard(
                    dashboard=dashboard,
                    message=f"Updated panel {panel_id}"
                )

        raise ValueError(f"Panel with ID {panel_id} not found")

    def add_query_to_panel(
        self,
        dashboard_uid: str,
        panel_id: int,
        expr: str,
        datasource_uid: str,
        legend_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add query/target to existing panel

        Args:
            dashboard_uid: Dashboard UID
            panel_id: Panel ID
            expr: Query expression
            datasource_uid: Data source UID
            legend_format: Legend format

        Returns:
            Update response
        """
        dashboard = self.client.get_dashboard_by_uid(dashboard_uid)

        # Find panel
        panel = None
        for p in dashboard.get("panels", []):
            if p.get("id") == panel_id:
                panel = p
                break

        if not panel:
            raise ValueError(f"Panel with ID {panel_id} not found")

        # Generate new refId
        existing_targets = panel.get("targets", [])
        ref_ids = [t.get("refId", "") for t in existing_targets]
        new_ref_id = chr(ord("A") + len(ref_ids)) if len(ref_ids) < 26 else f"q{len(ref_ids)}"

        # Add target
        new_target = {
            "datasource": {"uid": datasource_uid, "type": "prometheus"},
            "expr": expr,
            "refId": new_ref_id
        }

        if legend_format:
            new_target["legendFormat"] = legend_format

        panel["targets"] = existing_targets + [new_target]

        return self.client.update_dashboard(
            dashboard=dashboard,
            message=f"Added query to panel {panel_id}"
        )

    def duplicate_panel(
        self,
        dashboard_uid: str,
        panel_id: int,
        offset_y: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Duplicate panel in dashboard

        Args:
            dashboard_uid: Dashboard UID
            panel_id: Panel ID to duplicate
            offset_y: Y offset for new panel (default: same as panel height)

        Returns:
            Update response
        """
        import copy

        dashboard = self.client.get_dashboard_by_uid(dashboard_uid)

        # Find panel
        source_panel = None
        panel_index = None
        for i, p in enumerate(dashboard.get("panels", [])):
            if p.get("id") == panel_id:
                source_panel = p
                panel_index = i
                break

        if not source_panel:
            raise ValueError(f"Panel with ID {panel_id} not found")

        # Create duplicate
        new_panel = copy.deepcopy(source_panel)

        # Generate new ID
        existing_ids = [p.get("id", 0) for p in dashboard.get("panels", [])]
        new_panel["id"] = max(existing_ids) + 1

        # Offset position
        if offset_y is None:
            offset_y = new_panel.get("gridPos", {}).get("h", 8)

        new_panel["gridPos"]["y"] += offset_y
        new_panel["title"] = f"{new_panel['title']} (copy)"

        # Insert after source
        dashboard["panels"].insert(panel_index + 1, new_panel)

        return self.client.update_dashboard(
            dashboard=dashboard,
            message=f"Duplicated panel {panel_id}"
        )

    def reorder_panels(
        self,
        dashboard_uid: str,
        panel_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Reorder panels in dashboard

        Args:
            dashboard_uid: Dashboard UID
            panel_ids: List of panel IDs in desired order

        Returns:
            Update response
        """
        dashboard = self.client.get_dashboard_by_uid(dashboard_uid)
        all_panels = dashboard.get("panels", [])

        # Create ordered list
        panel_map = {p.get("id"): p for p in all_panels}
        ordered = []
        for pid in panel_ids:
            if pid in panel_map:
                ordered.append(panel_map[pid])
                del panel_map[pid]

        # Add any remaining panels
        ordered.extend(panel_map.values())

        dashboard["panels"] = ordered

        return self.client.update_dashboard(
            dashboard=dashboard,
            message="Reordered panels"
        )
