"""Browse the knowledge graph, run its queries, and inspect reasoning/validation."""

import argparse
import json
import sys
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, RDFS

BASE_DIR = Path(__file__).resolve().parent
EX = Namespace("https://example.org/cits3005-prototype#")


def load_graph():
    return Graph().parse(BASE_DIR / "output" / "knowledge_graph.owl", format="xml")


def reasoned_graph(with_before=False):
    from owlready2 import World

    sys.path.insert(0, str(BASE_DIR / "ontology_prototype"))
    from ontology import reason, snapshot

    world = World()
    try:
        onto = world.get_ontology((BASE_DIR / "output" / "knowledge_graph.owl").as_uri()).load()
        before = snapshot(world) if with_before else None
        reason(onto)
        after = snapshot(world)
        return (before, after) if with_before else after
    finally:
        world.close()


def load_titles():
    titles = {}
    for filename in ["degrees.json", "majors.json", "units.json"]:
        records = json.loads((BASE_DIR / "data" / filename).read_text(encoding="utf-8"))
        titles.update({code: record["title"] for code, record in records.items()})
    return titles


def display_term(term, titles):
    value = str(term)
    code = value.rsplit("#", 1)[-1]
    return f"{titles[code]} ({code})" if code in titles else code


def browse(graph, code, titles):
    subject = EX[code]
    pairs = list(graph.predicate_objects(subject))
    if not pairs:
        print(f"没有找到：{code}")
        return 1
    print(display_term(subject, titles))
    for predicate, obj in sorted(pairs, key=lambda pair: tuple(map(str, pair))):
        labels = sorted(str(label) for label in graph.objects(obj, RDFS.label))
        value = " / ".join(labels) if labels else display_term(obj, titles)
        print(f"- {display_term(predicate, {})}: {value}")
    return 0


def show_inferred(before, after, titles, code=None):
    rows = sorted(
        (triple for triple in after if triple not in before and (
            triple[1] == RDF.type or str(triple[1]).startswith(str(EX))
        ) and (code is None or EX[code] in (triple[0], triple[2]))),
        key=lambda triple: tuple(map(str, triple)),
    )
    print(f"新增类型及关系（{len(rows)}）：")
    for subject, predicate, obj in rows:
        labels = sorted(str(label) for label in after.objects(obj, RDFS.label))
        value = " / ".join(labels) if labels else display_term(obj, titles)
        print(f"- {display_term(subject, titles)} → {display_term(predicate, {})} → {value}")


def validate(graph):
    sys.path.insert(0, str(BASE_DIR / "ontology_prototype"))
    from validation import validate_graph

    conforms, _, report = validate_graph(graph)
    print(report)
    return 0 if conforms else 1


def search_majors(g, query, raw_keyword):
    keyword = raw_keyword.strip()
    if not keyword:
        return []
    return [
        str(row.major)
        for row in g.query(query, initBindings={"keyword": Literal(keyword)})
    ]


def main():
    parser = argparse.ArgumentParser(description="Browse, query, reason, or validate the knowledge graph.")
    parser.add_argument("query", choices=["1", "2", "3", "4", "browse", "inferred", "validate"])
    parser.add_argument("keyword", nargs="?", help="Query 4 keyword or browse/inferred resource code")
    parser.add_argument("--asserted", action="store_true", help="Validate before reasoning")
    args = parser.parse_args()

    if args.query not in ["4", "browse", "inferred"] and args.keyword is not None:
        parser.error("Only Query 4, browse, and inferred accept a keyword/code.")
    if args.asserted and args.query != "validate":
        parser.error("--asserted is only supported with validate.")
    if args.query == "browse" and not args.keyword:
        parser.error("browse requires a resource code, e.g. MJD-ANTHR.")

    if args.query == "4":
        keyword = args.keyword if args.keyword is not None else input("请输入关键词：")
        if not keyword.strip():
            print("关键词不能为空。")
            return 1

    g = load_graph()
    if args.query == "validate":
        return validate(g if args.asserted else reasoned_graph())

    titles = load_titles()
    if args.query == "browse":
        return browse(g, args.keyword.strip(), titles)
    if args.query == "inferred":
        code = args.keyword.strip() if args.keyword is not None else None
        if code is not None and not list(g.predicate_objects(EX[code])):
            print(f"没有找到：{code}")
            return 1
        before, after = reasoned_graph(with_before=True)
        show_inferred(before, after, titles, code)
        return 0
    if args.query in ["1", "2"]:
        g = reasoned_graph()

    query = (BASE_DIR / "queries" / f"query{args.query}.rq").read_text(encoding="utf-8")
    if args.query in ["1", "2"]:
        rows = list(g.query(query))
        if not rows:
            print("没有匹配的结果。")
            return 0
        print(f"查询结果（{len(rows)}）：")
        for row in sorted(rows, key=lambda row: tuple(map(str, row))):
            print("- " + " → ".join(display_term(term, titles) for term in row))
        return 0

    majors = (
        search_majors(g, query, keyword)
        if args.query == "4"
        else [str(row.major) for row in g.query(query)]
    )

    if not majors:
        print("没有匹配的 Major。")
        return 0

    print(f"匹配的 Majors（{len(majors)}）：")
    for iri in majors:
        print(f"- {display_term(iri, titles)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, EOFError) as error:
        print(f"无法运行：{error}", file=sys.stderr)
        raise SystemExit(1)
