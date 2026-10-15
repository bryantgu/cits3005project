from pathlib import Path
import sys

from owlready2 import World


# ============================================================
# Paths / imports
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
KG_FILE = BASE_DIR / "output" / "knowledge_graph.owl"
QUERY_DIR = BASE_DIR / "queries"

sys.path.insert(0, str(BASE_DIR / "ontology_prototype"))

from ontology import reason, snapshot
from validation import validate_graph


# ============================================================
# Load knowledge graph
# ============================================================

def load_knowledge_graph():
    """Load the OWL knowledge graph and run Pellet reasoning."""

    if not KG_FILE.exists():
        print(f"Knowledge graph not found: {KG_FILE}")
        print("Run build_graph.py first.")
        sys.exit(1)

    print("Loading knowledge graph...")

    world = World()

    try:
        onto = world.get_ontology(KG_FILE.as_uri()).load()

        print("Running Pellet reasoner...")
        reason(onto)

        print("Knowledge graph ready.\n")

        return world, onto

    except Exception:
        world.close()
        raise


def get_individual(onto, code):
    """Find an ontology individual by code."""

    code = code.strip()

    if not code:
        return None

    individual = onto[code]

    if individual is not None:
        return individual

    return onto[code.upper()]


def get_label(entity):
    """Return rdfs:label if available, otherwise entity name."""

    labels = list(entity.label)

    if labels:
        return str(labels[0])

    return entity.name


# ============================================================
# Browse
# ============================================================

def browse_degrees(onto):
    print("\n=== DEGREES ===")

    degrees = sorted(
        onto.Degree.instances(),
        key=lambda x: x.name
    )

    for degree in degrees:
        print(f"- {degree.name}")

    print(f"\nTotal: {len(degrees)}")


def browse_majors(onto):
    print("\n=== MAJORS ===")

    majors = sorted(
        onto.Major.instances(),
        key=lambda x: x.name
    )

    for major in majors:
        print(f"- {major.name}")

    print(f"\nTotal: {len(majors)}")


def browse_units(onto):
    print("\n=== UNITS ===")

    units = sorted(
        onto.Unit.instances(),
        key=lambda x: x.name
    )

    for unit in units:
        print(f"- {unit.name}")

    print(f"\nTotal: {len(units)}")


# ============================================================
# Degree details
# ============================================================

def show_degree(onto):
    code = input("\nEnter degree code: ").strip().upper()

    degree = get_individual(onto, code)

    degree_instances = set(onto.Degree.instances())

    if degree is None or degree not in degree_instances:
        print("Degree not found.")
        return

    print("\n=== DEGREE DETAILS ===")
    print("Code:", degree.name)

    majors = sorted(
        degree.hasMajor,
        key=lambda x: x.name
    )

    print("Number of majors:", len(majors))

    if majors:
        print("\nMajors:")

        for major in majors:
            print("  -", major.name)

    if hasattr(degree, "involvesDegree"):
        components = sorted(
            degree.involvesDegree,
            key=lambda x: x.name
        )

        if components:
            print("\nComponent Degrees:")

            for component in components:
                print("  -", component.name)

    if hasattr(degree, "inheritsMajorsFrom"):
        sources = sorted(
            degree.inheritsMajorsFrom,
            key=lambda x: x.name
        )

        if sources:
            print("\nInherits Majors From:")

            for source in sources:
                print("  -", source.name)


# ============================================================
# Major details
# ============================================================

def show_major(onto):
    code = input("\nEnter major code: ").strip().upper()

    major = get_individual(onto, code)

    major_instances = set(onto.Major.instances())

    if major is None or major not in major_instances:
        print("Major not found.")
        return

    print("\n=== MAJOR DETAILS ===")
    print("Code:", major.name)

    units = sorted(
        major.hasCoreUnit,
        key=lambda x: x.name
    )

    print("Number of core units:", len(units))

    if units:
        print("\nCore Units:")

        for unit in units:
            print("  -", unit.name)

    locations = sorted(
        major.availableAt,
        key=lambda x: x.name
    )

    if locations:
        print("\nLocations:")

        for location in locations:
            print("  -", get_label(location))

    outcomes = list(major.hasOutcome)

    if outcomes:
        print("\nOutcomes:")

        for outcome in outcomes:
            print("  -", get_label(outcome))


# ============================================================
# Unit details
# ============================================================

def show_unit(onto):
    code = input("\nEnter unit code: ").strip().upper()

    unit = get_individual(onto, code)

    unit_instances = set(onto.Unit.instances())

    if unit is None or unit not in unit_instances:
        print("Unit not found.")
        return

    print("\n=== UNIT DETAILS ===")
    print("Code:", unit.name)

    if unit.level:
        print("Level:", unit.level[0])

    if unit.creditPoints:
        print("Credit Points:", unit.creditPoints[0])

    prerequisites = sorted(
        unit.hasPrerequisite,
        key=lambda x: x.name
    )

    if prerequisites:
        print("\nPrerequisites:")

        for prerequisite in prerequisites:
            print("  -", prerequisite.name)

    else:
        print("\nPrerequisites: None recorded")

    locations = sorted(
        unit.availableAt,
        key=lambda x: x.name
    )

    if locations:
        print("\nLocations:")

        for location in locations:
            print("  -", get_label(location))

    outcomes = list(unit.hasOutcome)

    if outcomes:
        print("\nOutcomes:")

        for outcome in outcomes:
            print("  -", get_label(outcome))


# ============================================================
# Search
# ============================================================

def search_knowledge_graph(onto):
    keyword = input(
        "\nEnter a keyword, code, or outcome text: "
    ).strip().lower()

    if not keyword:
        print("Search term cannot be empty.")
        return

    results = set()

    # Degrees
    for degree in onto.Degree.instances():
        if keyword in degree.name.lower():
            results.add(("Degree", degree.name))

    # Majors
    for major in onto.Major.instances():
        matched = keyword in major.name.lower()

        if not matched:
            for outcome in major.hasOutcome:
                text = get_label(outcome).lower()

                if keyword in text:
                    matched = True
                    break

        if matched:
            results.add(("Major", major.name))

    # Units
    for unit in onto.Unit.instances():
        matched = keyword in unit.name.lower()

        if not matched:
            for outcome in unit.hasOutcome:
                text = get_label(outcome).lower()

                if keyword in text:
                    matched = True
                    break

        if matched:
            results.add(("Unit", unit.name))

    print("\n=== SEARCH RESULTS ===")

    if not results:
        print("No matching results.")
        return

    sorted_results = sorted(
        results,
        key=lambda x: (x[0], x[1])
    )

    for entity_type, code in sorted_results:
        print(f"{entity_type:<7} {code}")

    print(f"\nTotal matches: {len(sorted_results)}")


# ============================================================
# SPARQL queries
# ============================================================

def run_query_file(world, filename):
    query_file = QUERY_DIR / filename

    if not query_file.exists():
        print(f"Query file not found: {query_file}")
        return []

    query_text = query_file.read_text(
        encoding="utf-8"
    )

    graph = snapshot(world)

    try:
        return list(graph.query(query_text))

    except Exception as exc:
        print("\nSPARQL query failed:")
        print(exc)
        return []


def run_query1(world):
    print("\n=== QUERY 1: FOUNDATIONAL UNITS ===")

    rows = run_query_file(
        world,
        "query1.rq"
    )

    if not rows:
        print("No results.")
        return

    for degree, unit in rows:
        degree_name = str(degree).split("#")[-1]
        unit_name = str(unit).split("#")[-1]

        print(
            f"{degree_name:<10} -> {unit_name}"
        )

    print(
        f"\nTotal degree-unit pairs: {len(rows)}"
    )


def run_query2(world):
    print(
        "\n=== QUERY 2: "
        "AVERAGE MAJOR OPTIONS ==="
    )

    rows = run_query_file(
        world,
        "query2.rq"
    )

    if not rows:
        print("No results.")
        return

    for degree_type, average in rows:
        type_name = str(
            degree_type
        ).split("#")[-1]

        try:
            average_value = float(average)

            print(
                f"{type_name:<20} "
                f"{average_value:.2f}"
            )

        except (TypeError, ValueError):
            print(
                f"{type_name:<20} "
                f"{average}"
            )

    print(
        f"\nDegree types returned: {len(rows)}"
    )


def query_menu(world):
    while True:
        print(
            "\n=== PREDEFINED SPARQL QUERIES ==="
        )

        print("1. Foundational units")
        print(
            "2. Average major options "
            "by degree type"
        )
        print("0. Back")

        choice = input(
            "\nSelect a query: "
        ).strip()

        if choice == "1":
            run_query1(world)

        elif choice == "2":
            run_query2(world)

        elif choice == "0":
            return

        else:
            print(
                "Invalid option. "
                "Please try again."
            )


# ============================================================
# Reasoning
# ============================================================

def show_inferred_relationships(onto):
    print(
        "\n=== INFERRED RELATIONSHIPS ==="
    )

    print("\nCombined Degrees:")

    combined_codes = [
        "CB034",
        "CB006",
        "CB010",
        "CB004"
    ]

    for code in combined_codes:
        degree = onto[code]

        if degree is None:
            continue

        components = sorted(
            degree.involvesDegree,
            key=lambda x: x.name
        )

        majors = sorted(
            degree.hasMajor,
            key=lambda x: x.name
        )

        print(f"\n{code}")

        if components:
            print(
                "  Component degrees:",
                ", ".join(
                    component.name
                    for component in components
                )
            )

        print(
            "  Majors after reasoning:",
            len(majors)
        )

    # Bachelor of Philosophy
    philosophy = onto["BH005"]

    if philosophy is not None:
        sources = sorted(
            philosophy.inheritsMajorsFrom,
            key=lambda x: x.name
        )

        majors = sorted(
            philosophy.hasMajor,
            key=lambda x: x.name
        )

        print("\nBH005")

        print(
            "  Inherits majors from:",
            ", ".join(
                source.name
                for source in sources
            )
        )

        print(
            "  Majors after reasoning:",
            len(majors)
        )

    # Transitive prerequisite example
    print(
        "\nTransitive prerequisite example:"
    )

    laws3401 = onto["LAWS3401"]

    if laws3401 is not None:
        prerequisites = sorted(
            prerequisite.name
            for prerequisite
            in laws3401.hasPrerequisite
        )

        print(
            "  LAWS3401 prerequisites:",
            ", ".join(prerequisites)
        )

        if "LAWS1110" in prerequisites:
            print(
                "  LAWS1110 is reachable "
                "through transitive reasoning."
            )


# ============================================================
# SHACL validation
# ============================================================

def validate_knowledge_graph(world):
    print(
        "\n=== KNOWLEDGE GRAPH VALIDATION ==="
    )

    graph = snapshot(world)

    try:
        conforms, _, report_text = (
            validate_graph(graph)
        )

    except Exception as exc:
        print("Validation failed:")
        print(exc)
        return

    print("Triples:", len(graph))
    print("SHACL conforms:", conforms)

    if conforms:
        print(
            "No SHACL constraint violations "
            "were detected."
        )

    else:
        print("\nValidation report:")
        print(report_text)


# ============================================================
# Main menu
# ============================================================

def print_menu():
    print("\n" + "=" * 42)
    print(" UWA KNOWLEDGE GRAPH BROWSER")
    print("=" * 42)

    print("1. List degrees")
    print("2. View degree")
    print("3. List majors")
    print("4. View major")
    print("5. List units")
    print("6. View unit")
    print("7. Search knowledge graph")
    print("8. Run predefined SPARQL queries")
    print("9. Show inferred relationships")
    print("10. Validate knowledge graph")
    print("0. Exit")


def main():
    world, onto = load_knowledge_graph()

    try:
        while True:
            print_menu()

            choice = input(
                "\nSelect an option: "
            ).strip()

            if choice == "1":
                browse_degrees(onto)

            elif choice == "2":
                show_degree(onto)

            elif choice == "3":
                browse_majors(onto)

            elif choice == "4":
                show_major(onto)

            elif choice == "5":
                browse_units(onto)

            elif choice == "6":
                show_unit(onto)

            elif choice == "7":
                search_knowledge_graph(onto)

            elif choice == "8":
                query_menu(world)

            elif choice == "9":
                show_inferred_relationships(onto)

            elif choice == "10":
                validate_knowledge_graph(world)

            elif choice == "0":
                print("\nGoodbye.")
                break

            else:
                print(
                    "Invalid option. "
                    "Please try again."
                )

    finally:
        world.close()


if __name__ == "__main__":
    main()