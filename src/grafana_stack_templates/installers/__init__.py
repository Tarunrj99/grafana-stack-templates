"""Module-type-specific installers."""

from .alert_rule import install_alert_rule
from .dashboard import install_dashboard
from .recipe import install_recipe
from .slack_template import install_slack_template
from .sm_check import install_sm_check

__all__ = [
    "install_alert_rule",
    "install_dashboard",
    "install_recipe",
    "install_slack_template",
    "install_sm_check",
]
