# Family Ontology Design Decisions

## Document Purpose

This document synthesizes the key design decisions and architectural choices made during the development of the family ontology. It serves as a reference for understanding the rationale behind the current implementation.

---

## 1. Relationship Hierarchy

### 1.1 Core Relationship Categories

The ontology organizes family relationships into distinct categories:

| Category | Section | Examples |
|----------|---------|----------|
| **0. Core** | Base relationships | `parentOf`, `childOf`, `spouseOf`, `siblingOf` |
| **1. Extended** | Multi-generational | `grandparentOf`, `uncleAuntOf`, `cousinOf` |
| **2. In-law** | Marriage-based | `parentInLawOf`, `siblingInLawOf` |
| **3. Blended** | Step/half relationships | `stepParentOf`, `halfSiblingOf` |
| **4. Additional** | Special cases | `twinOf` |
| **5. Disjointness** | Logical constraints | Property exclusions |
| **6. Social** | Non-biological | `godParentOf`, `friendOf` |

### 1.2 Gender-Neutral vs Gender-Specific

**Decision:** Every relationship has both gender-neutral and gender-specific variants.

- **Gender-neutral** (e.g., `:parentOf`) - Base property, inferred via OWL axioms
- **Gender-specific** (e.g., `:motherOf`, `:fatherOf`) - Subproperties, materialized via SPARQL

**Rationale:**
- Gender-neutral properties enable inclusive queries
- Gender-specific properties support traditional genealogical terminology
- Subproperty relationship ensures `?x :motherOf ?y` implies `?x :parentOf ?y`

---

## 2. Inference Strategy

### 2.1 OWL Axioms vs Materialization

**Decision:** Use OWL axioms where possible, SPARQL materialization where necessary.

| Mechanism | Use Case | Example |
|-----------|----------|---------|
| `owl:inverseOf` | Bidirectional relationships | `:childOf` inverse of `:parentOf` |
| `owl:propertyChainAxiom` | Transitive compositions | `:grandparentOf` = `:parentOf` → `:parentOf` |
| `owl:SymmetricProperty` | Mutual relationships | `:spouseOf`, `:siblingOf` |
| **SPARQL Materialization** | Complex logic, UNION, FILTER NOT EXISTS | `:siblingOf`, `:uncleAuntOf` |

### 2.2 Materialization Levels

**Decision:** Implement dependency-ordered materialization levels (0-4).

```
Level 0: No dependencies (base data)
Level 1: Depends on base properties (siblingOf, stepParentOf, halfSiblingOf)
Level 2: Depends on Level 1 (grandparent-GS, stepSibling, siblingInLaw)
Level 3: Depends on Level 2 (greatGrandparent-GS, cousin-GS)
Level 4: Depends on Level 3 (complex chains)
```

**Rationale:** Ensures correct execution order and prevents missing dependencies.

### 2.3 Materialization Metadata

**Decision:** Annotate properties with materialization metadata directly in the ontology.

```turtle
:siblingOf
    :materializationDependency :parentOf, :childOf ;
    :materializationScript "sparql/materialisation/materialize-siblingOf-GN.sparql" ;
    :materializationReason "Property chain creates duplicates; SPARQL ensures uniqueness" ;
    :materializationLevel 1 .
```

**Rationale:**
- Self-documenting ontology
- Enables automated materialization pipelines
- Clear dependency tracking

---

## 3. Blended Family Design Decisions

### 3.1 Step-Sibling vs Sibling Relationship

**Decision:** `:stepSiblingOf` is **NOT** a subproperty of `:siblingOf`.

```turtle
:stepSiblingOf owl:propertyDisjointWith :siblingOf .
```

**Rationale:**
- `:siblingOf` defined as "shares at least one parent" (biological/adoptive)
- Step-siblings share **no** biological parent
- Maintains strict genealogical definition
- Query for "all siblings including step" requires explicit UNION

**Alternative considered:** Making step-siblings a subproperty (rejected for genealogical precision).

### 3.2 Half-Sibling vs Sibling Relationship

**Decision:** `:halfSiblingOf` **IS** a subproperty of `:siblingOf`.

```turtle
:halfSiblingOf rdfs:subPropertyOf :siblingOf .
```

**Rationale:**
- Half-siblings share exactly one biological parent
- Satisfies the `:siblingOf` definition ("shares at least one parent")
- Query for `:siblingOf` automatically includes half-siblings
- Genealogically correct

### 3.3 Step-Parent Exclusion

**Decision:** A person cannot be both parent and step-parent of the same child.

```turtle
:stepParentOf owl:propertyDisjointWith :parentOf .
```

**Rationale:**
- Prevents logical contradictions
- Step-parent relationship implies non-biological parent
- Adoption transitions step-parent to adoptive-parent (different relationship)

---

## 4. Property Chain Limitations

### 4.1 OWL Property Chain Support

**Finding:** Not all triple stores support `owl:propertyChainAxiom`.

| Store | Property Chain Support |
|-------|----------------------|
| RDFLib + owlrl | ✅ Full support |
| GraphDB | ✅ Full support |
| Apache Jena Fuseki | ❌ Not supported |
| Virtuoso | ❌ Not supported |
| Blazegraph | ❌ Not supported |

**Decision:** Define property chains in OWL for compliant reasoners, provide materialization scripts as fallback.

### 4.2 Relationships Requiring Materialization

Some relationships cannot be expressed as pure OWL property chains:

| Relationship | Reason for Materialization |
|--------------|---------------------------|
| `:siblingOf` | Property chain creates self-loops; needs FILTER |
| `:uncleAuntOf` | Requires UNION (blood + by marriage) |
| `:siblingInLawOf` | Requires UNION (spouse's sibling + sibling's spouse) |
| `:halfSiblingOf` | Requires "exactly one shared parent" logic |
| `:stepSiblingOf` | Requires "no shared parent" exclusion |

---

## 5. Adoptive Relationships

### 5.1 Adoptive Parent as Subproperty

**Decision:** `:adoptiveParentOf` is a subproperty of `:parentOf`.

```turtle
:adoptiveParentOf rdfs:subPropertyOf :parentOf .
```

**Rationale:**
- Adoptive parents are legally and socially parents
- Query for `:parentOf` includes adoptive parents
- Enables "all parents" queries without explicit UNION
- Consistent with legal definitions

### 5.2 Adoptive Sibling Inference

**Consequence:** Adoptive siblings are automatically `:siblingOf` each other.

- `:siblingOf` defined via `:childOf` → `:parentOf` chain
- `:adoptiveChildOf` is subproperty of `:childOf`
- Therefore adoptive children of same parent are siblings

---

## 6. Social Relationships

### 6.1 Non-Biological Relationships

**Decision:** Include social/ceremonial relationships in separate category.

| Property | Type | Notes |
|----------|------|-------|
| `:godParentOf` | Direct property | Not inferred |
| `:godChildOf` | Inverse | `owl:inverseOf :godParentOf` |
| `:witnessOf` | Direct property | Marriage witness |
| `:friendOf` | Symmetric | `owl:SymmetricProperty` |
| `:closeFriendOf` | Subproperty | `rdfs:subPropertyOf :friendOf` |

**Rationale:**
- These relationships are socially significant
- Cannot be inferred from biological data
- Must be explicitly asserted

---

## 7. Testing Strategy

### 7.1 Backend Support

**Decision:** Support multiple backends with consistent test results.

| Backend | Purpose | Test Result |
|---------|---------|-------------|
| RDFLib + owlrl | Local development, CI/CD | 66/66 ✅ |
| GraphDB | Production deployment | 66/66 ✅ |

### 7.2 Test Organization

Tests organized by dependency level matching materialization levels:

- **Level 0:** Base relationships (no inference needed)
- **Level 1-3:** Inferred relationships (increasing complexity)
- **Level 4-7:** Gender-specific variants
- **Level 8:** Blended family relationships
- **Level 9:** Social relationships

---

## 8. Future Considerations

### 8.1 Not Implemented (Deferred)

| Feature | Status | Reason |
|---------|--------|--------|
| Lineage-specific properties (maternal/paternal) | Deferred | Doubles ontology complexity; implement only if use case emerges |
| Temporal modeling | Not started | Requires significant architecture changes |
| Full-sibling distinction | Query pattern only | Cannot express "shares BOTH parents" in OWL |

### 8.2 Open Questions

1. **Remarriage modeling:** Can a person have multiple step-parents over time?
2. **Step-adoption:** How to model transition from step-parent to adoptive parent?
3. **Temporal aspects:** When did relationships begin/end?

---

## Document History

| Date | Change |
|------|--------|
| 2026-01-03 | Blended family (Phase 1 & 2) implemented |
| 2026-01-06 | GraphDB integration completed (66/66 tests) |
| 2026-01-06 | Fuseki investigation concluded (property chains not supported) |
| 2026-01-06 | Design decisions document created |

---

## References

- Ontology: `ontology/family-ontology.ttl`
- Test suite: `tests/family-relationships.json`
- Materialization scripts: `sparql/materialisation/`
