# CITS3005 Knowledge Representation Project
## User Manual

**Students:**  
Jessica Lin – 24254044  
Bryant Gu – 24135184

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation and Running the Application](#2-installation-and-running-the-application)
3. [Knowledge Graph Schema](#3-knowledge-graph-schema)
4. [Ontology Rules and Constraints](#4-ontology-rules-and-constraints)
5. [SPARQL Queries](#5-sparql-queries)
6. [Managing Knowledge Graph Data](#6-managing-knowledge-graph-data)
7. [Modifying the Ontology](#7-modifying-the-ontology)
8. [Assumptions and Data Limitations](#8-assumptions-and-data-limitations)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Introduction

### 1.1 Purpose of the System

The system represents and manages the relationships between degrees, majors, units, locations, learning outcomes and prerequisites. It uses the UWA handbook dataset supplied with the project. The data is stored as a knowledge graph, so the links between the different types of information are explicit.

An OWL ontology adds reasoning, validation and querying on top of the knowledge graph. Users browse, search and query the handbook data through a command-line application.

### 1.2 System Overview

The system consists of the following components:

| Component | File(s) | Role |
|---|---|---|
| Source data | `data/degrees.json`, `data/majors.json`, `data/units.json`, `data/prerequisite_review.csv` | Handbook records and reviewed prerequisite links |
| Ontology | `ontology_prototype/ontology.py` | Defines the classes, properties and OWL rules (property chains, transitivity) |
| Graph builder | `build_graph.py` | Reads the data files, creates the individuals and relationships, and saves the result to `output/knowledge_graph.owl` |
| Constraints | `ontology_prototype/validation.py` | SHACL shapes that check the graph for constraint violations |
| SPARQL queries | `queries/query1.rq` – `queries/query4.rq` | The four predefined queries |
| Applications | `app.py` (interactive menu), `run_queries.py` (one-shot commands) | User interfaces to the knowledge graph |

The workflow is:

```
data/*.json + prerequisite_review.csv
            │  build_graph.py
            ▼
 output/knowledge_graph.owl   (asserted facts only)
            │  app.py / run_queries.py
            ▼
   Pellet reasoner (OWL rules)  ──►  inferred facts
            │
            ├─► browse / search
            ├─► SPARQL queries
            └─► SHACL validation
```

The saved OWL file holds only **asserted** facts. When it starts, the application loads this file and runs the **Pellet** reasoner, which adds the **inferred** relationships, for example the majors that a combined degree inherits from its component degrees. SHACL is then used to check that the reasoned graph satisfies the defined constraints.

The current knowledge graph contains:

| Item | Count |
|---|---|
| Degrees | 11 |
| Majors | 97 |
| Units | 887 |
| Learning outcomes (distinct) | 4,432 |
| Locations | 9 |
| Approved prerequisite links | 15 |
| Triples before reasoning | 24,854 |
| Triples after reasoning | 33,736 |

---

## 2. Installation and Running the Application

### 2.1 Requirements

| Requirement | Version / notes |
|---|---|
| Python | 3.9 or later (developed with 3.9.6, also tested with 3.13) |
| Java | Java 8 or later on the `PATH`; the Pellet reasoner bundled with Owlready2 runs on Java (tested with Temurin 21) |
| `owlready2` | 0.49 (do **not** use 0.51 — its bundled Jena caused `UnsupportedClassVersionError` in testing) |
| `rdflib` | 7.6.0 |
| `pyshacl` | 0.40.1 |
| `pytest` | 8.4.2 (only needed to run the tests) |

To check that Java is installed:

```bash
java -version
```

Install the Python packages in a virtual environment from the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r ontology_prototype/requirements.txt
```

### 2.2 Starting the Application

The repository already contains a generated `output/knowledge_graph.owl`. To regenerate it from the data files (required after any data change, see Section 6):

```bash
python build_graph.py
```

Start the interactive application from the project root:

```bash
python app.py
```

The application loads the knowledge graph and runs the Pellet reasoner. This takes a few seconds:

```
Loading knowledge graph...
Running Pellet reasoner...
Knowledge graph ready.
```

The reasoner prints lines starting with `* Owlready` while it runs. These are normal diagnostic messages, not errors.

If `output/knowledge_graph.owl` is missing, the application prints `Knowledge graph not found ... Run build_graph.py first.` and exits.

### 2.3 Main Menu

```
==========================================
 UWA KNOWLEDGE GRAPH BROWSER
==========================================
1. List degrees
2. View degree
3. List majors
4. View major
5. List units
6. View unit
7. Search knowledge graph
8. Run predefined SPARQL queries
9. Show inferred relationships
10. Validate knowledge graph
0. Exit
```

Type an option number and press Enter. An invalid option prints `Invalid option. Please try again.` and the menu is shown again. Choose `0` to exit.

| Option | Description | Section |
|---|---|---|
| 1, 3, 5 | List all degrees, majors or units by code | 2.4 |
| 2, 4, 6 | Show the details of one degree, major or unit | 2.4 |
| 7 | Keyword search across codes and learning outcomes | 2.5 |
| 8 | Open the SPARQL query sub-menu | 5 |
| 9 | Show examples of relationships inferred by the reasoner | 2.6 |
| 10 | Run SHACL validation on the reasoned graph | 2.7 |

### 2.4 Browsing Degrees, Majors and Units

**Listing (options 1, 3, 5).** These print every degree, major or unit code in alphabetical order, followed by a total (11 degrees, 97 majors, 887 units).

**Viewing details (options 2, 4, 6).** The application asks for a code. Codes are not case-sensitive (`mjd-anthr` works the same as `MJD-ANTHR`). If the code does not exist, or belongs to a different type (for example a unit code entered under *View degree*), the application prints `Degree not found.`, `Major not found.` or `Unit not found.`.

| Option | Prompt | Information shown |
|---|---|---|
| 2. View degree | `Enter degree code:` | Number of majors and the major list (including inferred majors), component degrees (combined degrees only), and degrees it inherits majors from (BH005 only) |
| 4. View major | `Enter major code:` | Number of core units, the core unit list, and the learning outcomes (direct major outcomes plus outcomes inferred from its core units) |
| 6. View unit | `Enter unit code:` | Level, credit points, prerequisites (direct and transitive), locations and learning outcomes |

Example, viewing a unit:

```
Enter unit code: LAWS3401

=== UNIT DETAILS ===
Code: LAWS3401
Level: 3
Credit Points: 6

Prerequisites:
  - LAWS1110
  - LAWS2223

Locations:
  - UWA (Perth)

Outcomes:
  - identify and analyse recent examples of emerging crime challenges
  - explain the nature and impact of technology on crime
  ...
```

Only `LAWS2223` is recorded as a direct prerequisite of LAWS3401. `LAWS1110` appears because the reasoner applies the transitive prerequisite rule (Section 4.1).

Example, viewing a combined degree:

```
Enter degree code: CB034

=== DEGREE DETAILS ===
Code: CB034
Number of majors: 57

Majors:
  - MJD-ANTHR
  ...

Component Degrees:
  - BH011
  - BP001
```

CB034 has no majors in the source data. All 57 are inferred from its component degrees BH011 (Engineering) and BP001 (Arts).

The degree codes in the dataset are:

| Code | Degree | Class |
|---|---|---|
| BP001 | Bachelor of Arts | StandardDegree |
| BP002 | Bachelor of Commerce | StandardDegree |
| BP004 | Bachelor of Science | StandardDegree |
| BP019 | Bachelor of Agricultural Science | StandardDegree |
| BH005 | Bachelor of Philosophy (Honours) | HonoursDegree |
| BH008 | Bachelor of Advanced Computer Science (Honours) | HonoursDegree |
| BH011 | Bachelor of Engineering (Honours) | HonoursDegree |
| CB004 | Bachelor of Engineering (Honours) / Bachelor of Science | CombinedDegree |
| CB006 | Bachelor of Engineering (Honours) / Bachelor of Commerce | CombinedDegree |
| CB010 | Bachelor of Agricultural Science / Bachelor of Commerce | CombinedDegree |
| CB034 | Bachelor of Engineering (Honours) / Bachelor of Arts | CombinedDegree |

### 2.5 Searching the Knowledge Graph

Option 7 asks for a keyword:

```
Enter a keyword, code, or outcome text: data
```

The search is case-insensitive and matches substrings. It returns:

- **degrees** whose code contains the keyword;
- **majors** whose code or any learning outcome contains the keyword;
- **units** whose code or any learning outcome contains the keyword.

Results are grouped by type and sorted by code:

```
=== SEARCH RESULTS ===
Major   MJD-ACCTG
Major   MJD-AGBUS
...
Unit    ...

Total matches: 207
```

Notes:
- The search matches **codes and outcome text only**. It does not match titles, so `Anthropology` will not find `MJD-ANTHR` by name. Use part of the code (e.g. `ANTH`) or a word from an outcome.
- Major outcomes include outcomes inferred from core units, so the major search covers more than the direct major outcomes. Query 4 (Section 5.5) searches direct major outcomes only.
- An empty keyword prints `Search term cannot be empty.`

### 2.6 Viewing Inferred Relationships

Option 9 shows how the reasoner extends the asserted data:

```
=== INFERRED RELATIONSHIPS ===

Combined Degrees:

CB034
  Component degrees: BH011, BP001
  Majors after reasoning: 57

CB006
  Component degrees: BH011, BP002
  Majors after reasoning: 17

CB010
  Component degrees: BP002, BP019
  Majors after reasoning: 9

CB004
  Component degrees: BH011, BP004
  Majors after reasoning: 37

BH005
  Inherits majors from: BH008, BH011, BP001, BP002, BP004, BP019
  Majors after reasoning: 97

Transitive prerequisite example:
  LAWS3401 prerequisites: LAWS1110, LAWS2223
  LAWS1110 is reachable through transitive reasoning.
```

None of the combined degrees or BH005 has a major in the source data. Every major listed for them comes from the property-chain rules in Section 4.3.

To see **every** relationship the reasoner adds for a particular resource, use the one-shot command in Section 2.8:

```bash
python run_queries.py inferred LAWS3401
```

### 2.7 Validating the Knowledge Graph

Option 10 runs SHACL validation (Section 4.5) on the graph **after** reasoning:

```
=== KNOWLEDGE GRAPH VALIDATION ===
Triples: 33736
SHACL conforms: True
No SHACL constraint violations were detected.
```

If a constraint is violated, the application prints `SHACL conforms: False` followed by the full SHACL report. The report lists each violation with its **Focus Node** (the offending degree, major or unit) and a **Message** that explains the rule that failed.

### 2.8 Command-Line Alternative (`run_queries.py`)

`run_queries.py` performs a single operation and exits, which suits scripting and testing.

| Command | Action |
|---|---|
| `python run_queries.py 1` | Run Query 1 (on the reasoned graph) |
| `python run_queries.py 2` | Run Query 2 (on the reasoned graph) |
| `python run_queries.py 3` | Run Query 3 |
| `python run_queries.py 4 "data analysis"` | Run Query 4 with a keyword (prompts for one if omitted) |
| `python run_queries.py browse LAWS2223` | Show every asserted property of a resource, with titles |
| `python run_queries.py inferred` | List every triple the reasoner adds |
| `python run_queries.py inferred CB034` | List the inferred triples that involve one resource |
| `python run_queries.py validate` | SHACL validation after reasoning |
| `python run_queries.py validate --asserted` | SHACL validation **before** reasoning |

Unlike `app.py`, `run_queries.py` prints resource titles next to codes, e.g. `Anthropology (MJD-ANTHR)`.

---

## 3. Knowledge Graph Schema

All entities use the namespace `https://example.org/cits3005-prototype#` (prefix `ex:`). Each individual is named by its handbook code, e.g. `ex:BP001`, `ex:MJD-ANTHR`, `ex:CITS3005`.

### 3.1 Main Classes

| Class | Parent | Description | Individuals |
|---|---|---|---|
| `Degree` | `Thing` | A UWA undergraduate course | 11 |
| `StandardDegree` | `Degree` | Bachelor's course (handbook study type "Bachelor's course") | 4 |
| `HonoursDegree` | `Degree` | Honours course ("Honour's courses") | 3 |
| `CombinedDegree` | `Degree` | Combined bachelor's course ("Combined bachelor's courses") | 4 |
| `Major` | `Thing` | A major that can be taken within a degree | 97 |
| `Unit` | `Thing` | A unit of study | 887 |
| `Outcome` | `Thing` | A learning outcome statement | 4,432 |
| `Location` | `Thing` | A place where a unit is offered | 9 |

**Outcome identifiers.** Each distinct outcome text becomes one `Outcome` individual named `Outcome_<SHA-256 hash of the text>`. The text itself is stored in `rdfs:label`. A unit and a major that share an identical outcome text therefore point to the same individual.

**Location identifiers.** Locations are named `Location_<name>` with non-alphanumeric characters replaced by `_`, e.g. `Location_UWA_Perth`, `Location_Albany`, `Location_Hong_Kong`. The original name is stored in `rdfs:label`. The nine locations are UWA (Perth), Albany, Indonesia, China, Germany, Japan, Hong Kong, Venice and Online.

### 3.2 Object Properties

| Property | Domain | Range | Characteristics | Meaning |
|---|---|---|---|---|
| `hasMajor` | `Degree` | `Major` | Property chains (Section 4.3) | The degree offers this major |
| `hasUnit` | `Major` | `Unit` | — | The unit belongs to the major |
| `hasCoreUnit` | `Major` | `Unit` | Sub-property of `hasUnit` | The unit is a core (compulsory) unit of the major |
| `hasPrerequisite` | `Unit` | `Unit` | **Transitive** | The first unit requires the second unit |
| `availableAt` | `Unit ∪ Major` | `Location` | — | Offered at this location |
| `hasOutcome` | `Unit ∪ Major` | `Outcome` | Property chain (Section 4.2) | Has this learning outcome |
| `involvesDegree` | `CombinedDegree` | `Degree` | — | A component degree of a combined degree |
| `inheritsMajorsFrom` | `Degree` | `Degree` | — | The degree can take majors from another degree (used for BH005) |

### 3.3 Data Properties

| Property | Domain | Range | Meaning |
|---|---|---|---|
| `level` | `Unit` | `xsd:integer` | Unit level (1–5 in the current data), from the `level` field of `units.json` |
| `creditPoints` | `Unit` | `xsd:integer` | Credit points (6 for most units; some have 0, 12 or 24), from the `credit` field of `units.json` |
| `rdfs:label` | `Outcome`, `Location` | string | Outcome text / location name |

### 3.4 Relationships Between Degree, Major and Unit

```
                   involvesDegree / inheritsMajorsFrom
                        ┌──────────┐
                        ▼          │
 ┌──────────┐  hasMajor  ┌───────┐  hasCoreUnit  ┌──────┐  availableAt  ┌──────────┐
 │  Degree  │ ─────────► │ Major │ ────────────► │ Unit │ ────────────► │ Location │
 └──────────┘            └───────┘  (⊑ hasUnit)  └──────┘               └──────────┘
                             │                     │  ▲
                  hasOutcome │          hasOutcome │  │ hasPrerequisite
                             ▼                     ▼  │ (transitive)
                         ┌─────────┐           ┌─────────┐
                         │ Outcome │           │ Outcome │
                         └─────────┘           └─────────┘
```

- A **degree** has one or more **majors** (`hasMajor`). Standard and honours degrees get their majors from `degrees.json`. Combined degrees and BH005 get theirs by inference.
- A **major** has **core units** (`hasCoreUnit`), taken from the `units` list in `majors.json`.
- A **unit** may have **prerequisite** units, **locations** and **learning outcomes**.
- **Majors** have their own outcomes from `majors.json`, and also inherit the outcomes of their core units through reasoning.

Asserted relationship counts in the current graph:

| Relationship | Count |
|---|---|
| Degree → Major (`hasMajor`) | 98 |
| Major → Core Unit (`hasCoreUnit`) | 1,511 |
| Unit → Outcome (`hasOutcome`) | 4,470 |
| Major → Outcome (`hasOutcome`) | 568 |
| Unit → Location (`availableAt`) | 1,014 |
| Unit → Prerequisite (`hasPrerequisite`) | 15 |
| Combined Degree → Component (`involvesDegree`) | 8 |
| BH005 → Source Degree (`inheritsMajorsFrom`) | 6 |

---

## 4. Ontology Rules and Constraints

The rules are OWL 2 axioms (transitivity, property chains, sub-properties) evaluated by the Pellet reasoner. They are not hand-written Python logic. Constraints are written in SHACL and checked with `pyshacl`.

### 4.1 Prerequisite Rules

**Rule (transitivity).** `hasPrerequisite` is declared a `TransitiveProperty`:

> If unit A has prerequisite B, and B has prerequisite C, then A has prerequisite C.

Example from the dataset:

| Fact | Type |
|---|---|
| LAWS3401 `hasPrerequisite` LAWS2223 | Asserted |
| LAWS2223 `hasPrerequisite` LAWS1110 | Asserted |
| LAWS3401 `hasPrerequisite` LAWS1110 | **Inferred** |

**Constraint (no cycles).** The SHACL shape `ex:NoPrerequisiteCycle` reports any unit that can reach itself through one or more prerequisite edges (`ex:hasPrerequisite+`), e.g. A → B → A. A cycle would make a unit impossible to enrol in.

### 4.2 Core Unit and Outcome Rules

**Rule (core units are units).** `hasCoreUnit` is a sub-property of `hasUnit`:

> If major M has core unit U, then M has unit U.

**Rule (outcome propagation).** `hasOutcome` has the property chain `hasCoreUnit ∘ hasOutcome`:

> If major M has core unit U, and U has outcome O, then M has outcome O.

Only **core** unit outcomes propagate. A unit linked by plain `hasUnit` does not pass its outcomes on. The reasoning is that a student is guaranteed to achieve a core unit's outcomes, but not those of an optional unit.

### 4.3 Degree and Major Rules

`hasMajor` has two property chains:

**Rule (combined degrees).** `involvesDegree ∘ hasMajor`:

> If combined degree C involves degree D, and D has major M, then C has major M.

| Combined degree | Component degrees | Majors after reasoning |
|---|---|---|
| CB004 | BH011, BP004 | 37 |
| CB006 | BH011, BP002 | 17 |
| CB010 | BP002, BP019 | 9 |
| CB034 | BH011, BP001 | 57 |

**Rule (Bachelor of Philosophy).** `inheritsMajorsFrom ∘ hasMajor`:

> If degree D inherits majors from degree E, and E has major M, then D has major M.

BH005 (Bachelor of Philosophy (Honours)) inherits from BP001, BP002, BP004, BP019, BH008 and BH011, so it can take all 97 majors.

### 4.4 Level 1 Credit Constraint

The SHACL shape `ex:LevelOneCreditLimit` checks that, for every major, the **total credit points of its level 1 core units do not exceed 48**. Each unit is counted once, even if it is linked more than once.

The constraint can only be checked if the unit data is correct, so the shape `ex:CoreUnitMetadata` also checks every unit used as a core unit:

| Property | Rule |
|---|---|
| `level` | exactly one value, `xsd:integer`, ≥ 1 |
| `creditPoints` | exactly one value, `xsd:integer`, ≥ 0 |

So a unit with missing, duplicated, text-valued or negative metadata is reported as a violation. It is not silently ignored in the credit total.

### 4.5 SHACL Validation

All shapes are defined in the `SHAPES` string in `ontology_prototype/validation.py`:

| Shape | Target | Checks |
|---|---|---|
| `ex:NoPrerequisiteCycle` | Units with prerequisites | No prerequisite cycles |
| `ex:DegreeHasMajor` | Every `Degree` | At least one `hasMajor` |
| `ex:CoreUnitMetadata` | Every object of `hasCoreUnit` | Valid `level` and `creditPoints` |
| `ex:LevelOneCreditLimit` | Every `Major` | Level 1 core credits ≤ 48 |

Validation runs with `inference="none"`, so pyshacl does not apply any inference of its own. The result therefore depends on whether the graph has been reasoned:

| Graph | Triples | Conforms | Violations |
|---|---|---|---|
| Before reasoning (`run_queries.py validate --asserted`) | 24,854 | **False** | 5 — BH005, CB004, CB006, CB010 and CB034 have no asserted majors |
| After reasoning (`app.py` option 10, `run_queries.py validate`) | 33,736 | **True** | 0 |

This difference is expected. It shows that the property-chain rules from Section 4.3 are needed for these five degrees to satisfy `ex:DegreeHasMajor`.

---

## 5. SPARQL Queries

### 5.1 Running Predefined Queries

Choose option **8** from the main menu to open the query sub-menu:

```
=== PREDEFINED SPARQL QUERIES ===
1. Foundational units
2. Average major options by degree type
3. Majors completable in Albany
4. Search majors by outcome
0. Back
```

The query text is stored in `queries/query1.rq` to `queries/query4.rq` and can be edited or run in any SPARQL tool. All queries use the prefix:

```sparql
PREFIX ex: <https://example.org/cits3005-prototype#>
```

| Query | Graph used | Why |
|---|---|---|
| 1 | Reasoned | Combined degrees only have majors after reasoning |
| 2 | Reasoned | Same reason as Query 1 |
| 3 | Reasoned | The result is the same with or without reasoning |
| 4 | Asserted (`knowledge_graph.owl`) | Searches **direct** major outcomes only. The reasoned graph would include outcomes inherited from core units |

### 5.2 Query 1 – Foundational Units

**Question:** Which units are core units of **every** major in a degree? These are units that every student in the degree must take, whichever major they choose.

```sparql
SELECT DISTINCT ?degree ?unit
WHERE {
    ?degree ex:hasMajor ?major .
    ?major ex:hasCoreUnit ?unit .
    FILTER NOT EXISTS {
        ?degree ex:hasMajor ?otherMajor .
        FILTER NOT EXISTS { ?otherMajor ex:hasCoreUnit ?unit . }
    }
}
```

The double `FILTER NOT EXISTS` expresses "for all": keep the unit only if no major of the degree lacks it.

**Result:** 44 degree–unit pairs.

| Degree | Foundational units |
|---|---|
| BH008 Advanced Computer Science (Honours) | 19 |
| BP019 Agricultural Science | 16 |
| BH011 Engineering (Honours) | 9 |

```
BP019      -> AGRI1001
BP019      -> BIOL1131
BP019      -> SCIE1104
...
Total degree-unit pairs: 44
```

Degrees with many unrelated majors (e.g. Arts, Science) have no unit shared by every major, so they do not appear. BP019 has a single major, so all of that major's core units count as foundational.

### 5.3 Query 2 – Average Number of Major Options

**Question:** On average, how many majors can a student choose from in each type of degree?

The inner sub-query counts the distinct majors per degree. The outer query averages those counts per degree class. BH005 is excluded because it inherits every major (97) and would distort the honours average.

**Result:**

```
CombinedDegree       30.00
HonoursDegree        6.50
StandardDegree       21.25
```

| Type | Degrees counted | Calculation |
|---|---|---|
| CombinedDegree | CB004, CB006, CB010, CB034 | (37 + 17 + 9 + 57) / 4 = 30.00 |
| HonoursDegree | BH008, BH011 | (4 + 9) / 2 = 6.50 |
| StandardDegree | BP001, BP002, BP004, BP019 | (48 + 8 + 28 + 1) / 4 = 21.25 |

### 5.4 Query 3 – Majors Available in Albany

**Question:** Which majors can be completed entirely at the Albany campus, i.e. **all** of their core units are offered in Albany?

```sparql
SELECT DISTINCT ?major
WHERE {
    ?major a ex:Major .
    ?major ex:hasCoreUnit ?anyCore .
    FILTER NOT EXISTS {
        ?major ex:hasCoreUnit ?unit .
        FILTER NOT EXISTS { ?unit ex:availableAt ex:Location_Albany . }
    }
}
ORDER BY ?major
```

The `?anyCore` pattern excludes majors with no core units, which would otherwise match vacuously.

**Result:** 5 majors.

| Code | Major |
|---|---|
| MJD-ANTHR | Anthropology |
| MJD-BOTNY | Botany |
| MJD-CONBI | Conservation Biology |
| MJD-ENVSC | Environmental Science |
| MJD-MBIOL | Marine Biology |

`build_graph.py` checks this result independently against the JSON data and prints the same five majors under `ALBANY MAJOR CANDIDATES`.

### 5.5 Query 4 – Search Majors by Learning Outcomes

**Question:** Which majors list a learning outcome that contains a given phrase?

The application asks for the phrase:

```
Enter outcome search text (e.g. data analysis): data analysis

Majors matching "data analysis":
MJD-AGBUS
MJD-AGTDM
MJD-BUSAN
MJD-GENET
MJD-PHYSC

Total matching majors: 5
```

The phrase is passed to the query as the variable `?keyword` (`initBindings`), not pasted into the query text, so special characters cannot break the query.

```sparql
FILTER(CONTAINS(LCASE(STR(?text)), LCASE(STR(?keyword))))
```

- The match is **case-insensitive** and works on **substrings**, so `prog` matches "programming".
- Leading and trailing spaces are removed; an empty phrase is rejected.
- Only the major's **own** outcomes from `majors.json` are searched (Section 5.1).

Example results:

| Phrase | Matching majors |
|---|---|
| `data analysis` | 5 |
| `programming` | 6 |
| `zzzz_no_match` | 0 (`No majors found for "zzzz_no_match".`) |

### 5.6 Interpreting Query Results

- Results are shown as **codes**. Look up the details with options 2, 4 and 6, or show titles with `python run_queries.py browse <code>`.
- `No results.` means the query ran successfully but nothing matched. It is not an error.
- If a query file is missing or has a syntax error, the application prints `Query file not found` or `SPARQL query failed:` followed by the parser message.
- The results reflect the current `knowledge_graph.owl`. After changing the data, rebuild the graph (Section 6.5) and run the queries again.
- The expected results of the current dataset are recorded in `query_verification.json` and checked automatically by `test_queries34.py`.

---

## 6. Managing Knowledge Graph Data

**Do not edit `output/knowledge_graph.owl` directly.** It is regenerated from the data files every time `build_graph.py` runs, so manual edits are lost. Change the files in `data/` and rebuild.

### 6.1 Data File Structure

**`data/degrees.json`** — an object keyed by degree code:

```json
"BP001": {
  "code": "BP001",
  "title": "Bachelor of Arts",
  "study_type": "Bachelor's course",
  "majors": ["MJD-ANTHR", "MJD-APHGY", "..."],
  ...
}
```

| Field | Used for |
|---|---|
| `study_type` | Degree class. Must be exactly `"Bachelor's course"`, `"Honour's courses"` or `"Combined bachelor's courses"` |
| `majors` | `hasMajor` links (every code must exist in `majors.json`) |
| `title` | Displayed by `run_queries.py` |

**`data/majors.json`** — an object keyed by major code:

| Field | Used for |
|---|---|
| `units` | `hasCoreUnit` links (every code must exist in `units.json`) |
| `outcomes` | Direct major `hasOutcome` links (list of strings) |
| `title` | Displayed by `build_graph.py` and `run_queries.py` |

**`data/units.json`** — an object keyed by unit code:

| Field | Used for |
|---|---|
| `level` | `level` (string or number, converted to integer) |
| `credit` | `creditPoints` (converted to integer) |
| `locations` | `availableAt` links, e.g. `["Albany", "UWA (Perth)"]` |
| `outcomes` | Unit `hasOutcome` links |
| `title` | Displayed by `run_queries.py` |

Other fields (`description`, `school`, `semesters`, `assessment`, ...) are kept for reference but are not loaded into the graph.

**`data/prerequisite_review.csv`** — candidate prerequisite links extracted from the handbook text:

| Column | Meaning |
|---|---|
| `unit` | The unit that has the requirement |
| `prerequisite` | The required unit |
| `description` | Original handbook prerequisite text |
| `needs_review` | `YES` if the text is ambiguous (contains "or", "any", "except", ...) |
| `warning_reasons` | Why the row was flagged |
| `approved` | `YES` to import the link; anything else is skipped |

**Hard-coded relationships in `build_graph.py`.** The degree inheritance links are not in the JSON files. They are defined in `link_degree_inheritance()`:

```python
combined_sources = {
    "CB034": ["BH011", "BP001"],
    "CB006": ["BH011", "BP002"],
    "CB010": ["BP019", "BP002"],
    "CB004": ["BH011", "BP004"]
}
philosophy_sources = ["BP001", "BP004", "BP002", "BP019", "BH008", "BH011"]
```

### 6.2 Adding Data

**Add a unit.** Add an entry to `units.json` with at least `level`, `credit`, `locations` and `outcomes`:

```json
"CITS9999": {
  "code": "CITS9999",
  "title": "Example Unit",
  "level": "3",
  "credit": "6",
  "locations": ["UWA (Perth)"],
  "outcomes": ["design and evaluate knowledge graphs"]
}
```

A new location name automatically creates a new `Location` individual.

**Add a major.** Add an entry to `majors.json`, listing only unit codes that exist in `units.json`:

```json
"MJD-EXAMP": {
  "code": "MJD-EXAMP",
  "title": "Example Major",
  "outcomes": ["..."],
  "units": ["CITS1401", "CITS9999"]
}
```

Then add `"MJD-EXAMP"` to the `majors` list of at least one degree in `degrees.json`.

**Add a degree.** Add an entry to `degrees.json` with a valid `study_type` and a `majors` list. For a **combined** degree, leave `majors` empty and add its component degrees to `combined_sources` in `build_graph.py`. To include it in option 9's output, also add its code to `combined_codes` in `show_inferred_relationships()` in `app.py`.

**Add a prerequisite.** Add a row to `prerequisite_review.csv` and set `approved` to `YES`:

```csv
CITS9999,CITS2005,Successful completion of CITS2005,NO,,YES
```

### 6.3 Updating Data

Edit the relevant field in the JSON file, e.g. change a unit's `locations`, add a code to a major's `units` list, or correct an outcome. Because outcomes are identified by a hash of their text, editing an outcome text creates a new `Outcome` individual. The old one disappears automatically if no unit or major uses it any more.

To approve or reject a candidate prerequisite, change the `approved` column to `YES` or clear it.

### 6.4 Removing Data

When removing an entity, also remove **every reference** to it. Otherwise `build_graph.py` stops with an error:

| Removing | Also remove references from |
|---|---|
| A unit | Every major's `units` list in `majors.json`, and every row of `prerequisite_review.csv` that names it (approved rows only) |
| A major | Every degree's `majors` list in `degrees.json` |
| A degree | `combined_sources` / `philosophy_sources` in `build_graph.py`, and `combined_codes` in `app.py` if listed |

Notes:
- `build_graph.py` runs a test on LAWS3401, LAWS2223 and LAWS1110 at the end of the build. If these units are removed, delete that test block (`PREREQUISITE TEST`) too.
- Query 2 excludes `ex:BH005` by name. Update `queries/query2.rq` if BH005 is removed or renamed.
- Removing a degree's last major will make SHACL report `A degree needs at least one major in this graph.`

### 6.5 Rebuilding the Knowledge Graph

After any change in `data/` or `build_graph.py`, run:

```bash
python build_graph.py
```

The script:

1. Loads the three JSON files and prints the record counts.
2. **Checks references.** It stops with `ValueError: Invalid JSON references` if a degree lists an unknown major or a major lists an unknown unit.
3. Creates the individuals and relationships and imports the approved prerequisites. It stops if a prerequisite row names an unknown unit or a unit that requires itself.
4. Prints a summary of individuals and relationships, the Albany major candidates and a prerequisite test.
5. Checks that no artificial test individuals (from `ontology.py`'s examples) leaked into the graph.
6. Saves `output/knowledge_graph.owl` (RDF/XML, about 2.5 MB).

Expected summary for the current data:

```
=== KNOWLEDGE GRAPH SUMMARY ===
Degree individuals: 11
Major individuals: 97
Unit individuals: 887
Outcome individuals: 4432
Location individuals: 9

=== RELATIONSHIPS ===
Degree-Major: 98
Major-Core Unit: 1511
...
Approved Unit-Prerequisite: 15
Unapproved candidates skipped: 172
```

Then restart `app.py` and run option 10 to confirm the new data satisfies all constraints.

---

## 7. Modifying the Ontology

The ontology is defined in `build_ontology()` in `ontology_prototype/ontology.py`. Every class, property and rule is declared inside the `with onto:` block. After any change, rebuild the graph (`python build_graph.py`) so that the OWL file contains the new schema.

### 7.1 Adding Classes and Properties

**New class** — subclass `Thing` or an existing class:

```python
class PostgraduateDegree(Degree): pass
```

**New object property** — give its domain and range:

```python
class hasCoordinator(ObjectProperty):
    domain = [Unit]
    range = [Staff]
```

**New data property:**

```python
class semesterOffered(DataProperty):
    domain = [Unit]
    range = [str]
```

A new class or property is just schema until data uses it. Fill it in `build_graph.py` by adding a function in the same style as `create_units()` or `link_units_locations()` and calling it from `main()`. Map a new `study_type` to its class in the `degree_classes` dictionary in `create_degrees()`.

### 7.2 Adding Ontology Rules

Rules are written as OWL axioms so that the Pellet reasoner applies them.

| Rule type | How to declare | Example |
|---|---|---|
| Transitive property | Add `TransitiveProperty` as a base class | `class hasPrerequisite(ObjectProperty, TransitiveProperty)` |
| Sub-property | Subclass the parent property | `class hasCoreUnit(hasUnit)` |
| Property chain | Assign `property_chain` | see below |
| Inverse property | Set `inverse_property` in a new property | `class isMajorOf(ObjectProperty): inverse_property = hasMajor` |

Property chain example. It reads "if X `involvesDegree` Y and Y `hasMajor` Z, then X `hasMajor` Z":

```python
hasMajor.property_chain = [
    PropertyChain([involvesDegree, hasMajor]),
    PropertyChain([inheritsMajorsFrom, hasMajor]),
]
```

To add another chain to an existing property, **append it to the list**. Assigning a new list on its own replaces the existing chains.

Reasoning runs in `reason()` with `infer_property_values=True`, which makes Pellet infer property values as well as class membership. Do not replace OWL rules with Python loops that add triples, because those would not be ontology reasoning.

### 7.3 Adding or Modifying Constraints

Constraints are SHACL shapes in Turtle syntax inside the `SHAPES` string in `ontology_prototype/validation.py`.

**Property constraint (cardinality / datatype)** — e.g. every unit must be offered in at least one location:

```turtle
ex:UnitHasLocation a sh:NodeShape ;
    sh:targetClass ex:Unit ;
    sh:property [ sh:path ex:availableAt ; sh:minCount 1 ;
                  sh:message "A unit must be offered at a location." ] .
```

**SPARQL constraint** — for rules that need a query. Each row the `SELECT` returns is one violation, and `$this` is the focus node:

```turtle
ex:MajorHasCoreUnit a sh:NodeShape ;
    sh:targetClass ex:Major ;
    sh:sparql [
        sh:message "A major has no core units." ;
        sh:select """
            PREFIX ex: <https://example.org/cits3005-prototype#>
            SELECT $this WHERE {
                FILTER NOT EXISTS { $this ex:hasCoreUnit ?u . }
            }
        """
    ] .
```

To change an existing limit, edit the shape. For example, change `FILTER(?total > 48)` in `ex:LevelOneCreditLimit`, and update its `sh:message` to match.

Shapes are validated with `meta_shacl=True`, so a syntax error in a shape is reported when validation runs.

### 7.4 Testing New Rules and Constraints

The project has two test suites, run with pytest from the project root:

```bash
python -m pytest -q -p no:cacheprovider test_queries34.py ontology_prototype
```

Expected output with the current code: `42 passed`.

| File | Tests |
|---|---|
| `ontology_prototype/test_reasoning.py` | Each rule infers the expected new triple, and no unintended triples are inferred |
| `ontology_prototype/test_validation.py` | Each SHACL shape passes valid graphs and fails invalid ones (cycles, missing majors, credit totals, bad metadata) |
| `test_queries34.py` | Queries 3 and 4 match results computed directly from the JSON files |

Further checks on the real knowledge graph, run as scripts:

```bash
python test_real_kg.py     # SHACL before/after reasoning on the full graph
python test_query1.py      # Query 1 on the reasoned graph
python test_query2.py      # Query 2 on the reasoned graph
python ontology_prototype/ontology.py   # rule demo on artificial examples
```

**Recommended way to test a new rule or constraint:**

1. Build a **small artificial graph** in a test that triggers the rule, as the example individuals in `build_ontology(include_examples=True)` do.
2. For a rule, check that the triple is **absent before** `reason()` and **present after** it.
3. For a constraint, write one graph that should pass and one that should fail, and check `conforms` and the reported shape. `test_validation.py` has a `check()` helper for this.
4. Run the full test suite, rebuild the graph, and run option 10 to make sure the real data still conforms.

Keep test individuals out of the real graph. `build_graph.py` calls `build_ontology(include_examples=False)` and checks that none of the example names are present.

---

## 8. Assumptions and Data Limitations

### 8.1 Core Unit Assumption

The handbook data does not separate compulsory units from option units within a major. The system **treats every unit in a major's `units` list as a core unit** (`hasCoreUnit`). As a result:

- Query 1 (foundational units) and Query 3 (Albany) may be stricter than reality. A major with an option unit not offered in Albany is excluded from Query 3 even if students could pick a different option.
- Outcome propagation (Section 4.2) adds the outcomes of all listed units to the major.
- The level 1 credit check (Section 4.4) counts all listed level 1 units.

The `hasUnit` / `hasCoreUnit` split in the ontology allows option units to be modelled separately if better data becomes available.

### 8.2 Prerequisite Data

Prerequisites in the handbook are free text (e.g. *"any Level 2 CLAN unit or ARCY unit (except ARCY2005)"*). They cannot all be represented as simple unit-to-unit links. Candidate links were extracted into `prerequisite_review.csv` (187 rows), and ambiguous ones were flagged with `needs_review` and `warning_reasons`.

- Only rows with `approved = YES` are imported: currently **15 links**. The other 172 are skipped.
- "Or" conditions, "any level X unit", credit-point requirements and corequisites are **not** modelled, so `hasPrerequisite` is a conservative subset of the real requirements.
- A unit with `Prerequisites: None recorded` may still have prerequisites in the handbook.
- To extend coverage, review more rows and set `approved` to `YES` (Section 6.2).

### 8.3 Albany Availability

- Location data comes from the `locations` field of each unit. Albany availability is assessed at the **unit level**. The `locations` text of degrees is not used.
- A major is "available in Albany" only if **all** of its (assumed core) units are offered there (Section 8.1). Semester, mode of delivery and year of offering are not considered.
- Only 129 of the 887 units list Albany, so few majors qualify (5 majors).

### 8.4 Other Limitations

- **Degree inheritance is hard-coded.** The component degrees of combined degrees and BH005's sources are set in `build_graph.py`, not read from the handbook data.
- **Dataset scope.** Only the 11 degrees, 97 majors and 887 units in the supplied dataset are covered. Units referenced in the handbook but missing from the dataset are not represented.
- **Outcome matching is textual.** Searches and Query 4 use substring matching, not meaning, so "analysing data" does not match "data analysis".
- **Identical outcome text is shared.** Two units with exactly the same outcome sentence point to the same `Outcome` individual.
- **The reasoner runs at every start-up.** `app.py` runs Pellet each time it starts, which takes a few seconds and requires Java.

---

## 9. Troubleshooting

| Problem | Cause / fix |
|---|---|
| `Knowledge graph not found ... Run build_graph.py first.` | `output/knowledge_graph.owl` is missing; run `python build_graph.py` |
| `ModuleNotFoundError: No module named 'owlready2'` | Activate the virtual environment and run `pip install -r ontology_prototype/requirements.txt` |
| Reasoner fails to start with an error mentioning `java` | Java is not installed or not on the `PATH`; install a JDK and check with `java -version` |
| `UnsupportedClassVersionError` | Wrong Owlready2 version; install `owlready2==0.49` |
| `ValueError: Invalid JSON references` | A degree or major lists a code that does not exist; check the `Missing majors` / `Missing units` counts printed before the error |
| `ValueError: Unknown unit` / `Unknown prerequisite` | An approved CSV row names a unit missing from `units.json` |
| `ValueError: Unknown degree type` | A degree's `study_type` is not one of the three accepted values |
| `KeyError` on a degree code during build | A degree referenced in `combined_sources` / `philosophy_sources` was removed from `degrees.json` |
| `SHACL conforms: False` | Read the Focus Node and Message in the report; see Section 4.5 |
| `* Owlready ...` lines in the output | Normal reasoner diagnostics, not errors |
