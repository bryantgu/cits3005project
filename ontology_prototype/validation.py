"""SHACL checks over an explicitly supplied graph, without hidden inference."""
from rdflib import Graph
from pyshacl import validate

SHAPES = '''
@prefix ex: <https://example.org/cits3005-prototype#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:NoPrerequisiteCycle a sh:NodeShape ;
    sh:targetClass ex:Unit ;
    sh:targetSubjectsOf ex:hasPrerequisite ;
    sh:sparql [
        sh:message "A unit reaches itself through one or more prerequisite edges." ;
        sh:select """
            PREFIX ex: <https://example.org/cits3005-prototype#>
            SELECT $this WHERE { $this ex:hasPrerequisite+ $this . }
        """
    ] .

ex:DegreeHasMajor a sh:NodeShape ;
    sh:targetClass ex:Degree ;
    sh:property [ sh:path ex:hasMajor ; sh:minCount 1 ;
                  sh:message "A degree needs at least one major in this graph." ] .

# Independently validate metadata; SHACL does not guarantee shape evaluation order.
# The sum filters non-numeric values, but these shapes still reject that data.
ex:CoreUnitMetadata a sh:NodeShape ;
    sh:targetObjectsOf ex:hasCoreUnit ;
    sh:property [ sh:path ex:level ; sh:datatype xsd:integer ;
                  sh:minCount 1 ; sh:maxCount 1 ; sh:minInclusive 1 ] ;
    sh:property [ sh:path ex:creditPoints ; sh:datatype xsd:integer ;
                  sh:minCount 1 ; sh:maxCount 1 ; sh:minInclusive 0 ] .

ex:LevelOneCreditLimit a sh:NodeShape ;
    sh:targetClass ex:Major ;
    sh:sparql [
        sh:message "Mandatory level 1 units exceed 48 credit points." ;
        sh:select """
            PREFIX ex: <https://example.org/cits3005-prototype#>
            SELECT $this WHERE {
                { SELECT $this (SUM(?credits) AS ?total) WHERE {
                    { SELECT DISTINCT $this ?unit ?credits WHERE {
                        $this ex:hasCoreUnit ?unit .
                        ?unit ex:level 1 ; ex:creditPoints ?credits .
                        FILTER(isNumeric(?credits))
                    } }
                } GROUP BY $this }
                FILTER(?total > 48)
            }
        """
    ] .
'''


def validate_graph(graph):
    shapes = Graph().parse(data=SHAPES, format="turtle")
    return validate(graph, shacl_graph=shapes, inference="none",
                    meta_shacl=True, abort_on_first=False)
