"""Parameter type tests."""

from cmem_plugin_base.testing import TestPluginContext

from cmem_plugin_loopwf.workflow_type import SuitableWorkflowParameterType
from tests.conftest import FixtureProjectData
from tests.utils import needs_cmem


@needs_cmem
def test_init(loopwf_project: FixtureProjectData) -> None:
    """Test init and list"""
    fd = loopwf_project
    parameter = SuitableWorkflowParameterType()
    completed_list = parameter.autocomplete(
        query_terms=["entity"],
        depend_on_parameter_values=[],
        context=TestPluginContext(fd.project_id),
    )
    assert fd.workflow_id in [_.value for _ in completed_list]
    assert fd.workflow_label in [_.label for _ in completed_list]
    assert len(completed_list) == 1

    completed_list = parameter.autocomplete(
        query_terms=[],
        depend_on_parameter_values=[],
        context=TestPluginContext(fd.project_id),
    )
    assert len(completed_list) == 1

    label = parameter.label(
        value=fd.workflow_id,
        depend_on_parameter_values=[],
        context=TestPluginContext(fd.project_id),
    )
    assert label == fd.workflow_label
