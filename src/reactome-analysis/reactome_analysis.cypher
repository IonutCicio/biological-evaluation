// MATCH - physical entities without a compartment.
MATCH (physicalEntity:PhysicalEntity)
WHERE NOT EXISTS { (physicalEntity)--(compartment:Compartment) }
RETURN physicalEntity
LIMIT 10

// COUNT - physical entities without a compartment.
MATCH (physicalEntity:PhysicalEntity)
WHERE NOT EXISTS { (physicalEntity)--(compartment:Compartment) }
RETURN COUNT(physicalEntity) // 19

// MATCH - physical entities with multiple compartments.
MATCH (physicalEntity:PhysicalEntity)--(c1:Compartment)
WHERE
  EXISTS {
    MATCH (physicalEntity)--(c2:Compartment)
    WHERE c2 <> c1
  }
RETURN n
LIMIT 10

// COUNT - physical entities with multiple compartments
MATCH (physicalEntity:PhysicalEntity)--(c1:Compartment)
WHERE
  EXISTS {
    MATCH (physicalEntity)--(c2:Compartment)
    WHERE c2 <> c1
  }
RETURN COUNT(n) // 14046

// MATCH - example physical entity with multiple compartments
MATCH path = (n {dbId: 10163238})--(c:Compartment)
RETURN path

// MATCH - labels of entities which have a stIdVersion but are NOT physical entities or events
MATCH (physicalEntity)
WHERE
  physicalEntity.stIdVersion <> '' AND
  NOT 'Event' IN labels(physicalEntity) AND
  NOT 'PhysicalEntity' IN labels(physicalEntity)
RETURN DISTINCT (labels(physicalEntity));
// ["DatabaseObject", "Deletable", "PositiveRegulation", "Regulation", "PositiveGeneExpressionRegulation"]
// ["DatabaseObject", "Deletable", "PositiveRegulation", "Regulation"]
// ["DatabaseObject", "Deletable", "Regulation", "NegativeRegulation", "NegativeGeneExpressionRegulation"]
// ["DatabaseObject", "Deletable", "Regulation", "NegativeRegulation"]
// ["DatabaseObject", "Deletable", "PositiveRegulation", "Regulation", "Requirement"]

// MATCH - max length of a "path" from pathway to reaction lik event
MATCH path = (:ReactionLikeEvent)<-[:hasEvent*12..]-(:Pathway)
RETURN path
LIMIT 1

// MATCH - top level pathways
MATCH (pathway:Pathway)
WHERE NOT EXISTS { (event:Event)-[:hasEvent]->(pathway) }
RETURN DISTINCT pathway.displayName

// Autophagy
// Cell Cycle
// Complex III assembly
// Cell-Cell communication
// Cellular responses to stimuli
// Transport of small molecules
// Chromatin organization
// Circadian clock
// Developmental Biology
// Digestion and absorption
// Disease
// DNA Repair
// DNA Replication
// Drug ADME
// Extracellular matrix organization
// Gene expression (Transcription)
// Hemostasis
// Immune System
// Metabolism
// Metabolism of proteins
// Metabolism of RNA
// Muscle contraction
// Mycobacterium tuberculosis biological processes
// Neuronal System
// Organelle biogenesis and maintenance
// Programmed Cell Death
// Protein localization
// Reproduction
// Sensory Perception
// Signal Transduction
// Vesicle-mediated transport
// DNA replication and repair
// Innate Immune System
// Drosophila signaling pathways

// MATCH - stoichiometry is ALWAYS defined  for inputs and outputs
MATCH path = (:PhysicalEntity)-[rel:input|output]-(:ReactionLikeEvent)
WHERE rel.stoichiometry IS NULL
RETURN path
LIMIT 1;

// MATCH - example of reverse reaction
MATCH path = (:ReactionLikeEvent)-[:reverseReaction]-(:ReactionLikeEvent)
RETURN path
LIMIT 1

// MATCH - transport "reaction" (catalysts etc...)
MATCH (catalystActivity:CatalystActivity)
WHERE catalystActivity.displayName CONTAINS 'transport'
RETURN catalystActivity
LIMIT 3

// MATCH  - example of transport
MATCH path = ({dbId: 10023106})-[:input|output]-(:PhysicalEntity)
RETURN path

// COUNT - relations number
MATCH ()-[relation]-()
RETURN COUNT(DISTINCT relation) // 11207998

// COUNT - relations with "stoichiometry" attribute
MATCH ()-[rel]-()
WHERE rel.stoichiometry >= 0
RETURN COUNT(DISTINCT rel) // 11207998

// COUNT - node with display name
MATCH (node)
WHERE node.displayName <> ''
RETURN COUNT(DISTINCT nod) // 2884994

// COUNT - nodes
MATCH (node)
RETURN COUNT(DISTINCT node) // 2886311

// COUNT - nodes with "isInDisease" attribute
MATCH (node)
WHERE node.isInDisease OR NOT node.isInDisease
RETURN COUNT(DISTINCT node) // 518301

// MATCH - reaction with catalyst
MATCH
  path1 =
    (reactionLikeEvent:ReactionLikeEvent)-[:catalystActivity]->
    (:CatalystActivity)-[:physicalEntity]->
    (:PhysicalEntity)<-[:hasComponent]-
    (complex:Complex),
  path2 = (reactionLikeEvent)-[:input|output*..4]-(complex)
RETURN path1, path2
LIMIT 1

// COUNT - catalysts which are not inputs of reactions
MATCH
  path =
    (reactionLikeEvent:ReactionLikeEvent)-[:catalystActivity]->
    (:CatalystActivity)-[:physicalEntity]->
    (physicalEntity:PhysicalEntity)
WHERE
  NOT EXISTS {
    MATCH (physicalEntity)<-[:input]-(reactionLikeEvent)
  }
RETURN COUNT(DISTINCT path)

// COUNT - catalysts which are inputs of reactions
MATCH
  path =
    (reactionLikeEvent:ReactionLikeEvent)-[:catalystActivity]->
    (:CatalystActivity)-[:physicalEntity]->
    (physicalEntity:PhysicalEntity)
WHERE
  EXISTS {
    MATCH (reactionLikeEvent)-[:input]->(physicalEntity)
  }
RETURN COUNT(DISTINCT path)

// COUNT - like above for regulators
MATCH
  path =
    (reactionLikeEvent:ReactionLikeEvent)-[:regulatedBy]->
    (:Regulation)-[:regulator]->
    (physicalEntity:PhysicalEntity)
WHERE
  NOT EXISTS {
    MATCH (reactionLikeEvent)-[:input]->(physicalEntity)
  }
RETURN COUNT(DISTINCT path) // ~ 1000

// COUNT - like above, for inputs
MATCH
  path =
    (n:PhysicalEntity)<-[:output]-
    (r:ReactionLikeEvent)-[:input]->
    (m:PhysicalEntity)
WHERE
  EXISTS {
    MATCH (r)-[:input]->(n)
  }
RETURN path
RETURN COUNT(DISTINCT path) // ~ 2932

// MATCH - pathways from gene
MATCH (n)-[:referenceDatabase]->(rd:ReferenceDatabase)
WHERE
  toLower(rd.displayName) = toLower("UniProt") AND
  (n.identifier = "P36897" OR
    n.variantIdentifier = "P36897" OR
    "P36897" IN n.geneName OR
    "P36897" IN n.name)
WITH DISTINCT n
MATCH
  (pe:PhysicalEntity)-
    [:referenceEntity|referenceSequence|crossReference|referenceGene*]->
  (n)
WITH DISTINCT pe
MATCH
  (rle:ReactionLikeEvent)-
    [:input
      |output
      |catalystActivity
      |physicalEntity
      |entityFunctionalStatus
      |diseaseEntity
      |regulatedBy
      |regulator
      |hasComponent
      |hasMember
      |hasCandidate
      |repeatedUnit*]->
  (pe)
WITH DISTINCT rle
MATCH (:Species {taxId: "9606"})<-[:species]-(p:Pathway)-[:hasEvent]->(rle)
RETURN DISTINCT p
ORDER BY p.stId

// TODO: surroundedBy
MATCH path = (n {dbId: 9626247})--(c:Compartment)
RETURN path
LIMIT 10
