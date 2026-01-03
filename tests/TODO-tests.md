# Family Ontology Test Coverage

This document tracks test coverage for all relationships defined in the family ontology.

## Core Family Relationships

### Core Gender-Neutral Relationships
- [x] `:spouseOf` - Spouse relationships (symmetric, irreflexive)
- [x] `:parentOf` - Parent relationships (inverse of childOf)
- [x] `:childOf` - Child relationships (inverse of parentOf)
- [ ] `:adoptiveParentOf` - Adoptive parent relationships (inverse of doptiveChildOf)
- [ ] `:adoptiveChildOf` - Adoptive child relationships (inverse of adoptiveParentOf)
- [x] `:siblingOf` - Sibling relationships (symmetric, irreflexive, materialized)

### Core Gender-Specific Relationships

#### Parent-Child
- [x] `:motherOf` - Mother relationships
- [x] `:fatherOf` - Father relationships
- [x] `:daughterOf` - Daughter relationships
- [x] `:sonOf` - Son relationships

#### Siblings
- [x] `:sisterOf` - Sister relationships
- [x] `:brotherOf` - Brother relationships

## Extended Family Relationships

### Extended Gender-Neutral Relationships

#### Grandparents
- [x] `:grandparentOf` - Grandparent relationships (property chain)
- [x] `:grandchildOf` - Grandchild relationships (inverse)

#### In-Law Relationships
- [x] `:parentInLawOf` - Parent-in-law relationships (property chain)
- [x] `:childInLawOf` - Child-in-law relationships (inverse)
- [x] `:siblingInLawOf` - Sibling-in-law relationships (property chain, symmetric)

#### Second Circle (Uncle/Aunt, Nibling, Cousin)
- [x] `:uncleAuntOf` - Uncle/aunt relationships (materialized)
- [x] `:niblingOf` - Nibling (niece/nephew) relationships (inverse)
- [x] `:cousinOf` - Cousin relationships (symmetric, irreflexive, materialized)

#### Great-Grandparents
- [ ] `:greatGrandparentOf` - Great-grandparent relationships (property chain)
- [ ] `:greatGrandchildOf` - Great-grandchild relationships (inverse)

### Extended Gender-Specific Relationships

#### Grandparent Relationships
- [x] `:grandmotherOf` - Grandmother relationships
- [x] `:grandfatherOf` - Grandfather relationships
- [x] `:granddaughterOf` - Granddaughter relationships
- [x] `:grandsonOf` - Grandson relationships

#### Uncle/Aunt Relationships
- [x] `:auntOf` - Aunt relationships
- [x] `:uncleOf` - Uncle relationships
- [x] `:nieceOf` - Niece relationships
- [x] `:nephewOf` - Nephew relationships

#### Cousin Relationships
- [x] `:cousinFemaleOf` - Female cousin relationships
- [x] `:cousinMaleOf` - Male cousin relationships

#### Great-Grandparent Relationships
- [ ] `:greatGrandmotherOf` - Great-grandmother relationships
- [ ] `:greatGrandfatherOf` - Great-grandfather relationships
- [ ] `:greatGranddaughterOf` - Great-granddaughter relationships
- [ ] `:greatGrandsonOf` - Great-grandson relationships

## Blended Family Relationships

### Core Gender-Neutral Blended Family Relationships
- [ ] `:stepParentOf` - Step-parent relationships
- [ ] `:stepChildOf` - Step-child relationships
- [ ] `:stepSiblingOf` - Step-sibling relationships (symmetric, irreflexive)
- [ ] `:halfSiblingOf` - Half-sibling relationships (symmetric, irreflexive)

### Core Gender-Specific Blended Family Relationships

#### Step Parents
- [ ] `:stepMotherOf` - Step-mother relationships
- [ ] `:stepFatherOf` - Step-father relationships

#### Step Children
- [ ] `:stepDaughterOf` - Step-daughter relationships
- [ ] `:stepSonOf` - Step-son relationships

#### Step Siblings
- [ ] `:stepBrotherOf` - Step-brother relationships
- [ ] `:stepSisterOf` - Step-sister relationships

#### Half Siblings
- [ ] `:halfSisterOf` - Half-sister relationships
- [ ] `:halfBrotherOf` - Half-brother relationships

## Additional Family Relationships

### Twin Relationships
- [x] `:twinOf` - Twin relationships (symmetric, irreflexive)

## Social Relationships

### Core Social Relationships
- [ ] `:friendOf` - Friend relationships
- [ ] `:closeFriendOf` - Close friend relationships

### Extended Gender-Neutral Social Relationships
- [ ] `:godParentOf` - Godparent relationships
- [ ] `:godChildOf` - Godchild relationships
- [ ] `:witnessOf` - Marriage witness relationships

### Extended Gender-Specific Social Relationships
- [ ] `:godmotherOf` - Godmother relationships
- [ ] `:godfatherOf` - Godfather relationships
- [ ] `:goddaughterOf` - Goddaughter relationships
- [ ] `:godsonOf` - Godson relationships

---

## Test Coverage Summary

**Total Relationships:** 61  
**Tested:** 29 ✅  
**Untested:** 32 ❌  
**Coverage:** 47.5%

### Priority for Next Tests

1. **High Priority** (Common relationships)
   - Adoptive parent/child relationships
   - Step-parent/child/sibling relationships
   - Half-sibling relationships
   - Great-grandparent relationships

2. **Medium Priority** (Social relationships)
   - Godparent relationships
   - Friend relationships

3. **Low Priority** (Less common)
   - Marriage witness relationships
