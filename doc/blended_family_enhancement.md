# Blended Family Enhancement

## Status: ✅ IMPLEMENTED (2026-01-03)

This document originally analyzed the need for enhanced blended family modeling. **Phase 1 (Step-Relationships) and Phase 2 (Half-Siblings) have been implemented.**

### Implementation Summary
- `:stepParentOf`, `:stepChildOf`, `:stepSiblingOf` - implemented via SPARQL materialization
- `:halfSiblingOf` - implemented via SPARQL materialization  
- Gender-specific variants for all blended family relationships
- Decision made: `:stepSiblingOf` is **NOT** a subproperty of `:siblingOf` (strict biological definition)
- Decision made: `:halfSiblingOf` **IS** a subproperty of `:siblingOf` (shares biological parent)

---

## Original Analysis (Historical)

## Overview

This document analyzes the need for enhanced blended family modeling with parent specification in the family ontology, following the successful implementation of adoptive relationships.

## Current State

### Existing Sibling Definition

```turtle
:siblingOf rdfs:subPropertyOf rel:siblingOf ;
    rdfs:comment """
        A person who shares at least one parent with another person.
        This relationship is symmetric and irreflexive.
    """@en ;
    owl:propertyChainAxiom ( 
        :childOf    # First find Parent
        :parentOf   # Then find Parent's children
    ) .
```
 
**What This Captures**
- ✅ **Full siblings** - Share both parents
- ✅ **Half-siblings** - Share one parent
- ✅ **Adoptive siblings** - Via :adoptiveParentOf subproperty

#### Identified Gaps

##### 1. Step-Relationships Not Modeled

**Scenario:** Blended Family

```turtle
# John and Mary marry, each bringing a child from previous relationship
ex:John :parentOf ex:Alice .      # Alice is John's biological child
ex:Mary :parentOf ex:Tom .        # Tom is Mary's biological child  
ex:John :spouseOf ex:Mary .       # They marry

# Problem: Alice and Tom are NOT siblings by current definition
# (they share NO parent), but they ARE step-siblings in reality
```

**Impact:** Cannot model step-siblings, step-parents, or step-children.

##### 2. Cannot Distinguish Half-Siblings from Full Siblings

**Scenario:** Sibling Query Ambiguity

```turtle
ex:Alice :siblingOf ex:Bob .
# Question: Do they share BOTH parents or just ONE?
# Current ontology cannot answer without additional queries
```

**Impact:**
- Cannot query "all full siblings" vs "all half-siblings"
- Loss of genealogical precision
- Inheritance law applications may require this distinction

##### 3. No Lineage Tracking (Maternal vs Paternal)
**Scenario:** Lineage-Specific Queries

```sparql
# Cannot express:
# - "All maternal siblings" (siblings through mother)
# - "All paternal grandparents" (father's parents)
# - "Maternal uncle" vs "Paternal uncle"
```

**Impact:**
- Cannot model lineage-specific traditions or inheritance
- Cannot distinguish maternal vs paternal extended family
- Genealogical research requires this information

#### Proposed Solutions

##### 1. Option 1: Step-Relationship Properties
Add properties for relationships through marriage (not biology/adoption):

```turtle
### step-parent
:stepParentOf a owl:ObjectProperty ;
    rdfs:label "step-parent of"@en ;
    rdfs:comment "A person who is married to the parent of another person, but is not their biological or adoptive parent."@en ;
    owl:propertyChainAxiom (
        :spouseOf
        :parentOf
    ) .

### step-child
:stepChildOf a owl:ObjectProperty ;
    owl:inverseOf :stepParentOf ;
    rdfs:label "step-child of"@en .

### step-sibling
:stepSiblingOf a owl:ObjectProperty ;
    rdfs:label "step-sibling of"@en ;
    rdfs:comment "A person who is the child of one's step-parent, but not one's biological or adoptive parent."@en ;
    owl:propertyChainAxiom (
        :childOf
        :spouseOf
        :parentOf
    ) .
```

**Pros:**
- ✅ Clearly distinguishes step-relationships from biological/adoptive
- ✅ Automatic inference through property chains
- ✅ Maintains separation from sibling relationships

**Cons:**
- ⚠️ Step-siblings won't be inferred as :siblingOf (may be desired)
- ⚠️ Need to decide: should step-siblings be a subproperty of :siblingOf?

##### 2. Option 2: Half-Sibling and Full-Sibling Distinction
```turtle
### full sibling
:fullSiblingOf rdfs:subPropertyOf :siblingOf ;
    rdfs:label "full sibling of"@en ;
    rdfs:comment "A person who shares both parents with another person."@en .

### half sibling  
:halfSiblingOf rdfs:subPropertyOf :siblingOf ;
    rdfs:label "half sibling of"@en ;
    rdfs:comment "A person who shares exactly one parent with another person."@en .
```

**Challenge:** Cannot express "shares BOTH parents" or "shares EXACTLY ONE parent" in OWL property chains directly. Would require:

- SWRL rules
- SPARQL CONSTRUCT queries
- Application logic

##### 3. Option 3: Lineage-Specific Properties

```turtle
### maternal lineage
:maternalGrandparentOf rdfs:subPropertyOf :grandparentOf ;
    owl:propertyChainAxiom (
        :motherOf
        :parentOf
    ) .

:paternalGrandparentOf rdfs:subPropertyOf :grandparentOf ;
    owl:propertyChainAxiom (
        :fatherOf
        :parentOf
    ) .

:maternalUncleOf rdfs:subPropertyOf :uncleAuntOf ;
    owl:propertyChainAxiom (
        :motherOf
        :brotherOf
    ) .

# ... etc.
```

**Pros:**
- ✅ Enables lineage-specific queries
- ✅ Important for genealogical accuracy

**Cons:**
- ⚠️ Requires gender-specific properties (:motherOf, :fatherOf)
- ⚠️ Doubles the number of extended family properties
- ⚠️ More complex ontology

#### Recommendations

##### 1. Priority 1: Step-Relationships (High Value, Low Complexity)

Implement Option 1 first:

- Add `:stepParentOf`, `:stepChildOf`, `:stepSiblingOf`
- Use property chains for automatic inference
- Decision needed: Should `:stepSiblingOf` be a subproperty of `:siblingOf`?
- Yes = Step-siblings are "siblings" in queries (inclusive definition)
- No = Keep step-siblings separate (strict biological/adoptive definition)

##### 2. Priority 2: Half-Sibling Distinction (Medium Value, Medium Complexity)

Implement Option 2 if genealogical precision is needed:

- Requires SWRL rules or SPARQL CONSTRUCT
- Best implemented as derived data, not in base ontology
- Consider documenting as a query pattern rather than ontology extension

##### 3. Priority 3: Lineage Tracking (Lower Priority)

Implement Option 3 only if:

- Genealogical applications require maternal/paternal distinction
- Cultural or legal requirements demand lineage tracking
- Willing to accept increased ontology complexity

#### Implementation Strategy

##### 1. Phase 1: Step-Relationships
1. Add `:stepParentOf` with property chain
2. Add `:stepChildOf` as inverse
3. Add `:stepSiblingOf` with property chain
4. **Decide and document:** Relationship between `:stepSiblingOf` and `:siblingOf`
5. Create test cases for blended families
6. Update documentation

##### 2. Phase 2: Query Patterns (Alternative to Option 2)
Document SPARQL query patterns for:
- Finding full siblings (share 2+ parents)
- Finding half-siblings (share exactly 1 parent)
- Distinguishing sibling types without modifying ontology

##### 3. Phase 3: Lineage Properties (If Needed)
Only if use case emerges:
- Add maternal/paternal variants of extended family
- Document trade-offs in complexity
- Create separate namespace for lineage properties?

#### Open Questions
1. Should step-siblings be considered "siblings"?
Legal context: Often yes
Biological context: No
Social context: Depends on family
- **Recommendation:** Make `:stepSiblingOf` a subproperty of `:siblingOf` to reflect social/legal reality

2. Do we need to model remarriage and multiple step-parents?
- Can a person have multiple step-parents over time?
- Requires temporal modeling (separate TODO item)

3. How to handle step-adoption?
- Step-parent who later legally adopts the child
- Transitions from `:stepParentOf` to `:adoptiveParentOf`
- May need temporal aspect or relationship change modeling

#### Related TODO Items
- [x] Support adoptive relationships (Completed - provides foundation)
- [x] Enhance blended family modeling with parent specification (Implemented 2026-01-03)
- [ ] Add temporal aspect modeling for relationship changes over time (Related to remarriage)
- [ ] Implement modeling of lifecycle events (Related to adoption/marriage timing)
- [ ] Add lineage-specific properties (maternal/paternal) - Phase 3 if needed

#### References
- Current ontology: `ontology/family-ontology.ttl`
- Test cases: `tests/data/family-sample-data.ttl`, `tests/data/family-anchors-data.ttl`
- Materialization scripts: `sparql/materialisation/materialize-stepParentOf-stepChildOf-GN.sparql`, etc.
- Related: Adoptive relationship implementation (completed)
---
Document Status: ✅ Phase 1 & 2 IMPLEMENTED

Last Updated: 2026-01-03

Remaining: Phase 3 (Lineage Properties) - implement only if use case emerges