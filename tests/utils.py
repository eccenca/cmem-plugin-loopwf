"""utils"""

from os import environ

import pytest
from cmem.cmempy.queries import SparqlQuery

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
    query = SparqlQuery(query_type="SELECT", text=query_str)
    result = query.get_json_results()
    return int(result["results"]["bindings"][0]["concepts"]["value"])
