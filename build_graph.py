import json
import csv
import sys
import hashlib
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(BASE_DIR / "ontology_prototype"))
from ontology import build_ontology


# ==========================================
# 1. LOAD JSON FILES
# ==========================================

def load_json(filename):
    with open(BASE_DIR / "data" / filename, "r", encoding="utf-8") as f:
        return json.load(f)


# ==========================================
# 2. CREATE DEGREE INDIVIDUALS
# ==========================================

def create_degrees(onto, degrees):
    degree_classes = {
        "Bachelor's course": onto.StandardDegree,
        "Honour's courses": onto.HonoursDegree,
        "Combined bachelor's courses": onto.CombinedDegree
    }

    created = {}

    for code, data in degrees.items():
        study_type = data["study_type"]

        if study_type not in degree_classes:
            raise ValueError(f"Unknown degree type: {study_type}")

        created[code] = degree_classes[study_type](code)

    return created


# ==========================================
# 3. CREATE MAJOR INDIVIDUALS
# ==========================================

def create_majors(onto, majors):
    return {
        code: onto.Major(code)
        for code in majors
    }


# ==========================================
# 4. CREATE UNIT INDIVIDUALS
# ==========================================

def create_units(onto, units):
    created = {}

    for code, data in units.items():
        unit = onto.Unit(code)
        unit.level = [int(data["level"])]
        unit.creditPoints = [int(data["credit"])]

        created[code] = unit

    return created


# ==========================================
# 5. LINK DEGREES TO MAJORS
# ==========================================

def link_degrees_majors(degrees, created_degrees, created_majors):
    count = 0

    for degree_code, data in degrees.items():
        degree = created_degrees[degree_code]

        for major_code in data.get("majors", []):
            major = created_majors[major_code]

            if major not in degree.hasMajor:
                degree.hasMajor.append(major)
                count += 1

    return count


# ==========================================
# 6. LINK MAJORS TO CORE UNITS
# ==========================================

def link_majors_units(majors, created_majors, created_units):
    count = 0

    for major_code, data in majors.items():
        major = created_majors[major_code]

        for unit_code in data.get("units", []):
            unit = created_units[unit_code]

            if unit not in major.hasCoreUnit:
                major.hasCoreUnit.append(unit)
                count += 1

    return count


# ==========================================
# 7. CREATE AND LINK OUTCOMES
# ==========================================

def link_outcomes(onto, records, individuals, outcome_cache):
    count = 0

    for code, data in records.items():
        individual = individuals[code]

        for raw_text in data.get("outcomes", []):
            if not isinstance(raw_text, str):
                continue

            text = raw_text.strip()

            if not text:
                continue

            if text not in outcome_cache:
                identifier = hashlib.sha256(
                    text.encode("utf-8")
                ).hexdigest()

                outcome = onto.Outcome("Outcome_" + identifier)
                outcome.label.append(text)

                outcome_cache[text] = outcome

            outcome = outcome_cache[text]

            if outcome not in individual.hasOutcome:
                individual.hasOutcome.append(outcome)
                count += 1

    return count


# ==========================================
# 8. CREATE LOCATION INDIVIDUALS
# ==========================================

def create_locations(onto, units):
    created = {}
    location_names = set()

    for data in units.values():
        for location in data.get("locations", []):
            name = location.strip()

            if name:
                location_names.add(name)

    for name in sorted(location_names):
        safe_name = re.sub(
            r"[^A-Za-z0-9]+",
            "_",
            name
        ).strip("_")

        location = onto.Location("Location_" + safe_name)

        if name not in location.label:
            location.label.append(name)

        created[name] = location

    return created


# ==========================================
# 9. LINK UNITS TO LOCATIONS
# ==========================================

def link_units_locations(units, created_units, created_locations):
    count = 0

    for unit_code, data in units.items():
        unit = created_units[unit_code]

        for location_name in data.get("locations", []):
            name = location_name.strip()

            if not name:
                continue

            location = created_locations[name]

            if location not in unit.availableAt:
                unit.availableAt.append(location)
                count += 1

    return count


# ==========================================
# 10. CHECK ALBANY MAJOR CANDIDATES
# ==========================================

def find_albany_majors(majors, units):
    eligible = []

    for major_code, data in majors.items():
        core_units = set(data.get("units", []))

        if not core_units:
            continue

        all_in_albany = all(
            "Albany" in units[code].get("locations", [])
            for code in core_units
        )

        if all_in_albany:
            eligible.append(major_code)

    return eligible


# ==========================================
# 11. IMPORT APPROVED PREREQUISITES
# ==========================================

def link_approved_prerequisites(created_units):
    filename = BASE_DIR / "data" / "prerequisite_review.csv"

    count = 0
    skipped = 0

    with open(filename, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        required_columns = {
            "unit", "prerequisite", "approved"
        }

        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError("Missing columns in prerequisite CSV")

        for row in reader:

            if row["approved"].strip().upper() != "YES":
                skipped += 1
                continue

            unit_code = row["unit"].strip()
            prerequisite_code = row["prerequisite"].strip()

            if unit_code not in created_units:
                raise ValueError(f"Unknown unit: {unit_code}")

            if prerequisite_code not in created_units:
                raise ValueError(
                    f"Unknown prerequisite: {prerequisite_code}"
                )

            if unit_code == prerequisite_code:
                raise ValueError(
                    f"Self prerequisite: {unit_code}"
                )

            unit = created_units[unit_code]
            prerequisite = created_units[prerequisite_code]

            if prerequisite not in unit.hasPrerequisite:
                unit.hasPrerequisite.append(prerequisite)
                count += 1

    return count, skipped


def link_degree_inheritance(created_degrees):

    # Combined Degrees and their component Degrees
    combined_sources = {
        "CB034": ["BH011", "BP001"],
        "CB006": ["BH011", "BP002"],
        "CB010": ["BP019", "BP002"],
        "CB004": ["BH011", "BP004"]
    }

    combined_links = 0

    for combined_code, source_codes in combined_sources.items():
        combined = created_degrees[combined_code]

        for source_code in source_codes:
            source = created_degrees[source_code]

            if source not in combined.involvesDegree:
                combined.involvesDegree.append(source)
                combined_links += 1

    # Bachelor of Philosophy (Honours)
    philosophy = created_degrees["BH005"]

    philosophy_sources = [
        "BP001",
        "BP004",
        "BP002",
        "BP019",
        "BH008",
        "BH011"
    ]

    philosophy_links = 0

    for source_code in philosophy_sources:
        source = created_degrees[source_code]

        if source not in philosophy.inheritsMajorsFrom:
            philosophy.inheritsMajorsFrom.append(source)
            philosophy_links += 1

    return combined_links, philosophy_links


# ==========================================
# 12. MAIN PROGRAM
# ==========================================

def main():
    degrees = load_json("degrees.json")
    majors = load_json("majors.json")
    units = load_json("units.json")

    print("=== KNOWLEDGE GRAPH DATA LOADING ===")
    print("Degrees:", len(degrees))
    print("Majors:", len(majors))
    print("Units:", len(units))

    # Reference checks
    missing_majors = {
        code
        for data in degrees.values()
        for code in data.get("majors", [])
        if code not in majors
    }

    missing_units = {
        code
        for data in majors.values()
        for code in data.get("units", [])
        if code not in units
    }

    print("\n=== REFERENCE VALIDATION ===")
    print("Missing majors:", len(missing_majors))
    print("Missing units:", len(missing_units))

    if missing_majors or missing_units:
        raise ValueError("Invalid JSON references")

    world, onto = build_ontology(include_examples=False)

    try:
        # Individuals
        created_degrees = create_degrees(onto, degrees)
        created_majors = create_majors(onto, majors)
        created_units = create_units(onto, units)

        # Degree / Major / Unit relationships
        degree_major_links = link_degrees_majors(
            degrees, created_degrees, created_majors
        )
        
        combined_links, philosophy_links = link_degree_inheritance(
            created_degrees
            )

        print("\n=== DEGREE INHERITANCE RELATIONSHIPS ===")
        print("Combined Degree links:", combined_links)
        print("Philosophy inheritance links:", philosophy_links)

        for code in ["CB034", "CB006", "CB010", "CB004"]:
            degree = created_degrees[code]
            print(
                code,
                "involves:",
                [source.name for source in degree.involvesDegree]
            )

        print(
            "BH005 inherits from:",
            [
                source.name
                for source in created_degrees["BH005"].inheritsMajorsFrom
            ]
        )

        major_unit_links = link_majors_units(
            majors, created_majors, created_units
        )

        # Learning outcomes
        outcome_cache = {}

        unit_outcome_links = link_outcomes(
            onto, units, created_units, outcome_cache
        )

        major_outcome_links = link_outcomes(
            onto, majors, created_majors, outcome_cache
        )

        # Locations
        created_locations = create_locations(onto, units)

        unit_location_links = link_units_locations(
            units, created_units, created_locations
        )

        # Albany candidates
        albany_majors = find_albany_majors(majors, units)

        # Approved prerequisites
        prerequisite_links, skipped = link_approved_prerequisites(
            created_units
        )

        print("\n=== KNOWLEDGE GRAPH SUMMARY ===")
        print("Degree individuals:", len(created_degrees))
        print("Major individuals:", len(created_majors))
        print("Unit individuals:", len(created_units))
        print("Outcome individuals:", len(outcome_cache))
        print("Location individuals:", len(created_locations))

        print("\n=== RELATIONSHIPS ===")
        print("Degree-Major:", degree_major_links)
        print("Major-Core Unit:", major_unit_links)
        print("Unit-Outcome:", unit_outcome_links)
        print("Major-Outcome:", major_outcome_links)
        print("Unit-Location:", unit_location_links)
        print("Approved Unit-Prerequisite:", prerequisite_links)
        print("Unapproved candidates skipped:", skipped)

        print("\n=== ALBANY MAJOR CANDIDATES ===")
        print("Total candidates:", len(albany_majors))

        for code in albany_majors:
            print(code, "-", majors[code]["title"])

        # Check direct prerequisite relations
        print("\n=== PREREQUISITE TEST ===")

        laws3401 = created_units["LAWS3401"]
        laws2223 = created_units["LAWS2223"]
        laws1110 = created_units["LAWS1110"]

        print(
            "LAWS3401 -> LAWS2223:",
            laws2223 in laws3401.hasPrerequisite
        )

        print(
            "LAWS2223 -> LAWS1110:",
            laws1110 in laws2223.hasPrerequisite
        )

        print(
            "LAWS3401 -> LAWS1110 is a two-hop path:",
            laws2223 in laws3401.hasPrerequisite
            and laws1110 in laws2223.hasPrerequisite
        )

        print(
            "Note: Pellet reasoning has not been run."
        )
        
        print("\n=== TEST DATA ISOLATION ===")

        test_names = [
            "BachelorOfScience",
            "ScienceCommerceCombined",
            "BachelorOfPhilosophy",
            "ComputerScience",
            "ProgrammingSkills"
        ]

        for name in test_names:
            assert onto[name] is None, f"Unexpected test data: {name}"

        print("PASS: No artificial test individuals found")
        
        # ==========================================
        # EXPORT KNOWLEDGE GRAPH
        # ==========================================

        output_dir = BASE_DIR / "output"
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / "knowledge_graph.owl"

        onto.save(
            file=str(output_file),
            format="rdfxml"
        )

        print("\n=== KNOWLEDGE GRAPH EXPORT ===")
        print("Saved to:", output_file)
        print("File size:", output_file.stat().st_size, "bytes")


    finally:
        world.close()


if __name__ == "__main__":
    main()
