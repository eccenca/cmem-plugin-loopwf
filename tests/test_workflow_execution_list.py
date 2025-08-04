"""Test WorkflowExecutionList"""

from dataclasses import dataclass

import pytest
from cmem_plugin_base.dataintegration.entity import Entities
from cmem_plugin_base.dataintegration.plugins import PluginLogger
from cmem_plugin_base.dataintegration.utils.entity_builder import build_entities_from_data
from cmem_plugin_base.testing import TestExecutionContext

from cmem_plugin_loopwf.task import WorkflowExecution, WorkflowExecutionList
from tests.conftest import FixtureProjectData
from tests.utils import number_of_concepts


@dataclass
class WorkflowExecutionFixture:
    """Fixture for WorkflowExecutionList"""

    number_of_workflows: int
    input_entities: Entities
    loopwf_project: FixtureProjectData
    executions: WorkflowExecutionList


@pytest.fixture
def execution_fixture(loopwf_project: FixtureProjectData) -> WorkflowExecutionFixture:
    """Provide WorkflowExecutionFixture"""
    number_of_workflows = 100
    input_entities = build_entities_from_data(
        [{"label": f"Entity {x}"} for x in range(number_of_workflows)]
    )
    executions = WorkflowExecutionList()
    executions.context = TestExecutionContext()
    executions.logger = PluginLogger()
    for entity in input_entities.entities:
        new_execution = WorkflowExecution(
            task_id=loopwf_project.workflow_id,
            project_id=loopwf_project.project_id,
            entity=entity,
            schema=input_entities.schema,
            execution_context=TestExecutionContext(
                project_id=loopwf_project.project_id, task_id=loopwf_project.workflow_id
            ),
            logger=PluginLogger(),
        )
        executions.append(new_execution)

    return WorkflowExecutionFixture(
        loopwf_project=loopwf_project,
        number_of_workflows=number_of_workflows,
        input_entities=input_entities,
        executions=executions,
    )


def test_start_x_workflow(execution_fixture: WorkflowExecutionFixture) -> None:
    """Test WorkflowExecutionList"""
    executions = execution_fixture.executions
    number_of_workflows = execution_fixture.number_of_workflows
    # base check
    assert number_of_workflows == executions.queued + executions.finished + executions.running
    assert executions.queued == number_of_workflows
    assert executions.finished == 0
    assert executions.running == 0
    assert number_of_concepts() == 0

    executions.execute(parallel_execution=6)

    assert number_of_workflows == executions.queued + executions.finished + executions.running
    assert executions.queued == 0
    assert executions.finished == number_of_workflows
    assert executions.running == 0
    assert number_of_concepts() == number_of_workflows == executions.finished
