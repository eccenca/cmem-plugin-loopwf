"""DI Workflow Parameter Type."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cmem_client.client import Client
from cmem_plugin_base.dataintegration.types import Autocompletion, StringParameterType

if TYPE_CHECKING:
    from cmem_client.models.workflow import Workflow
    from cmem_plugin_base.dataintegration.context import PluginContext


def workflow_label(workflow: Workflow) -> str:
    """Get the display label of a workflow"""
    return f"{workflow.label} ({workflow.id})"


class SuitableWorkflowParameterType(StringParameterType):
    """Workflow parameter type to list all suitable workflows"""

    allow_only_autocompleted_values: bool = True

    autocomplete_value_with_labels: bool = True

    def label(
        self,
        value: str,
        depend_on_parameter_values: list[Any],  # noqa: ARG002
        context: PluginContext,
    ) -> str | None:
        """Return the label for the given workflow ID"""
        workflows = self.get_suitable_workflows(
            client=Client.from_context(context=context), project_id=context.project_id
        )
        workflow = workflows.get(value)
        return workflow_label(workflow) if workflow else None

    @staticmethod
    def get_suitable_workflows(client: Client, project_id: str) -> dict[str, Workflow]:
        """Get all suitable workflows for a given project"""
        return {
            _.id: _
            for _ in client.workflows.values()
            if project_id == _.project_id and len(_.variable_inputs) == 1
        }

    def autocomplete(
        self,
        query_terms: list[str],
        depend_on_parameter_values: list[Any],  # noqa: ARG002
        context: PluginContext,
    ) -> list[Autocompletion]:
        """Autocomplete workflow parameters

        Returns all workflow IDs that match ALL provided query terms.
        """
        workflows = self.get_suitable_workflows(
            client=Client.from_context(context=context), project_id=context.project_id
        )
        result = []
        for _ in workflows.values():
            label = workflow_label(_)
            if len(query_terms) == 0:
                result.append(Autocompletion(value=_.id, label=label))
                continue
            for term in query_terms:
                if term.lower() in label.lower():
                    result.append(Autocompletion(value=_.id, label=label))
                    continue
        result.sort(key=lambda x: x.label)
        return list(set(result))
