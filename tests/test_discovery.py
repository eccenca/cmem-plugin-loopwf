"""Test discover plugin"""

from cmem_plugin_base.dataintegration.discovery import discover_plugins


def test_discovery() -> None:
    """Test discovery plugin"""
    discover = discover_plugins()
    assert len(discover.plugins) > 0
    assert "cmem_plugin_loopwf-task-StartWorkflow" in [_.plugin_id for _ in discover.plugins]
