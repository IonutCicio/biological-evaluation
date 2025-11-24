CREATE
  (TEST_ENTITY:PhysicalEntity)<-[:input]-(TEST_REACTION:ReactionLikeEvent),
  (TEST_REACTION)<-[:hasEvent]-(TEST_PATHWAY:Pathway)
WITH *

MATCH (targetPathway:Pathway)
WHERE targetPathway IN [TEST_PATHWAY]
CALL
  apoc.path.subgraphNodes(
    targetPathway,
    {relationshipFilter: "hasEvent>", labelFilter: ">ReactionLikeEvent"}
  )
  YIELD node AS reactionOfInterest
WITH *, COLLECT(DISTINCT reactionOfInterest) AS reactionsOfInterest
MATCH (targetEntity)
WHERE targetEntity IN [TEST_ENTITY]
CALL
  apoc.path.subgraphNodes(
    targetEntity,
    {
      relationshipFilter: "<output|input>|catalystActivity>|physicalEntity>",
      labelFilter: ">ReactionLikeEvent"
    }
  )
  YIELD node
  WHERE node IN reactionsOfInterest
RETURN node.dbId;

CREATE
  (TEST_ENTITY:PhysicalEntity)<-[:input]-(TEST_REACTION:ReactionLikeEvent),
  (TEST_REACTION)<-[:hasEvent]-(TEST_PATHWAY:Pathway)
WITH *

MATCH (targetPathway:Pathway)
WHERE targetPathway IN [TEST_PATHWAY]
CALL
  apoc.path.subgraphNodes(
    targetPathway,
    {relationshipFilter: "hasEvent>", labelFilter: ">ReactionLikeEvent"}
  )
  YIELD node AS reactionOfInterest
WITH *, COLLECT(DISTINCT reactionOfInterest) AS reactionsOfInterest
MATCH (targetEntity)
WHERE targetEntity IN [TEST_ENTITY]
CALL
  apoc.path.subgraphNodes(
    targetEntity,
    {
      relationshipFilter: "<output|input>|catalystActivity>|physicalEntity>",
      labelFilter: ">ReactionLikeEvent"
    }
  )
  YIELD node
  WHERE node IN reactionsOfInterest
DETACH DELETE TEST_ENTITY, TEST_REACTION, TEST_PATHWAY
RETURN TEST_ENTITY;
// WITH node, testPath
// MATCH ()
// DELETE testPath
// WITH node

CREATE
  TEST_PATH =
    (TEST_ENTITY:PhysicalEntity)<-[:output]-
    (:ReactionLikeEvent)<-[:hasEvent]-
    (TEST_PATHWAY:Pathway)
WITH *

MATCH (targetPathway:Pathway)
WHERE targetPathway IN [TEST_PATHWAY]
CALL
  apoc.path.subgraphNodes(
    targetPathway,
    {relationshipFilter: "hasEvent>", labelFilter: ">ReactionLikeEvent"}
  )
  YIELD node
WITH COLLECT(node) AS reactionsOfInterest, TEST_PATH, TEST_ENTITY
MATCH (n)
WHERE n IN [TEST_ENTITY]
CALL
  apoc.path.subgraphNodes(
    n,
    {
      relationshipFilter: "<output|input>|catalystActivity>|physicalEntity>",
      labelFilter: ">ReactionLikeEvent"
    }
  )
  YIELD node
  WHERE node IN reactionsOfInterest
DELETE TEST_PATH
RETURN COUNT(DISTINCT node);
