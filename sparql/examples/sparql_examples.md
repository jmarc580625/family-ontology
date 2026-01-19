# SPARQL Query Examples

Examples of correct SPARQL patterns for the family ontology.
Note: In RDF triples, the subject performs the relationship to the object.
For "X's children", use `?child fam:childOf fam:X` (child is subject).

---

## 1. Super-property for all family relationships

#### Who is related to X? (using relatedTo super-property)
```sparql
SELECT ?person WHERE { fam:X fam:relatedTo ?person }
```
Note: relatedTo is a super-property of all family relationships, enabling broad "who is related" queries.

---

#### Find all family members of X (using property path)
```sparql
SELECT ?person ?relationship WHERE { 
  fam:X ?relationship ?person .
  ?relationship rdfs:subPropertyOf* fam:relatedTo .
}
```

---

## 2. core family relationships

### 2.1 core gender-neutral family relationships

#### Who is X's spouse?
```sparql
SELECT ?spouse WHERE { fam:X fam:spouseOf ?spouse }
```
Note: spouseOf is symmetric.

---

#### Who is X's civil partner?
```sparql
SELECT ?partner WHERE { fam:X fam:civilPartnerOf ?partner }
```
Note: civilPartnerOf is for legally recognized civil unions (PACS, civil partnerships).

---

#### Who is X's life partner?
```sparql
SELECT ?partner WHERE { fam:X fam:lifePartnerOf ?partner }
```
Note: lifePartnerOf is for long-term committed relationships without formal marriage.

---

#### List all partnerships (married, civil, or life partners)
```sparql
SELECT ?person1 ?person2 ?type WHERE {
  { ?person1 fam:spouseOf ?person2 . BIND("married" AS ?type) }
  UNION
  { ?person1 fam:civilPartnerOf ?person2 . BIND("civil partner" AS ?type) }
  UNION
  { ?person1 fam:lifePartnerOf ?person2 . BIND("life partner" AS ?type) }
}
```

---

#### Is X rngaged in any kind of partnership?
```sparql
ASK {
  { fam:X fam:spouseOf ?p }
  UNION
  { fam:X fam:civilPartnerOf ?p }
  UNION
  { fam:X fam:lifePartnerOf ?p }
}
```

---

#### Who are X's parents?
```sparql
SELECT ?parent WHERE { ?parent fam:parentOf fam:X }
```

---

#### Who are X's children?
```sparql
SELECT ?child WHERE { ?child fam:childOf fam:X }
``` 
Note: childOf has the child as subject, parent as object.

---

#### Who are X's adoptive parents?
```sparql
SELECT ?adoptiveparent WHERE { ?adoptiveparent fam:adoptiveParentOf fam:X }
```

---

#### Who are X's adoptive children?
```sparql
SELECT ?adoptivechild WHERE { ?adoptivechild fam:adoptiveChildOf fam:X }
```

---

#### Who are X's siblings?
```sparql
SELECT ?sibling WHERE { fam:X fam:siblingOf ?sibling }
```
Note: siblingOf is symmetric.

---

### 2.2 core gender-specific family relationships

#### Who is X's wife?
```sparql
SELECT ?wife WHERE { ?wife fam:wifeOf fam:X }
```

---

#### Who is X's husband?
```sparql
SELECT ?husband WHERE { ?husband fam:husbandOf fam:X }
```

---

#### Who is X's mother?
```sparql
SELECT ?mother WHERE { ?mother fam:motherOf fam:X }
```

---

#### Who is X's father?
```sparql
SELECT ?father WHERE { ?father fam:fatherOf fam:X }
```

---

#### Who are X's daughters?
```sparql
SELECT ?daughter WHERE { ?daughter fam:daughterOf fam:X }
```

---

#### Who are X's sons?
```sparql
SELECT ?son WHERE { ?son fam:sonOf fam:X }
```

---

#### Who are X's sons and daughters separately?
```sparql
SELECT ?son ?daughter WHERE {
  OPTIONAL { ?son fam:sonOf fam:X }
  OPTIONAL { ?daughter fam:daughterOf fam:X }
}
```

---

#### Who are X's sisters?
```sparql
SELECT ?sister WHERE { ?sister fam:sisterOf fam:X }
```

---

#### Who are X's brothers?
```sparql
SELECT ?brother WHERE { ?brother fam:brotherOf fam:X }
```

---

#### Who are X's brothers and sisters separately?
```sparql
SELECT ?brother ?sister WHERE {
  OPTIONAL { ?brother fam:brotherOf fam:X }
  OPTIONAL { ?sister fam:sisterOf fam:X }
}
```

---

## 3. extended family relationships

### 3.1 extended gender-neutral family relationships

#### Who are X's grandparents?
```sparql
SELECT ?grandparent WHERE { ?grandparent fam:grandparentOf fam:X }
```

---

#### Who are X's grandchildren?
```sparql
SELECT ?grandchild WHERE { ?grandchild fam:grandchildOf fam:X }
```

---

#### Who are X's uncles and aunts?
```sparql
SELECT ?uncleaunt WHERE { ?uncleaunt fam:uncleAuntOf fam:X }
```

---

#### Who are X's nieces and nephews?
```sparql
SELECT ?nibling WHERE { ?nibling fam:niblingOf fam:X }
```

---

#### Who are X's cousins?
```sparql
SELECT ?cousin WHERE { fam:X fam:cousinOf ?cousin }
```
Note: cousinOf is symmetric.

---

#### Who are X's great-grandparents?
```sparql
SELECT ?greatgrandparent WHERE { ?greatgrandparent fam:greatGrandparentOf fam:X }
```

---

#### Who are X's great-grandchildren?
```sparql
SELECT ?greatgrandchild WHERE { ?greatgrandchild fam:greatGrandchildOf fam:X }
```

---

#### Who are all of X's ancestors? (parents, grandparents, great-grandparents, etc.)
```sparql
SELECT ?ancestor WHERE { ?ancestor fam:ancestorOf fam:X }
```
Note: ancestorOf is transitive, so this returns all ancestors at any generational depth.

---

#### Who are all of X's descendants? (children, grandchildren, great-grandchildren, etc.)
```sparql
SELECT ?descendant WHERE { ?descendant fam:descendantOf fam:X }
```
Note: descendantOf is transitive, so this returns all descendants at any generational depth.

---

#### Is X an ancestor of Y?
```sparql
ASK { fam:X fam:ancestorOf fam:Y }
```

---

#### Find the lineage from X to Y (if Y is a descendant of X)
```sparql
SELECT ?ancestor WHERE {
  fam:Y fam:descendantOf ?ancestor .
  ?ancestor fam:descendantOf fam:X .
}
```

---

### 3.2 extended gender-specific family relationships

#### Who is X's grandmother?
```sparql
SELECT ?grandmother WHERE { ?grandmother fam:grandmotherOf fam:X }
```

---

#### Who is X's grandfather?
```sparql
SELECT ?grandfather WHERE { ?grandfather fam:grandfatherOf fam:X }
```

---

#### Who are X's granddaughters?
```sparql
SELECT ?granddaughter WHERE { ?granddaughter fam:granddaughterOf fam:X }
```

---

#### Who are X's grandsons?
```sparql
SELECT ?grandson WHERE { ?grandson fam:grandsonOf fam:X }
```

---

#### Who are X's aunts?
```sparql
SELECT ?aunt WHERE { ?aunt fam:auntOf fam:X }
```

---

#### Who are X's uncles?
```sparql
SELECT ?uncle WHERE { ?uncle fam:uncleOf fam:X }
```

---

#### Who are X's nieces?
```sparql
SELECT ?niece WHERE { ?niece fam:nieceOf fam:X }
```

---

#### Who are X's nephews?
```sparql
SELECT ?nephew WHERE { ?nephew fam:nephewOf fam:X }
```

---

#### Who are X's female cousins?
```sparql
SELECT ?cousin WHERE { ?cousin fam:cousinFemaleOf fam:X }
```

---

#### Who are X's male cousins?
```sparql
SELECT ?cousin WHERE { ?cousin fam:cousinMaleOf fam:X }
```

---

#### Who is X's great-grandmother?
```sparql
SELECT ?greatgrandmother WHERE { ?greatgrandmother fam:greatGrandmotherOf fam:X }
```

---

#### Who is X's great-grandfather?
```sparql
SELECT ?greatgrandfather WHERE { ?greatgrandfather fam:greatGrandfatherOf fam:X }
```

---

#### Who are X's great-granddaughters?
```sparql
SELECT ?greatgranddaughter WHERE { ?greatgranddaughter fam:greatGranddaughterOf fam:X }
```

---

#### Who are X's great-grandsons?
```sparql
SELECT ?greatgrandson WHERE { ?greatgrandson fam:greatGrandsonOf fam:X }
```

---

## 4. In-law family relationships

### 4.1 gender-neutral in-law family relationships

#### Who are X's parents-in-law?
```sparql
SELECT ?parentinlaw WHERE { ?parentinlaw fam:parentInLawOf fam:X }
```

---

#### Who are X's children-in-law?
```sparql
SELECT ?childinlaw WHERE { ?childinlaw fam:childInLawOf fam:X }
```

---

#### Who are X's siblings-in-law?
```sparql
SELECT ?siblinginlaw WHERE { fam:X fam:siblingInLawOf ?siblinginlaw }
```

---

### 4.2 gender-specific in-law family relationships

#### Who is X's mother-in-law?
```sparql
SELECT ?motherinlaw WHERE { ?motherinlaw fam:motherInLawOf fam:X }
```

---

#### Who is X's father-in-law?
```sparql
SELECT ?fatherinlaw WHERE { ?fatherinlaw fam:fatherInLawOf fam:X }
```

---

#### Who is X's daughter-in-law?
```sparql
SELECT ?daughterinlaw WHERE { ?daughterinlaw fam:daughterInLawOf fam:X }
```

---

#### Who is X's son-in-law?
```sparql
SELECT ?soninlaw WHERE { ?soninlaw fam:sonInLawOf fam:X }
```

---

#### Who is X's sister-in-law?
```sparql
SELECT ?sisterinlaw WHERE { ?sisterinlaw fam:sisterInLawOf fam:X }
```

---

#### Who is X's brother-in-law?
```sparql
SELECT ?brotherinlaw WHERE { ?brotherinlaw fam:brotherInLawOf fam:X }
```

---

## 5. Blended family relationships

### 5.1 gender-neutral blended family relationships

#### Who is X's stepparent?
```sparql
SELECT ?stepparent WHERE { ?stepparent fam:stepParentOf fam:X }
```

---

#### Who are X's stepchildren?
```sparql
SELECT ?stepchild WHERE { ?stepchild fam:stepChildOf fam:X }
```

---

#### Who are X's stepsiblings?
```sparql
SELECT ?stepsibling WHERE { fam:X fam:stepSiblingOf ?stepsibling }
```

---

#### Who are X's half-siblings?
```sparql
SELECT ?halfsibling WHERE { fam:X fam:halfSiblingOf ?halfsibling }
```

---

### 5.2 gender-specific blended family relationships

#### Who is X's stepmother?
```sparql
SELECT ?stepmother WHERE { ?stepmother fam:stepMotherOf fam:X }
```

---

#### Who is X's stepfather?
```sparql
SELECT ?stepfather WHERE { ?stepfather fam:stepFatherOf fam:X }
```

---

#### Who are X's stepdaughters?
```sparql
SELECT ?stepdaughter WHERE { ?stepdaughter fam:stepDaughterOf fam:X }
```

---

#### Who are X's stepsons?
```sparql
SELECT ?stepson WHERE { ?stepson fam:stepSonOf fam:X }
```

---

#### Who are X's stepsisters?
```sparql
SELECT ?stepsister WHERE { ?stepsister fam:stepSisterOf fam:X }
```

---

#### Who are X's stepbrothers?
```sparql
SELECT ?stepbrother WHERE { ?stepbrother fam:stepBrotherOf fam:X }
```

---

#### Who are X's half-sisters?
```sparql
SELECT ?halfsister WHERE { ?halfsister fam:halfSisterOf fam:X }
```

---

#### Who are X's half-brothers?
```sparql
SELECT ?halfbrother WHERE { ?halfbrother fam:halfBrotherOf fam:X }
```

---

## 6. Additional family relationships

### 6.1 twin relationship

#### Who is X's twin?
```sparql
SELECT ?twin WHERE { fam:X fam:twinOf ?twin }
```

---

#### Who are twins in the database?
```sparql
SELECT ?person1 ?person2 WHERE { ?person1 fam:twinOf ?person2 }
```

---

## 8. family-anchored social relationships

### 8.1 family-anchored gender-neutral social relationships

#### Who are X's godparents?
```sparql
SELECT ?godparent WHERE { ?godparent fam:godParentOf fam:X }
```

---

#### Who are X's godchildren?
```sparql
SELECT ?godchild WHERE { ?godchild fam:godChildOf fam:X }
```

---

#### Who was a witness at X's wedding?
```sparql
SELECT ?witness WHERE { ?witness fam:witnessOf fam:X }
```

---

### 8.2 family-anchored gender-specific social relationships

#### Who is X's godmother?
```sparql
SELECT ?godmother WHERE { ?godmother fam:godmotherOf fam:X }
```

---

#### Who is X's godfather?
```sparql
SELECT ?godfather WHERE { ?godfather fam:godfatherOf fam:X }
```

---

#### Who are X's goddaughters?
```sparql
SELECT ?goddaughter WHERE { ?goddaughter fam:goddaughterOf fam:X }
```

---

#### Who are X's godsons?
```sparql
SELECT ?godson WHERE { ?godson fam:godsonOf fam:X }
```

---

## 9. core social relationships

### 9.1 core gender-neutral social relationships

#### Who are X's friends?
```sparql
SELECT ?friend WHERE { fam:X fam:friendOf ?friend }
```
Note: friendOf is symmetric.

---

#### Who are X's close friends?
```sparql
SELECT ?friend WHERE { fam:X fam:closeFriendOf ?friend }
```
Note: closeFriendOf is a subproperty of friendOf.

---

## 10. Query Patterns

This section demonstrates common SPARQL query patterns that can be applied to any property in the ontology.

### 10.1 Counting Patterns

Use `COUNT()` to get the number of results instead of listing them.

#### Count children
```sparql
SELECT (COUNT(?child) AS ?count) WHERE { ?child fam:childOf fam:X }
```

---

#### Count with gender breakdown
```sparql
SELECT 
  (COUNT(DISTINCT ?son) AS ?sons) 
  (COUNT(DISTINCT ?daughter) AS ?daughters) 
WHERE {
  OPTIONAL { ?son fam:sonOf fam:X }
  OPTIONAL { ?daughter fam:daughterOf fam:X }
}
```

---

#### Count all persons by gender
```sparql
SELECT 
  (COUNT(DISTINCT ?male) AS ?males) 
  (COUNT(DISTINCT ?female) AS ?females) 
WHERE {
  OPTIONAL { ?male a fam:MalePerson }
  OPTIONAL { ?female a fam:FemalePerson }
}
```

---

### 10.2 Existence Patterns

Use `ASK` to check if a relationship exists (returns true/false).

#### Does X have children?
```sparql
ASK { ?child fam:childOf fam:X }
```

---

#### Is X married?
```sparql
ASK { fam:X fam:spouseOf ?spouse }
```

---

#### Are X and Y related?
```sparql
ASK { fam:X ?relationship fam:Y }
```

---

### 10.3 Listing Patterns

Query class membership to list all instances.

#### List all people
```sparql
SELECT ?person WHERE { ?person a fam:Person }
```

---

#### List all males
```sparql
SELECT ?male WHERE { ?male a fam:MalePerson }
```

---

#### List all females
```sparql
SELECT ?female WHERE { ?female a fam:FemalePerson }
```

---

### 10.4 Path and Meta-Query Patterns

Query relationships dynamically without specifying a particular property.

#### How is X related to Y?
```sparql
SELECT ?relationship WHERE { fam:X ?relationship fam:Y }
```

---

#### Find all relationships of X
```sparql
SELECT ?relationship ?person WHERE { fam:X ?relationship ?person }
```

---

### 10.5 Gender-Split Patterns

Combine gender-neutral properties with class membership to split results by gender.

#### List children with gender
```sparql
SELECT ?child ?gender WHERE {
  ?child fam:childOf fam:X .
  OPTIONAL { ?child a fam:MalePerson . BIND("male" AS ?gender) }
  OPTIONAL { ?child a fam:FemalePerson . BIND("female" AS ?gender) }
}
```

---

#### List siblings with gender
```sparql
SELECT ?sibling ?gender WHERE {
  fam:X fam:siblingOf ?sibling .
  OPTIONAL { ?sibling a fam:MalePerson . BIND("male" AS ?gender) }
  OPTIONAL { ?sibling a fam:FemalePerson . BIND("female" AS ?gender) }
}
```

