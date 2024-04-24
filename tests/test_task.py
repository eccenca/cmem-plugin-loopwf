"""Parameter type tests."""

import pytest
from cmem_plugin_base.dataintegration.entity import Entities

from cmem_plugin_loopwf import exceptions
from cmem_plugin_loopwf.task import StartWorkflow
from tests.conftest import FixtureProjectData
from tests.utils import TestExecutionContext, needs_cmem


def test_entity_to_dict(entities_json: Entities) -> None:
    """Test entity_to_dict"""
    _ = StartWorkflow.entity_to_dict(
        entity=next(entities_json.entities), schema=entities_json.schema
    )
    assert len(_) == 1
    assert _["label"] == "Entity 1"


@needs_cmem
def test_task(loopwf_project: FixtureProjectData, entities_json: Entities) -> None:
    """Test init and list"""
    fd = loopwf_project
    context = TestExecutionContext(project_id=fd.project_id, task_id=fd.task_id)
    task = StartWorkflow(workflow=fd.workflow_id)
    task.execute(context=context, inputs=[entities_json])


@needs_cmem
def test_task_errors(loopwf_project: FixtureProjectData, entities_json: Entities) -> None:
    """Test init and list"""
    fd = loopwf_project
    context = TestExecutionContext(project_id=fd.project_id, task_id=fd.task_id)
    task = StartWorkflow(workflow="not-there")
    with pytest.raises(exceptions.MissingInputError):
        task.execute(context=context, inputs=[])
    with pytest.raises(exceptions.TooManyInputsError):
        task.execute(context=context, inputs=[entities_json, entities_json])
    with pytest.raises(exceptions.NoSuitableWorkflowError):
        task.execute(context=context, inputs=[entities_json])
