
import sys
from pathlib import Path

from owlready2 import World
from rdflib import URIRef

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "ontology_prototype"))

from ontology import BASE, reason, snapshot
from validation import validate_graph


def main():
    path = BASE_DIR / "output" / "knowledge_graph.owl"

    if not path.exists():
        raise FileNotFoundError(path)

    world = World()

    try:
        onto = world.get_ontology(path.as_uri()).load()

        print("=== BEFORE REASONING ===", flush=True)

        before = snapshot(world)
        conforms_before, _, _ = validate_graph(before)

        print("Triples:", len(before), flush=True)
        print("SHACL conforms:", conforms_before, flush=True)

        for code in ["CB034", "CB006", "CB010", "CB004", "BH005"]:
            degree = onto[code]
            print(
                code,
                "Majors:",
                len(degree.hasMajor),
                flush=True
            )

        print("\n=== RUNNING PELLET REASONER ===", flush=True)

        reason(onto)

        print("\n=== AFTER REASONING ===", flush=True)

        after = snapshot(world)
        conforms_after, _, report_text = validate_graph(after)

        print("Triples:", len(after))
        print("New triples:", len(after) - len(before))

        for code in ["CB034", "CB006", "CB010", "CB004", "BH005"]:
            degree = onto[code]

            print(
                code,
                "Majors:",
                len(degree.hasMajor)
            )

        print("\n=== SPECIFIC INFERENCE TEST ===")

        inferred = (
            URIRef(BASE + "CB034"),
            URIRef(BASE + "hasMajor"),
            URIRef(BASE + "MJD-ANTHR")
        )

        print("Asserted before:", inferred in before)
        print("Present after reasoning:", inferred in after)

        print("\n=== SHACL AFTER REASONING ===")
        print("Conforms:", conforms_after)

        if not conforms_after:
            print(report_text[:3000])

    finally:
        world.close()


if __name__ == "__main__":
    main()
