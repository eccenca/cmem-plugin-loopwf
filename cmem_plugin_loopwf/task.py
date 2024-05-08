"""Random values workflow plugin module"""
import json
from collections.abc import Sequence
from pathlib import Path
from tempfile import NamedTemporaryFile

from cmem.cmempy.workflow.workflow import execute_workflow_io, get_workflows_io
from cmem_plugin_base.dataintegration.context import ExecutionContext, ExecutionReport
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginParameter
from cmem_plugin_base.dataintegration.entity import (
    Entities,
    Entity,
    EntityPath,
    EntitySchema,
)
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import FixedNumberOfInputs, FlexibleSchemaPort
from cmem_plugin_base.dataintegration.utils import setup_cmempy_user_access

from cmem_plugin_loopwf import exceptions
from cmem_plugin_loopwf.workflow_type import SuitableWorkflowParameterType

DOCUMENTATION = """This workflow task operates on a list of incoming entities
and sequentially starts a single "inner" workflow for each entity.
In case one "inner" workflow fails, the execution is stopped with an error.
In this case the error message can be seen in the Activities view
(see `Execute with payload of [inner workflow name]`).

The started workflow needs to have a replaceable JSON dataset as input.

Current notes and limitations:

- The entities which are the input of the "inner" workflow can not be hierarchic.
- The replaceable dataset of the "inner" workflow needs to be a JSON dataset.
- There is no check for circles implemented!
"""


@Plugin(
    label="Start Workflow per Entity",
    description="Loop over the output of a task and start a sub-workflow for each entity.",
    documentation=DOCUMENTATION,
    icon=Icon(package=__package__, file_name="loopwf.svg"),
    plugin_id="cmem_plugin_loopwf-task-StartWorkflow",
    parameters=[
        PluginParameter(
            name="workflow",
            label="Workflow",
            param_type=SuitableWorkflowParameterType(),
            description="Which workflow do you want to start per entity.",
        ),
    ],
)
class StartWorkflow(WorkflowPlugin):
    """Start Workflow per Entity"""

    context: ExecutionContext
    schema: EntitySchema

    def __init__(self, workflow: str) -> None:
        self.workflow = workflow
        self.input_ports = FixedNumberOfInputs([FlexibleSchemaPort()])
        self.output_port = None
        self.workflows_started = 0

    def execute(
        self,
        inputs: Sequence[Entities],
        context: ExecutionContext,
    ) -> None:
        """Run the workflow operator."""
        self.log.info("Start execute")
        self.context = context
        self.validate_inputs(inputs=inputs)
        self.schema = inputs[0].schema
        self.validate_workflow(workflow=self.workflow)

        for entity in inputs[0].entities:
            self.start_workflow(entity=entity)

        self.log.info("Stop execute")

    @staticmethod
    def validate_inputs(inputs: Sequence[Entities]) -> None:
        """Validate inputs."""
        inputs_count = len(inputs)
        if inputs_count == 0:
            raise exceptions.MissingInputError("Need a connected input task to get data from.")
        if inputs_count > 1:
            raise exceptions.TooManyInputsError("Can process a single input only.")

    def validate_workflow(self, workflow: str) -> None:
        """Validate a workflow (ID)"""
        current_project = self.context.task.project_id()
        setup_cmempy_user_access(context=self.context.user)
        suitable_workflows: dict[str, dict] = {
            f"{_['id']}": _
            for _ in get_workflows_io()
            if self.context.task.project_id() == _["projectId"] and len(_["variableInputs"]) == 1
        }
        if workflow not in suitable_workflows:
            raise exceptions.NoSuitableWorkflowError(
                f"Workflow '{workflow}' does not exist in project '{current_project}'"
                " or is missing a single replaceable input dataset."
            )
        self.log.info(str(suitable_workflows))

    def start_workflow(self, entity: Entity) -> None:
        """Start a single workflow."""
        entity_as_dict: dict = self.entity_to_dict(entity=entity, schema=self.schema)
        entity_as_json: str = json.dumps(entity_as_dict)
        self.log.info(f"Processing new entity: {entity_as_json}")
        # start workflow here
        with NamedTemporaryFile(mode="w+") as temp_file:
            self.log.info(f"temp file for entity: {temp_file.name}")
            temp_file.write(entity_as_json)
            temp_file.flush()
            self.log.info(f"temp file content: {Path(temp_file.name).read_text()}")
            setup_cmempy_user_access(context=self.context.user)
            execute_workflow_io(
                project_name=self.context.task.project_id(),
                task_name=self.workflow,
                input_file=temp_file.name,
                input_mime_type="application/x-plugin-json",
                output_mime_type="guess",
                auto_config=False,
            )
        self.workflows_started += 1
        self.context.report.update(
            ExecutionReport(
                entity_count=self.workflows_started,
                operation="start",
                operation_desc="workflows started",
            )
        )

    @staticmethod
    def entity_to_dict(entity: Entity, schema: EntitySchema) -> dict:
        """Convert an entity to a dictionary, using the schema"""
        path: EntityPath
        values: Sequence[str]
        entity_dict = {}
        for path, values in zip(schema.paths, entity.values, strict=True):
            if len(values) > 1:
                raise exceptions.MultipleValuesError(f"Multiple values for entity path {path.path}")
            entity_dict[path.path] = values[0]
        return entity_dict
