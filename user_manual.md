# CITS3005 Knowledge Representation Project
## User Manual

**Students:**  
Jessica Lin – 24254044
Bryant Gu – 24135184

---

## 1. Introduction

### 1.1 Purpose of the System

The purpose of this system is to represent and manage the relationships between degrees, majors, units, locations, learning outcomes, and prerequisites. The system uses data from the provided UWA handbook dataset. The data is represented as a knowledge graph that clearly shows the relationships between different types of information. 

By using an ontology, the system supports reasoning, validation, and querying over the knowledge graph. Users can use the command-line application to browse, search, and query the handbook data.

### 1.2 System Overview

### 1.2 System Overview

The system uses degree, major, and unit data from the UWA handbook. The `build_graph.py` script reads these data files and creates a knowledge graph. The generated knowledge graph is saved as `knowledge_graph.owl`.

The ontology defines the classes, properties, and rules used in the knowledge graph. These rules allow the system to infer new relationships. SHACL is used to check whether the knowledge graph violates the defined constraints.

Users interact with the knowledge graph through the command-line application. The application allows users to search the knowledge graph, browse the handbook data, and run SPARQL queries. It also allows users to view inferred relationships and validate the knowledge graph.

---

## 2. Installation and Running the Application

### 2.1 Requirements

### 2.2 Starting the Application

### 2.3 Main Menu

### 2.4 Browsing Degrees, Majors and Units

### 2.5 Searching the Knowledge Graph

### 2.6 Viewing Inferred Relationships

### 2.7 Validating the Knowledge Graph

---

## 3. Knowledge Graph Schema

### 3.1 Main Classes

### 3.2 Object Properties

### 3.3 Data Properties

### 3.4 Relationships Between Degree, Major and Unit

---

## 4. Ontology Rules and Constraints

### 4.1 Prerequisite Rules

### 4.2 Core Unit and Outcome Rules

### 4.3 Degree and Major Rules

### 4.4 Level 1 Credit Constraint

### 4.5 SHACL Validation

---

## 5. SPARQL Queries

### 5.1 Running Predefined Queries

### 5.2 Query 1 – Foundational Units

### 5.3 Query 2 – Average Number of Major Options

### 5.4 Query 3 – Majors Available in Albany

### 5.5 Query 4 – Search Majors by Learning Outcomes

### 5.6 Interpreting Query Results

---

## 6. Managing Knowledge Graph Data

### 6.1 Data File Structure

### 6.2 Adding Data

### 6.3 Updating Data

### 6.4 Removing Data

### 6.5 Rebuilding the Knowledge Graph

---

## 7. Modifying the Ontology

### 7.1 Adding Classes and Properties

### 7.2 Adding Ontology Rules

### 7.3 Adding or Modifying Constraints

### 7.4 Testing New Rules and Constraints

---

## 8. Assumptions and Data Limitations

### 8.1 Core Unit Assumption

### 8.2 Prerequisite Data

### 8.3 Albany Availability