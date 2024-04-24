"""Plugin specific exceptions."""


class MissingInputError(Exception):
    """Missing Input"""


class TooManyInputsError(Exception):
    """Too Many Inputs"""


class MultipleValuesError(ValueError):
    """Multiple Values for a Path"""


class NoSuitableWorkflowError(ValueError):
    """Workflow does not exist in current project

    ... or is missing a single replaceable input dataset.
    """
