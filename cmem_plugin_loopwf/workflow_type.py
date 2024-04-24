"""DI Workflow Parameter Type."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cmem.cmempy.workflow.workflow import get_workflows_io
from cmem.cmempy.workspace.tasks import get_task
from cmem_plugin_base.dataintegration.types import Autocompletion, StringParameterType
from cmem_plugin_base.dataintegration.utils import setup_cmempy_user_access

if TYPE_CHECKING:
    from cmem_plugin_base.dataintegration.context import PluginContext


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
        setup_cmempy_user_access(context.user)
        task = get_task(project=context.project_id, task=value)
        identifier = task["id"]
        title = str(task["metadata"]["label"])
        return f"{title} ({identifier})"

    @staticmethod
    def get_suitable_workflows(project_id: str) -> dict[str, dict]:
        """Get all suitable workflows for a given project"""
        return {
            f"{_['id']}": _
            for _ in get_workflows_io()
            if project_id == _["projectId"] and len(_["variableInputs"]) == 1
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
        setup_cmempy_user_access(context.user)
        result = []
        for _ in self.get_suitable_workflows(project_id=context.project_id).values():
            identifier = _["id"]
            title = _["label"]
            label = f"{title} ({identifier})"
            if len(query_terms) == 0:
                result.append(Autocompletion(value=identifier, label=label))
                continue
            for term in query_terms:
                if term.lower() in label.lower():
                    result.append(Autocompletion(value=identifier, label=label))
                    continue
        result.sort(key=lambda x: x.label)
        return list(set(result))
