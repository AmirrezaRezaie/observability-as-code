"""
Grafana Dashboard Manager
A toolkit for managing Grafana dashboards via API

Object-Oriented API:
- Folder: Represents a Grafana folder
- Dashboard: Represents a dashboard with component managers
- DatasourceComponent: Manage datasources in a dashboard
- PanelComponent: Manage panels in a dashboard
- VariableComponent: Manage variables in a dashboard

Legacy API (deprecated):
- DashboardManager, DatasourceManager, PanelManager, VariableManager
"""

from .client import GrafanaClient

# Object-Oriented API
from .folder import Folder
from .dashboard import Dashboard
from .components import DatasourceComponent, PanelComponent, VariableComponent

# Legacy API (still available for backward compatibility)
from .dashboard import DashboardManager
from .datasource import DatasourceManager
from .panel import PanelManager
from .variable import VariableManager

__all__ = [
    # Core
    "GrafanaClient",

    # Object-Oriented API (Recommended)
    "Folder",
    "Dashboard",
    "DatasourceComponent",
    "PanelComponent",
    "VariableComponent",

    # Legacy API
    "DashboardManager",
    "DatasourceManager",
    "PanelManager",
    "VariableManager"
]

__version__ = "2.0.0"
