"""Parameter type tests."""

from copy import deepcopy

import pytest
from cmem_plugin_base.dataintegration.entity import Entities

from cmem_plugin_loopwf import exceptions
from cmem_plugin_loopwf.task import StartWorkflow
from tests.conftest import FixtureProjectData
from tests.utils import needs_cmem


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
    input_entities = list(deepcopy(entities_json.entities))  # keep a copy to compare later
    task = StartWorkflow(workflow=loopwf_project.workflow_id, forward_entities=True)
    output: Entities = task.execute(
        context=loopwf_project.execution_context, inputs=[entities_json]
    )
    output_entities = list(output.entities)
    assert len(output_entities) == len(input_entities)
    for input_entity, output_entity in zip(input_entities, output_entities, strict=False):
        assert input_entity.values == output_entity.values

    task_no_forward = StartWorkflow(workflow=loopwf_project.workflow_id, forward_entities=False)
    assert not task_no_forward.execute(
        context=loopwf_project.execution_context, inputs=[entities_json]
    )


@needs_cmem
def test_task_errors(
    loopwf_project: FixtureProjectData, entities_json: Entities, broken_entities: Entities
) -> None:
    """Test init and list"""
    task = StartWorkflow(workflow=loopwf_project.workflow_id)
    with pytest.raises(exceptions.MissingInputError):
        task.execute(context=loopwf_project.execution_context, inputs=[])
    with pytest.raises(exceptions.TooManyInputsError):
        task.execute(
            context=loopwf_project.execution_context, inputs=[entities_json, entities_json]
        )
    with pytest.raises(exceptions.MultipleValuesError):
        task.execute(context=loopwf_project.execution_context, inputs=[broken_entities])

    task_not_there = StartWorkflow(workflow="not-there")
    with pytest.raises(exceptions.NoSuitableWorkflowError):
        task_not_there.execute(context=loopwf_project.execution_context, inputs=[entities_json])
