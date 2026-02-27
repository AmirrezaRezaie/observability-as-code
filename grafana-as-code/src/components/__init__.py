"""
Dashboard Components
Each component represents a part of a dashboard with add/remove/edit operations
"""

from .datasource import DatasourceComponent
from .panel import PanelComponent
from .variable import VariableComponent

__all__ = ["DatasourceComponent", "PanelComponent", "VariableComponent"]
