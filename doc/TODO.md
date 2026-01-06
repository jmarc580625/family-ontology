# Family Ontology Future Enhancements

## Completed
- [x] Support adoptive relationships
- [x] Support gender-specific in-law relationships
- [x] Use class-based gender modeling instead of string literals (`:MalePerson`, `:FemalePerson`)
- [x] Implement blended family relationships (step-parent, step-child, step-sibling, half-sibling)
- [x] Add `rdfs:domain` and `rdfs:range` to base properties
- [x] Add ontology header with metadata (version, license, creator)
- [x] Document materialization dependencies via custom annotation properties
- [x] GraphDB backend integration (66/66 tests passing)
- [x] RDFLib + owlrl backend (66/66 tests passing)
- [x] Investigate Fuseki backend (concluded: property chains not supported)
- [x] Create design decisions document (`doc/design_decisions.md`)

## Pending
- [ ] Add cardinality restrictions on relationships
- [ ] Add temporal aspect modeling for relationship changes over time
- [ ] Implement modeling of lifecycle events

## Deferred
- [ ] Add lineage-specific properties (maternal/paternal grandparent, uncle, etc.)
  - *Reason: Doubles ontology complexity; implement only if use case emerges*
- [ ] Full-sibling distinction (`:fullSiblingOf`)
  - *Reason: Cannot express "shares BOTH parents" in OWL; use SPARQL query pattern instead*

## Open Questions
- Remarriage modeling: Can a person have multiple step-parents over time?
- Step-adoption: How to model transition from step-parent to adoptive parent?
- Temporal aspects: When did relationships begin/end?

## References
- Design decisions: `doc/design_decisions.md`

