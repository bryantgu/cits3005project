import pytest
from rdflib import URIRef
from rdflib.namespace import RDF
from ontology import BASE, build_ontology, snapshot, reason
from validation import validate_graph


def triple(subject, prop, obj):
    return tuple(URIRef(BASE + value) for value in (subject, prop, obj))


@pytest.fixture(scope="module")
def experiment():
    world, onto = build_ontology()
    # An ordinary unit's outcome must not propagate through hasUnit alone.
    ordinary = onto.Unit("OptionalUnit")
    other = onto.Outcome("OptionalSkills")
    onto.ComputerScience.hasUnit.append(ordinary)
    ordinary.hasOutcome.append(other)
    # Two-hop inheritance tests the recursive chain, not just one application.
    outer = onto.CombinedDegree("OuterCombined")
    outer.involvesDegree.append(onto.ScienceCommerceCombined)
    before = snapshot(world)
    reason(onto)
    after = snapshot(world)
    yield before, after
    world.close()


@pytest.mark.parametrize("subject,prop,obj", [
    ("ScienceCommerceCombined", "hasMajor", "ComputerScience"),
    ("BachelorOfPhilosophy", "hasMajor", "ComputerScience"),
    ("ComputerScience", "hasOutcome", "ProgrammingSkills"),
    ("CITS3005", "hasPrerequisite", "CITS1401"),
    ("OuterCombined", "hasMajor", "ComputerScience"),
    ("ComputerScience", "hasUnit", "CITS1401"),
])
def test_new_inferred_relationship(experiment, subject, prop, obj):
    before, after = experiment
    expected = triple(subject, prop, obj)
    assert expected not in before, "Test target must not already be asserted"
    assert expected in after, "Pellet result must contain the inferred triple"


def test_no_unintended_relationships(experiment):
    _, after = experiment
    assert triple("ComputerScience", "hasOutcome", "OptionalSkills") not in after
    assert triple("CITS1401", "hasPrerequisite", "CITS3005") not in after
    assert (URIRef(BASE + "CITS1401"), RDF.type, URIRef(BASE + "Major")) not in after
    assert (URIRef(BASE + "ComputerScience"), RDF.type, URIRef(BASE + "Unit")) not in after


def test_degree_validation_before_and_after_reasoning(experiment):
    before, after = experiment
    conforms, report, _ = validate_graph(before)
    assert not conforms
    from rdflib import Namespace
    sh = Namespace("http://www.w3.org/ns/shacl#")
    focus_nodes = set(report.objects(None, sh.focusNode))
    assert focus_nodes == {URIRef(BASE + name) for name in (
        "ScienceCommerceCombined", "BachelorOfPhilosophy", "OuterCombined")}
    conforms, _, text = validate_graph(after)
    assert conforms, text
