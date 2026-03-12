"""
Panel Component
Manages panels (graphs, stats, gauges) within a dashboard
"""

import copy
from typing import Optional, Dict, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..dashboard_v2 import Dashboard


class PanelComponent:
    """
    Component for managing panels in a dashboard

    Usage:
        dashboard = Dashboard.get(client, "abc123")
        dashboard.panels.add_timeseries(title="CPU", expr="cpu_usage")
        dashboard.panels.remove(panel_id=1)
        dashboard.panels.edit(panel_id=2, title="New Title")
        dashboard.save()
    """

    def __init__(self, dashboard: 'Dashboard'):
        """
        Initialize panel component

        Args:
            dashboard: Parent Dashboard object
        """
        self.dashboard = dashboard

    def _get_next_panel_id(self) -> int:
        """Get next available panel ID"""
        data = self.dashboard._load_data()
        existing_ids = [p.get("id", 0) for p in data.get("panels", [])]
        return max(existing_ids) + 1 if existing_ids else 1

    def _get_next_grid_position(self) -> Dict[str, int]:
        """Calculate next grid position for panel"""
        data = self.dashboard._load_data()
        panels = data.get("panels", [])

        if not panels:
            return {"h": 8, "w": 12, "x": 0, "y": 0}

        # Find bottom-most panel
        max_y = max(
            p.get("gridPos", {}).get("y", 0) + p.get("gridPos", {}).get("h", 0)
            for p in panels
        )
        return {"h": 8, "w": 12, "x": 0, "y": max_y}

    # ADD operations

    def add_timeseries(
        self,
        title: str,
        expr: str,
        datasource_uid: str,
        legend_format: Optional[str] = None,
        grid_pos: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Add a time series panel to dashboard

        Args:
            title: Panel title
            expr: PromQL/expression for the metric
            datasource_uid: Data source UID
            legend_format: Legend format (e.g., "{{instance}}")
            grid_pos: Grid position {h, w, x, y}

        Returns:
            Created panel configuration
        """
        if grid_pos is None:
            grid_pos = self._get_next_grid_position()

        panel = {
            "type": "timeseries",
            "title": title,
            "id": self._get_next_panel_id(),
            "gridPos": grid_pos,
            "targets": [{
                "datasource": {"uid": datasource_uid, "type": "prometheus"},
                "expr": expr,
                "refId": "A",
                "legendFormat": legend_format
            }],
            "options": {
                "legend": {"displayMode": "list", "showLegend": True},
                "tooltip": {"mode": "single"}
            },
            "fieldConfig": {"defaults": {"unit": "short"}}
        }

        data = self.dashboard._load_data()
        data.setdefault("panels", []).append(panel)
        return panel

    def add_stat(
        self,
        title: str,
        expr: str,
        datasource_uid: str,
        grid_pos: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Add a stat panel to dashboard"""
        if grid_pos is None:
            grid_pos = self._get_next_grid_position()

        panel = {
            "type": "stat",
            "title": title,
            "id": self._get_next_panel_id(),
            "gridPos": grid_pos,
            "targets": [{
                "datasource": {"uid": datasource_uid, "type": "prometheus"},
                "expr": expr,
                "refId": "A",
                "instant": True
            }],
            "options": {
                "graphMode": "area",
                "colorMode": "value"
            },
            "fieldConfig": {"defaults": {"unit": "short", "decimals": 2}}
        }

        data = self.dashboard._load_data()
        data.setdefault("panels", []).append(panel)
        return panel

    def add_gauge(
        self,
        title: str,
        expr: str,
        datasource_uid: str,
        min: float = 0,
        max: float = 100,
        grid_pos: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """Add a gauge panel to dashboard"""
        if grid_pos is None:
            grid_pos = self._get_next_grid_position()

        panel = {
            "type": "gauge",
            "title": title,
            "id": self._get_next_panel_id(),
            "gridPos": grid_pos,
            "targets": [{
                "datasource": {"uid": datasource_uid, "type": "prometheus"},
                "expr": expr,
                "refId": "A",
                "instant": True
            }],
            "options": {
                "min": min,
                "max": max,
                "showThresholdLabels": False,
                "showThresholdMarkers": True
            }
        }

        data = self.dashboard._load_data()
        data.setdefault("panels", []).append(panel)
        return panel

    def add_custom(self, panel_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a custom panel configuration to dashboard

        Args:
            panel_config: Complete panel configuration

        Returns:
            Added panel configuration
        """
        data = self.dashboard._load_data()
        panel_config["id"] = self._get_next_panel_id()

        if "gridPos" not in panel_config:
            panel_config["gridPos"] = self._get_next_grid_position()

        data.setdefault("panels", []).append(panel_config)
        return panel_config

    # REMOVE operations

    def remove(self, panel_id: int) -> None:
        """
        Remove panel from dashboard

        Args:
            panel_id: Panel ID to remove
        """
        data = self.dashboard._load_data()
        panels = data.get("panels", [])

        original_count = len(panels)
        data["panels"] = [p for p in panels if p.get("id") != panel_id]

        if len(data["panels"]) == original_count:
            raise ValueError(f"Panel with ID {panel_id} not found")

    def clear(self) -> None:
        """Remove all panels from dashboard"""
        data = self.dashboard._load_data()
        data["panels"] = []

    # EDIT operations

    def edit(self, panel_id: int, **updates) -> None:
        """
        Edit panel properties

        Args:
            panel_id: Panel ID to edit
            **updates: Fields to update (title, gridPos, options, etc.)
        """
        data = self.dashboard._load_data()

        for panel in data.get("panels", []):
            if panel.get("id") == panel_id:
                panel.update(updates)
                return

        raise ValueError(f"Panel with ID {panel_id} not found")

    def edit_query(
        self,
        panel_id: int,
        target_index: int,
        **updates
    ) -> None:
        """
        Edit query/target in panel

        Args:
            panel_id: Panel ID
            target_index: Target index in panel
            **updates: Query fields to update (expr, legendFormat, etc.)
        """
        data = self.dashboard._load_data()

        for panel in data.get("panels", []):
            if panel.get("id") == panel_id:
                targets = panel.get("targets", [])
                if 0 <= target_index < len(targets):
                    targets[target_index].update(updates)
                    return
                raise IndexError(f"Target index {target_index} out of range")

        raise ValueError(f"Panel with ID {panel_id} not found")

    def add_query(
        self,
        panel_id: int,
        expr: str,
        datasource_uid: str,
        legend_format: Optional[str] = None
    ) -> None:
        """
        Add a query to existing panel

        Args:
            panel_id: Panel ID
            expr: Query expression
            datasource_uid: Data source UID
            legend_format: Legend format
        """
        data = self.dashboard._load_data()

        for panel in data.get("panels", []):
            if panel.get("id") == panel_id:
                targets = panel.get("targets", [])

                # Generate new refId
                ref_ids = [t.get("refId", "") for t in targets]
                new_ref_id = chr(ord("A") + len(ref_ids)) if len(ref_ids) < 26 else f"q{len(ref_ids)}"

                new_target = {
                    "datasource": {"uid": datasource_uid, "type": "prometheus"},
                    "expr": expr,
                    "refId": new_ref_id
                }

                if legend_format:
                    new_target["legendFormat"] = legend_format

                panel["targets"] = targets + [new_target]
                return

        raise ValueError(f"Panel with ID {panel_id} not found")

    # LIST operations

    def list_all(self) -> List[Dict[str, Any]]:
        """List all panels in dashboard"""
        return self.dashboard._load_data().get("panels", [])

    def get(self, panel_id: int) -> Optional[Dict[str, Any]]:
        """Get specific panel by ID"""
        for panel in self.list_all():
            if panel.get("id") == panel_id:
                return panel
        return None

    # Other operations

    def duplicate(self, panel_id: int, offset_y: Optional[int] = None) -> Dict[str, Any]:
        """
        Duplicate a panel

        Args:
            panel_id: Panel ID to duplicate
            offset_y: Y offset for new panel

        Returns:
            New panel configuration
        """
        source_panel = self.get(panel_id)
        if not source_panel:
            raise ValueError(f"Panel with ID {panel_id} not found")

        new_panel = copy.deepcopy(source_panel)
        new_panel["id"] = self._get_next_panel_id()

        if offset_y is None:
            offset_y = new_panel.get("gridPos", {}).get("h", 8)

        new_panel["gridPos"]["y"] += offset_y
        new_panel["title"] = f"{new_panel['title']} (copy)"

        data = self.dashboard._load_data()
        data.setdefault("panels", []).append(new_panel)
        return new_panel

    def reorder(self, panel_ids: List[int]) -> None:
        """
        Reorder panels in dashboard

        Args:
            panel_ids: List of panel IDs in desired order
        """
        data = self.dashboard._load_data()
        all_panels = data.get("panels", [])

        panel_map = {p.get("id"): p for p in all_panels}
        ordered = []

        for pid in panel_ids:
            if pid in panel_map:
                ordered.append(panel_map[pid])
                del panel_map[pid]

        # Add remaining panels
        ordered.extend(panel_map.values())
        data["panels"] = ordered
