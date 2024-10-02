from escape_helpers import sparql_escape_uri
from helpers import query, update
from string import Template
import logging

LOG = logging.getLogger(__name__)


QUERY_PRODUCT = Template("""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
     SELECT DISTINCT * WHERE {
       GRAPH <http://mu.semte.ch/graphs/public> {
         $uri a <https://productencatalogus.data.vlaanderen.be/ns/ipdc-lpdc#InstancePublicServiceSnapshot>;
              <http://purl.org/dc/terms/title> ?title; 
              <http://purl.org/dc/terms/description> ?description.    
FILTER (lang(?title) = "nl")
FILTER (lang(?description) = "nl")
         OPTIONAL {
           $uri <http://vocab.belgif.be/ns/publicservice#hasRequirement> ?requirement.
           ?requirement <http://purl.org/dc/terms/description> ?requirementDescription;
                        <http://purl.org/dc/terms/title> ?requirementTitle;
                        <http://www.w3.org/ns/shacl#order> ?requirementOrder.
FILTER (lang(?requirementTitle) = "nl")
FILTER (lang(?requirementDescription) = "nl")
         }
           $uri <http://purl.org/vocab/cpsv#follows> ?procedure.
           ?procedure <http://purl.org/dc/terms/title> ?procedureTitle;
             <http://purl.org/dc/terms/description> ?procedureDescription;
             <http://www.w3.org/ns/shacl#order> ?procedureOrder.
FILTER (lang(?procedureTitle) = "nl")
FILTER (lang(?procedureDescription) = "nl")
       }
     } ORDER BY ?sub LIMIT 1000 OFFSET 0
""")

def paginated_bindings(sparql_query, offset=0, limit=200):
    execute_query = lambda: query("{} LIMIT {} OFFSET {}".format(sparql_query, limit, offset))['results']['bindings']
    bindings = []
    last_execution = execute_query()
    while len(last_execution):
        bindings += last_execution
        offset += limit
        last_execution = execute_query()

    return bindings

def query_product_with_uri(uri):
    return paginated_bindings(QUERY_PRODUCT.substitute(uri=sparql_escape_uri(uri)))
