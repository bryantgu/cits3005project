from pathlib import Path
from owlready2 import World
import sys

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "ontology_prototype"))

from ontology import reason, snapshot


def main():
    kg_file = BASE_DIR / "output" / "knowledge_graph.owl"
    query_file = BASE_DIR / "queries" / "query1.rq"

    world = World()

    try:
        onto = world.get_ontology(kg_file.as_uri()).load()

        print("=== RUNNING REASONER ===")
        reason(onto)

        graph = snapshot(world)

        print("\n=== RUNNING QUERY 1 ===")

        query = query_file.read_text(encoding="utf-8")
        results = graph.query(query)

        rows = list(results)

        print("Results:", len(rows))

        for degree, unit in rows:
            print(
                degree.split("#")[-1],
                "->",
                unit.split("#")[-1]
            )

    finally:
        world.close()


if __name__ == "__main__":
    main()