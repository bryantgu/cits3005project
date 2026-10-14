"""Compare the submitted queries with the handbook JSON source data."""

import json

import pytest
from rdflib import Graph, Namespace, RDF

from run_queries import BASE_DIR, search_majors

EX = Namespace("https://example.org/cits3005-prototype#")


@pytest.fixture(scope="module")
def data():
    graph = Graph().parse(BASE_DIR / "output" / "knowledge_graph.owl", format="xml")
    majors = json.loads((BASE_DIR / "majors.json").read_text(encoding="utf-8"))
    units = json.loads((BASE_DIR / "units.json").read_text(encoding="utf-8"))
    return graph, majors, units


def query_text(number):
    return (BASE_DIR / "queries" / f"query{number}.rq").read_text(encoding="utf-8")


@pytest.mark.parametrize("keyword", [
    "data analysis", "programming", "DATA ANALYSIS", "  PrOgRaMmInG  ",
    "zzzz_no_match_9f32", "", "   ",
])
def test_outcome_search_matches_source(data, keyword):
    graph, majors, _ = data
    rows = search_majors(graph, query_text(4), keyword)
    actual = {iri.rsplit("#", 1)[-1] for iri in rows}
    term = keyword.strip().lower()
    expected = {
        code for code, record in majors.items()
        if term and any(term in text.strip().lower() for text in record["outcomes"])
    }
    assert actual == expected
    assert len(rows) == len(actual)


def test_blank_keyword_skips_query():
    class NoQuery:
        def query(self, *args, **kwargs):
            raise AssertionError("Blank input must not execute SPARQL")

    assert search_majors(NoQuery(), query_text(4), "   ") == []


def test_albany_matches_source(data):
    graph, majors, units = data
    rows = list(graph.query(query_text(3)))
    actual = {str(row.major).rsplit("#", 1)[-1] for row in rows}
    expected = {
        code for code, record in majors.items()
        if record["units"] and all(
            "Albany" in units[unit].get("locations", []) for unit in record["units"]
        )
    }
    assert actual == expected
    assert len(rows) == len(actual)
    assert "MJD-ANTHR" in actual
    assert "MJD-APHGY" not in actual


def test_major_without_core_units_is_excluded(data):
    original, _, _ = data
    graph = Graph()
    for triple in original:
        graph.add(triple)
    major = EX["MJD-ANTHR"]
    graph.remove((major, EX.hasCoreUnit, None))
    assert (major, RDF.type, EX.Major) in graph
    assert major not in {row.major for row in graph.query(query_text(3))}
    assert list(original.objects(major, EX.hasCoreUnit))
