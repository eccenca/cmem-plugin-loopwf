"""utils"""

import json
from os import environ

import pytest
from cmem_client.client import Client
from cmem_plugin_base.testing import TestExecutionContext

needs_cmem = pytest.mark.skipif(
    environ.get("CMEM_BASE_URI", "") == "", reason="Needs CMEM configuration"
)


def number_of_concepts() -> int:
    """Return number of concepts

    Assumption: each workflow gets only one entity (path = label) which is
    transformed into a single concept
    """
    query_str = """PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT (COUNT(?concept) AS ?concepts)
FROM <https://example.org/graph/>
WHERE {
  ?concept a skos:Concept
}"""
    client = Client.from_context(context=TestExecutionContext())
    result = json.loads(
        client.queries.execute_query(query=query_str, accept="application/sparql-results+json")
    )
    return int(result["results"]["bindings"][0]["concepts"]["value"])
