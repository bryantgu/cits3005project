"""Artificial experiments only: these individuals are not handbook facts."""
from owlready2 import (
    World, Thing, ObjectProperty, DataProperty, TransitiveProperty,
    PropertyChain, sync_reasoner_pellet,
)

BASE = "https://example.org/cits3005-prototype#"


def build_ontology():
    # A World is an isolated store: previous experiments cannot leak into this one.
    world = World()
    onto = world.get_ontology(BASE)
    with onto:
        class Degree(Thing): pass
        class StandardDegree(Degree): pass
        class CombinedDegree(Degree): pass
        class HonoursDegree(Degree): pass
        class Major(Thing): pass
        class Unit(Thing): pass
        class Location(Thing): pass
        class Outcome(Thing): pass

        class hasMajor(ObjectProperty):
            domain = [Degree]
            range = [Major]

        class hasUnit(ObjectProperty):
            domain = [Major]
            range = [Unit]

        class hasCoreUnit(hasUnit):
            domain = [Major]
            range = [Unit]

        class hasPrerequisite(ObjectProperty, TransitiveProperty):
            domain = [Unit]
            range = [Unit]

        class availableAt(ObjectProperty):
            domain = [Unit | Major]  # One union, not two intersecting domains.
            range = [Location]

        class hasOutcome(ObjectProperty):
            domain = [Unit | Major]
            range = [Outcome]

        class involvesDegree(ObjectProperty):
            domain = [CombinedDegree]
            range = [Degree]

        class inheritsMajorsFrom(ObjectProperty):
            domain = [Degree]
            range = [Degree]

        # Approved experiment-only metadata; no handbook data is assumed.
        class level(DataProperty):
            domain = [Unit]
            range = [int]

        class creditPoints(DataProperty):
            domain = [Unit]
            range = [int]

        # A --involvesDegree--> B --hasMajor--> C implies A --hasMajor--> C.
        hasMajor.property_chain = [
            PropertyChain([involvesDegree, hasMajor]),
            PropertyChain([inheritsMajorsFrom, hasMajor]),
        ]
        # Only core-unit outcomes propagate to the major.
        hasOutcome.property_chain = [PropertyChain([hasCoreUnit, hasOutcome])]

        science = StandardDegree("BachelorOfScience")
        combined = CombinedDegree("ScienceCommerceCombined")
        philosophy = Degree("BachelorOfPhilosophy")
        major = Major("ComputerScience")
        first = Unit("CITS1401")
        second = Unit("CITS2005")
        third = Unit("CITS3005")
        outcome = Outcome("ProgrammingSkills")

        science.hasMajor.append(major)
        combined.involvesDegree.append(science)
        philosophy.inheritsMajorsFrom.append(science)
        major.hasCoreUnit.append(first)
        first.hasOutcome.append(outcome)
        third.hasPrerequisite.append(second)
        second.hasPrerequisite.append(first)
        first.level = [1]
        first.creditPoints = [6]
    return world, onto


def snapshot(world):
    """Copy triples so later reasoning cannot mutate our asserted-data baseline."""
    from rdflib import Graph
    graph = Graph()
    for triple in world.as_rdflib_graph():
        graph.add(triple)
    return graph


def reason(onto):
    # Actual Java/Pellet reasoning; never substitute hand-written Python rules.
    sync_reasoner_pellet([onto], infer_property_values=True, debug=1)


if __name__ == "__main__":
    from rdflib import URIRef
    world, onto = build_ontology()
    before = snapshot(world)
    reason(onto)
    after = snapshot(world)
    for subject, prop, obj in [
        ("ScienceCommerceCombined", "hasMajor", "ComputerScience"),
        ("BachelorOfPhilosophy", "hasMajor", "ComputerScience"),
        ("ComputerScience", "hasOutcome", "ProgrammingSkills"),
        ("CITS3005", "hasPrerequisite", "CITS1401"),
    ]:
        triple = tuple(URIRef(BASE + value) for value in (subject, prop, obj))
        print(f"{subject} {prop} {obj}: asserted={triple in before}, after={triple in after}")
        assert triple not in before and triple in after
    world.close()
