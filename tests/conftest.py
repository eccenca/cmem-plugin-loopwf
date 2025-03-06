"""pytest configuration."""

import json
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner, Result
from cmem_cmemc import cli
from cmem_plugin_base.dataintegration.entity import Entities
from cmem_plugin_base.dataintegration.utils.entity_builder import build_entities_from_data

from tests.utils import needs_cmem

FIXTURE_DIR: Path = Path(__file__).parent / "fixtures"
RUNNER = CliRunner()


def cmemc(*arg: str | Path) -> Result:
    """Run cmemc command."""
    return RUNNER.invoke(cli, [str(_) for _ in arg])


@dataclass
class FixtureProjectData:
    """FixtureData for loopwf_project"""

    project_id: str = "loopwf"
    workflow_id: str = "run-per-entity"
    workflow_title: str = "run per entity"
    workflow_label: str = f"{workflow_title} ({workflow_id})"
    outer_workflow_id: str = "run"
    task_id: str = "StartWorkflowperEntity_567a764bfe0f7faf"
    graph_iri: str = "https://example.org/graph/"


@needs_cmem
@pytest.fixture
def loopwf_project() -> Generator[FixtureProjectData, Any, None]:
    """Provide the loopwf project"""
    data = FixtureProjectData()
    result = cmemc("project", "import", "--overwrite", FIXTURE_DIR / "loopwf.project.zip")
    assert result.exit_code == 0
    projects = cmemc("project", "list", "--id-only").output
    assert data.project_id in projects
    cmemc("graph", "delete", data.graph_iri)
    assert data.graph_iri not in cmemc("graph", "list", "--id-only").output
    yield data
    cmemc("project", "delete", data.project_id)
    projects = cmemc("project", "list", "--id-only").output
    assert data.project_id not in projects
    cmemc("graph", "delete", data.graph_iri)
    assert data.graph_iri not in cmemc("graph", "list", "--id-only").output


@pytest.fixture
def entities_json() -> Entities:
    """Provide entities.json as entities fixture"""
    return build_entities_from_data(
        json.loads(Path(FIXTURE_DIR / "entities.json").read_text()),
    )


@pytest.fixture
def bad_entities_json() -> Entities:
    """Provide entities.json as entities fixture"""
    return build_entities_from_data(
        json.loads(Path(FIXTURE_DIR / "bad_entities.json").read_text()),
    )
