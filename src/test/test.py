from typing import LiteralString, TypeAlias

import neo4j

URI = "neo4j://localhost:7687"
AUTH = ("noe4j", "neo4j")
DB = "graph.db"

PhysicalEntityId: TypeAlias = int
PathwayId: TypeAlias = int
ReactionLikeEventId: TypeAlias = int

FIRST: int = 0


def query_transitive_closure(
    driver: neo4j.Driver,
    physical_entities: set[PhysicalEntityId],
    pathways: set[PathwayId],
) -> set[ReactionLikeEventId]:
    """Find the reactions in the transitive closure of a set of target physical entities within a set of target pathways."""
    records: list[neo4j.Record]
    records, _, _ = driver.execute_query(
        """
        MATCH (targetPathway:Pathway)
        WHERE ID(targetPathway) IN $target_pathways
        CALL
            apoc.path.subgraphNodes(
                targetPathway,
                {relationshipFilter: "hasEvent>", labelFilter: ">ReactionLikeEvent"}
            )
            YIELD node
        WITH COLLECT(DISTINCT node) AS reactionsOfInterest
        MATCH (targetEntity:PhysicalEntity)
        WHERE ID(targetEntity) IN $target_physical_entities
        CALL
            apoc.path.subgraphNodes(
                targetEntity,
                {
                    relationshipFilter: "<output|input>|catalystActivity>|physicalEntity>|<regulatedBy|regulator>",
                    labelFilter: ">ReactionLikeEvent"
                }
            )
            YIELD node
            WHERE node IN reactionsOfInterest
        RETURN ID(node) AS id;
        """,
        target_pathways=list(pathways),
        target_physical_entities=list(physical_entities),
    )

    return {int(row["id"]) for row in records}  # pyright: ignore[reportAny]


def query_reaction_like_events_for_test(
    driver: neo4j.Driver, test: LiteralString
) -> tuple[set[ReactionLikeEventId], neo4j.Record]:
    """Instantiate test, calculate transitive closure, return results and cleanup test instance."""
    records: list[neo4j.Record]
    records, _, _ = driver.execute_query(test)
    row: neo4j.Record = records[FIRST]

    reaction_like_events = query_transitive_closure(
        driver, {row["e1"]}, {row["p1"]}
    )

    _ = driver.execute_query(
        "MATCH (node) WHERE node IN $nodes_to_delete DELETE node",
        nodes_to_delete=list(row),
    )

    return (reaction_like_events, row)


def test_1() -> None:
    """Test if reactions that produce the target physical entities are in the transitive closure (directly)."""
    with neo4j.GraphDatabase.driver(uri=URI, auth=AUTH, database=DB) as driver:
        reaction_like_events, row = query_reaction_like_events_for_test(
            driver,
            """
            CREATE
                (p1:Pathway),
                (e1:PhysicalEntity),
                (r1:ReactionLikeEvent),
                (p1)-[:hasEvent]->(r1),
                (r1)-[:output]->(e1)
            RETURN ID(p1) AS p1, ID(e1) AS e1, ID(r1) AS r1
            """,
        )

    assert reaction_like_events == {row["r1"]}


def test_2() -> None:
    """Test if the transitive closure excludes reactions for which only the inputs are in the transitive closure."""
    with neo4j.GraphDatabase.driver(uri=URI, auth=AUTH, database=DB) as driver:
        reaction_like_events, _ = query_reaction_like_events_for_test(
            driver,
            """
            CREATE
                (p1:Pathway),
                (e1:PhysicalEntity),
                (r1:ReactionLikeEvent),
                (p1)-[:hasEvent]->(p1),
                (r1)-[:input]->(e1)
            RETURN ID(p1) AS p1, ID(e1) AS e1, ID(r1) AS r1
            """,
        )

    assert reaction_like_events == set()


def test_3() -> None:
    """Test if the transitive closure excludes reactions for which only the inputs are in the transitive closure (indirectly)."""
    with neo4j.GraphDatabase.driver(uri=URI, auth=AUTH, database=DB) as driver:
        reaction_like_events, row = query_reaction_like_events_for_test(
            driver,
            """
            CREATE
                (p1:Pathway),
                (e1:PhysicalEntity),
                (e2:PhysicalEntity),
                (r1:ReactionLikeEvent),
                (r2:ReactionLikeEvent),
                (p1)-[:hasEvent]->(r1),
                (p1)-[:hasEvent]->(r2),
                (r1)-[:output]->(e1),
                (r1)-[:output]->(e2),
                (r2)-[:input]->(e2)
            RETURN ID(p1) AS p1, ID(e1) AS e1, ID(e2) AS e2, ID(r1) AS r1, ID(r2) AS r2
            """,
        )

    assert reaction_like_events == {row["r1"]}


def test_4() -> None:
    """Test if the transitive includes enzymes."""
    with neo4j.GraphDatabase.driver(uri=URI, auth=AUTH, database=DB) as driver:
        reaction_like_events, row = query_reaction_like_events_for_test(
            driver,
            """
            CREATE
                (p1:Pathway),
                (e1:PhysicalEntity),
                (e2:PhysicalEntity),
                (r1:ReactionLikeEvent),
                (r2:ReactionLikeEvent),
                (r3:ReactionLikeEvent),
                (c1:CatalystActivity),
                (p1)-[:hasEvent]->(r1),
                (p1)-[:hasEvent]->(r2),
                (p1)-[:hasEvent]->(r3),
                (r1)-[:output]->(e1),
                (r2)-[:output]->(e2),
                (r3)-[:input]->(e2),
                (r1)-[:catalystActivity]->(c1),
                (c1)-[:physicalEntity]->(e2)
            RETURN ID(p1) AS p1, ID(e1) AS e1, ID(e2) AS e2, ID(r1) AS r1, ID(r2) AS r2, ID(r3) AS r3
            """,
        )

    assert reaction_like_events == {row["r1"], row["r2"]}


def test_5() -> None:
    """Test if the transitive closure excludes reactions for which only the enzymes are the inputs are in the transitive closure."""
    with neo4j.GraphDatabase.driver(uri=URI, auth=AUTH, database=DB) as driver:
        reaction_like_events, row = query_reaction_like_events_for_test(
            driver,
            """
            CREATE
                (p1:Pathway),
                (e1:PhysicalEntity),
                (e2:PhysicalEntity),
                (e3:PhysicalEntity),
                (r1:ReactionLikeEvent),
                (r2:ReactionLikeEvent),
                (c1:CatalystActivity),
                (p1)-[:hasEvent]->(r1),
                (p1)-[:hasEvent]->(r2),
                (r1)-[:output]->(e1),
                (r1)-[:input]->(e2),
                (r1)-[:input]->(e3),
                (r2)-[:input]->(e3),
                (r2)-[:catalystActivity]->(c1),
                (c1)-[:physicalEntity]->(e2)
            RETURN ID(p1) AS p1, ID(e1) AS e1, ID(e2) AS e2, ID(e3) AS e3, ID(r1) AS r1, ID(r2) AS r2
            """,
        )

    assert reaction_like_events == {row["r1"]}
