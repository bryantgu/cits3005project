import pytest
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, XSD
from ontology import BASE
from validation import validate_graph

EX = Namespace(BASE)
SH = Namespace("http://www.w3.org/ns/shacl#")


def check(graph, expected, shape=None, component=None):
    conforms, report, text = validate_graph(graph)
    assert bool(conforms) == expected, text
    if shape:
        assert (None, SH.sourceShape, EX[shape]) in report, text
    if component:
        assert (None, SH.sourceConstraintComponent, SH[component]) in report, text


@pytest.mark.parametrize("edges,expected", [
    ([("A", "B"), ("B", "C")], True),
    ([("A", "A")], False),
    ([("A", "B"), ("B", "A")], False),
    ([("A", "B"), ("B", "C"), ("C", "A")], False),
])
def test_cycles(edges, expected):
    graph = Graph()
    for a, b in edges:
        graph.add((EX[a], RDF.type, EX.Unit))
        graph.add((EX[b], RDF.type, EX.Unit))
        graph.add((EX[a], EX.hasPrerequisite, EX[b]))
    check(graph, expected, None if expected else "NoPrerequisiteCycle")


@pytest.mark.parametrize("has_major", [True, False])
def test_degree_minimum(has_major):
    graph = Graph()
    graph.add((EX.D, RDF.type, EX.Degree))
    if has_major:
        graph.add((EX.D, EX.hasMajor, EX.M))
        graph.add((EX.M, RDF.type, EX.Major))
    check(graph, has_major, component=None if has_major else "MinCountConstraintComponent")


def major_graph(credits, level=1):
    graph = Graph()
    graph.add((EX.M, RDF.type, EX.Major))
    for index, points in enumerate(credits):
        unit = EX[f"U{index}"]
        graph.add((EX.M, EX.hasCoreUnit, unit))
        graph.add((unit, RDF.type, EX.Unit))
        graph.add((unit, EX.level, Literal(level, datatype=XSD.integer)))
        graph.add((unit, EX.creditPoints, Literal(points, datatype=XSD.integer)))
    return graph


@pytest.mark.parametrize("credits,level,expected", [
    ([], 1, True), ([6] * 7, 1, True), ([6] * 8, 1, True),
    ([6] * 9, 1, False), ([6] * 9, 2, True),
])
def test_credit_totals(credits, level, expected):
    check(major_graph(credits, level), expected,
          None if expected else "LevelOneCreditLimit")


def test_elective_candidates_are_not_all_required():
    graph = major_graph([6] * 8)
    # Three candidate options linked only by hasUnit, not mandatory hasCoreUnit.
    for name in ("OptionA", "OptionB", "OptionC"):
        graph.add((EX.M, EX.hasUnit, EX[name]))
        graph.add((EX[name], EX.level, Literal(1)))
        graph.add((EX[name], EX.creditPoints, Literal(6)))
    check(graph, True)


@pytest.mark.parametrize("problem", ["missing", "multiple", "text", "negative", "missing_level"])
def test_bad_metadata_does_not_silently_pass(problem):
    graph = major_graph([6])
    if problem == "missing":
        graph.remove((EX.U0, EX.creditPoints, None))
    elif problem == "multiple":
        graph.add((EX.U0, EX.creditPoints, Literal(12)))
    elif problem == "text":
        graph.set((EX.U0, EX.creditPoints, Literal("six")))
    elif problem == "negative":
        graph.set((EX.U0, EX.creditPoints, Literal(-6)))
    else:
        graph.remove((EX.U0, EX.level, None))
    check(graph, False)
