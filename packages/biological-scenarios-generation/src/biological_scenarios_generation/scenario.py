import itertools
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import reduce
from operator import attrgetter
from typing import Any, LiteralString, TypeAlias

import libsbml
import neo4j

from biological_scenarios_generation.core import IntGTZ, PartialOrder
from biological_scenarios_generation.model import BiologicalModel, SId
from biological_scenarios_generation.reactome import (
    Category,
    Compartment,
    MathML,
    Metadata,
    ModifierCategory,
    ModifierMetadata,
    Pathway,
    PhysicalEntity,
    PhysicalEntityMetadata,
    ReactionLikeEvent,
    ReactomeDbId,
    Stoichiometry,
)


def law_of_mass_action(
    sbml_model: libsbml.Model, reaction: ReactionLikeEvent
) -> tuple[MathML, set[SId]]:
    kinetic_constants = set[SId]()

    def repr_stoichiometry(
        physical_entity_metadata: tuple[PhysicalEntity, Metadata],
    ) -> str:
        (physical_entity, metadata) = physical_entity_metadata
        return f"({physical_entity}^{metadata.stoichiometry})"

    forward_kinetic_constant: libsbml.Parameter = sbml_model.createParameter()
    forward_kinetic_constant.setId(f"k_f_{reaction}")
    forward_kinetic_constant.setValue(0.0)
    forward_kinetic_constant.setConstant(True)
    kinetic_constants.add(forward_kinetic_constant.getId())
    formula_forward_reaction = f"({forward_kinetic_constant.getId()} * {'*'.join(map(repr_stoichiometry, reaction.species(Category.INPUT)))})"

    formula_hill_component: str = ""
    modifiers_functions: list[str] = []
    for modifier_id, (modifier, metadata) in enumerate(reaction.modifiers()):
        half_saturation_constant: libsbml.Parameter = (
            sbml_model.createParameter()
        )
        half_saturation_constant.setId(f"k_h_{modifier_id}_{reaction}")
        half_saturation_constant.setConstant(True)
        half_saturation_constant.setValue(0.5)
        kinetic_constants.add(half_saturation_constant.getId())

        hill_function: str = ""
        match metadata.category:
            case ModifierCategory.NEGATIVE_REGULATOR:
                hill_function = f"({half_saturation_constant.getId()} / ({half_saturation_constant.getId()} + {modifier}^10))"
            case _:
                hill_function = f"({modifier}^10 / ({half_saturation_constant.getId()} + {modifier}^10))"
        modifiers_functions.append(hill_function)

    if modifiers_functions:
        formula_hill_component = f"* ({'*'.join(modifiers_functions)})"

    return (
        f"({formula_forward_reaction}) {formula_hill_component}",
        kinetic_constants,
    )


KineticLaw: TypeAlias = Callable[
    [libsbml.Model, ReactionLikeEvent], tuple[MathML, set[SId]]
]


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class BiologicalScenarioDefinition:
    physical_entities: set[PhysicalEntity]
    pathways: set[Pathway]
    constraints: PartialOrder[PhysicalEntity]
    max_depth: IntGTZ | None = field(default=None)
    excluded_physical_entities: set[PhysicalEntity] = field(default_factory=set)
    default_kinetic_law: KineticLaw = field(default=law_of_mass_action)
    kinetic_laws: dict[ReactionLikeEvent, KineticLaw] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        assert self.physical_entities

    @dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
    class _BiochemicalNetwork:
        input_physical_entities: set[ReactomeDbId]
        output_physical_entities: set[ReactomeDbId]
        network: set[PhysicalEntity | ReactionLikeEvent | Compartment]

        def __post_init__(self) -> None:
            assert self.network

    # TODO: set the species of the entities! Otherwise you look for other stuff
    def __reachable_biochemical_network(
        self, neo4j_driver: neo4j.Driver
    ) -> _BiochemicalNetwork:
        def query_reachable_reactions(reaction: LiteralString) -> LiteralString:
            reactions_of_interest: LiteralString = "reactionsOfInterest"

            query_reactions_of_interest: LiteralString = f"""
            MATCH (pathway:Pathway)
            WHERE pathway.dbId IN $scenario_pathways
            CALL
                apoc.path.subgraphNodes(
                    pathway,
                    {{
                        relationshipFilter: "hasEvent>",
                        labelFilter: ">ReactionLikeEvent"
                    }}
                )
                YIELD node
            WITH COLLECT(DISTINCT node) AS {reactions_of_interest}
            """

            reactions_of_interest_filter: LiteralString = f"""
            WHERE {reaction} IN {reactions_of_interest}
            """

            return f"""
            {query_reactions_of_interest if self.pathways else ""}
            MATCH (physicalEntity:PhysicalEntity)
            WHERE physicalEntity.dbId IN $scenario_physical_entities
            CALL
                apoc.path.subgraphNodes(
                    physicalEntity,
                    {{
                        relationshipFilter: "<output|input>|catalystActivity>|physicalEntity>|regulatedBy>|regulator>|reverseReaction",
                        labelFilter: ">ReactionLikeEvent",
                        maxLevel: $max_depth,
                        denylistNodes: $excluded_physical_entities
                    }}
                )
                YIELD node AS {reaction}
            {reactions_of_interest_filter if self.pathways else ""}
            """

        def query_reaction_like_event_attributes(
            reaction: LiteralString,
            reachable_reactions: LiteralString,
            reachable_reactions_attributes: LiteralString,
        ) -> LiteralString:
            reaction_entities: LiteralString = "entities"
            reaction_catalysts: LiteralString = "catalysts"
            reaction_regulators: LiteralString = "regulators"
            reaction_compartments: LiteralString = "compartments"

            query_species: LiteralString = f"""
            CALL {{
                WITH {reaction}
                MATCH ({reaction})-[rel:input|output]->(physicalEntity:PhysicalEntity)
                RETURN
                    COLLECT({{
                        physicalEntity: physicalEntity,
                        stoichiometry: rel.stoichiometry,
                        category: type(rel)
                    }}) AS {reaction_entities}
            }}
            """

            query_catalysts: LiteralString = f"""
            CALL {{
                WITH {reaction}
                MATCH ({reaction})-[:catalystActivity]->(:CatalystActivity)-[:physicalEntity]->(physicalEntity:PhysicalEntity)
                RETURN
                    COLLECT({{
                        physicalEntity: physicalEntity,
                        category: "catalyst"
                    }}) AS {reaction_catalysts}
            }}
            """

            query_regulators: LiteralString = f"""
            CALL {{
                WITH {reaction}
                MATCH ({reaction})-[:regulatedBy]->(regulation:Regulation)-[:regulator]->(physicalEntity:PhysicalEntity)
                RETURN
                    COLLECT({{
                        physicalEntity: physicalEntity,
                        category: CASE
                            WHEN "PositiveRegulation" IN labels(regulation) THEN "positive_regulator"
                            WHEN "NegativeRegulation" IN labels(regulation) THEN "negative_regulator"
                            ELSE ""
                        END
                    }}) AS {reaction_regulators}
            }}
            """

            query_compartments: LiteralString = f"""
            CALL {{
                WITH {reaction}
                MATCH ({reaction})-[:compartment]->(compartment:Compartment)
                RETURN COLLECT(compartment.dbId) AS {reaction_compartments}
            }}
            """
            reaction_physical_entities_attributes: LiteralString = (
                "reactionOfClosurePhysicalEntitiesData"
            )

            query_physical_entities_attributes: LiteralString = f"""
            WITH *, {reaction_entities} + {reaction_catalysts} + {reaction_regulators} AS physicalEntitiesData
            CALL {{
                WITH physicalEntitiesData, {reachable_reactions}
                UNWIND physicalEntitiesData AS data_
                CALL {{
                    WITH data_
                    WITH data_.physicalEntity AS physicalEntity
                    MATCH (physicalEntity)-[:compartment]->(compartment:Compartment)
                    RETURN COLLECT(compartment.dbId) as physicalEntityCompartments
                }}
                CALL {{
                    WITH data_, {reachable_reactions}
                    WITH data_.physicalEntity AS physicalEntity, {reachable_reactions}
                    MATCH (physicalEntity)<-[:output]-(reactionLikeEvent:ReactionLikeEvent)
                    WHERE reactionLikeEvent IN {reachable_reactions}
                    RETURN COLLECT(reactionLikeEvent.dbId) AS producedBy
                }}
                RETURN
                    COLLECT({{
                        dbId: data_.physicalEntity.dbId,
                        category: data_.category,
                        stoichiometry: data_.stoichiometry,
                        compartments: physicalEntityCompartments,
                        producedBy: producedBy
                    }}) as {reaction_physical_entities_attributes}
            }}
            """

            return f"""
            {query_species}
            {query_catalysts}
            {query_regulators}
            {query_compartments}
            {query_physical_entities_attributes}
            WITH
                COLLECT({{
                    dbId: {reaction}.dbId,
                    physicalEntities: {reaction_physical_entities_attributes},
                    compartments: {reaction_compartments}
                }}) AS {reachable_reactions_attributes},
                {reachable_reactions}
            """

        def query_frontier(
            reachable_physical_entities: LiteralString,
            reachable_reactions: LiteralString,
            network__inputs: LiteralString,
            network_outputs: LiteralString,
        ) -> LiteralString:
            def __query_frontier(
                rel: LiteralString, collection: LiteralString
            ) -> LiteralString:
                return f"""
                CALL {{
                    WITH {reachable_physical_entities}, {reachable_reactions}
                    MATCH (physicalEntity:PhysicalEntity)
                    WHERE
                        physicalEntity.dbId IN {reachable_physical_entities} AND
                        NOT EXISTS {{
                            MATCH (physicalEntity)<-[:{rel}]-(reactionLikeEvent:ReactionLikeEvent)
                            WHERE reactionLikeEvent IN {reachable_reactions}
                        }}
                    RETURN COLLECT(physicalEntity.dbId) AS {collection}
                }}
                """

            return f"""
            {__query_frontier("output", network__inputs)}
            {__query_frontier("input", network_outputs)}
            """

        reachable_reactions_attributes: LiteralString = (
            "reachableReactionLikeEventAttributes"
        )
        network__inputs: LiteralString = "networkInputs"
        network_outputs: LiteralString = "networkOutputs"

        def query() -> LiteralString:
            reaction: LiteralString = "reachableReactionLikeEvent"
            reaction_attributes: LiteralString = "reactionLikeEventAttributes"
            reachable_reactions: LiteralString = "reachableReactionLikeEvents"

            physical_entity: LiteralString = "reachablePhysicalEntity"
            reachable_physical_entities: LiteralString = (
                "reachablePhysicalEntities"
            )

            return f"""
            {query_reachable_reactions(reaction)}
            WITH COLLECT(DISTINCT {reaction}) AS {reachable_reactions}
            UNWIND {reachable_reactions} AS {reaction}
            {
                query_reaction_like_event_attributes(
                    reaction,
                    reachable_reactions,
                    reachable_reactions_attributes,
                )
            }
            UNWIND {reachable_reactions_attributes} AS {reaction_attributes}
            UNWIND {reaction_attributes}.physicalEntities AS {physical_entity}
            WITH
                {reachable_reactions_attributes},
                {reachable_reactions},
                apoc.convert.toSet(
                    apoc.coll.flatten(COLLECT({physical_entity}.dbId))
                ) AS {reachable_physical_entities}
            {
                query_frontier(
                    reachable_physical_entities,
                    reachable_reactions,
                    network__inputs,
                    network_outputs,
                )
            }
            RETURN
                {reachable_reactions_attributes},
                {network__inputs},
                {network_outputs}
            """

        records: list[neo4j.Record]
        records, _, _ = neo4j_driver.execute_query(
            query(),
            scenario_pathways=list(map(int, self.pathways)),
            scenario_physical_entities=list(map(int, self.physical_entities)),
            excluded_physical_entities=list(
                map(int, self.excluded_physical_entities)
            ),
            max_depth=int(self.max_depth) if self.max_depth else -1,
        )

        input_physical_entities = set[ReactomeDbId](
            map(ReactomeDbId, itertools.chain(records[0][network__inputs]))
        )

        output_physical_entities = set[ReactomeDbId](
            map(ReactomeDbId, itertools.chain(records[0][network_outputs]))
        )

        def get_metadata(obj: dict[str, Any]) -> PhysicalEntityMetadata:
            match obj["category"]:
                case "input" | "output":
                    return Metadata(
                        stoichiometry=Stoichiometry(int(obj["stoichiometry"])),
                        category=Category(obj["category"]),
                    )
                case _:
                    return ModifierMetadata(
                        produced_by=set(map(ReactomeDbId, obj["producedBy"])),
                        category=ModifierCategory(obj["category"]),
                    )

        rows: list[dict[str, Any]] = records[0][reachable_reactions_attributes]
        reaction_like_events: set[ReactionLikeEvent] = {
            ReactionLikeEvent(
                id=ReactomeDbId(reaction["dbId"]),
                physical_entities={
                    PhysicalEntity(
                        id=ReactomeDbId(obj["dbId"]),
                        compartments=set(map(Compartment, obj["compartments"])),
                    ): get_metadata(obj)
                    for obj in reaction["physicalEntities"]
                },
                compartments=set(map(Compartment, reaction["compartments"])),
            )
            for reaction in rows
        }

        physical_entities: set[PhysicalEntity] = reduce(
            set[PhysicalEntity].union,
            (
                reaction_like_event.physical_entities
                for reaction_like_event in reaction_like_events
            ),
            set[PhysicalEntity](),
        )

        compartments: set[Compartment] = reduce(
            set[Compartment].union,
            map(attrgetter("compartments"), reaction_like_events),
            set[Compartment](),
        ) | reduce(
            set[Compartment].union,
            map(attrgetter("compartments"), physical_entities),
            set[Compartment](),
        )

        return BiologicalScenarioDefinition._BiochemicalNetwork(
            input_physical_entities=input_physical_entities,
            output_physical_entities=output_physical_entities,
            network=physical_entities | reaction_like_events | compartments,
        )

    def generate_biological_model(
        self, driver: neo4j.Driver
    ) -> BiologicalModel:
        """Produce a model by enriching the described BiologicalScenarioDefinition with external databases."""
        sbml_document: libsbml.SBMLDocument = libsbml.SBMLDocument(3, 1)

        sbml_model: libsbml.Model = sbml_document.createModel()
        sbml_model.setTimeUnits("second")
        sbml_model.setExtentUnits("mole")
        sbml_model.setSubstanceUnits("mole")

        default_compartment: libsbml.Compartment = (
            sbml_model.createCompartment()
        )
        default_compartment.setId("default_compartment")
        default_compartment.setConstant(True)
        default_compartment.setSize(1e-9)
        default_compartment.setSpatialDimensions(3)
        default_compartment.setUnits("litre")

        time: libsbml.Parameter = sbml_model.createParameter()
        time.setId("time_")
        time.setConstant(False)
        time.setValue(0.0)

        time_rule: libsbml.RateRule = sbml_model.createRateRule()
        time_rule.setVariable("time_")
        time_rule.setFormula("1")

        kinetic_constants = set[SId]()
        reaction_like_events_constraints = PartialOrder[ReactomeDbId]()
        biological_network: BiologicalScenarioDefinition._BiochemicalNetwork = (
            self.__reachable_biochemical_network(driver)
        )

        for obj in biological_network.network:
            match obj:
                case Compartment():
                    compartment: libsbml.Compartment = (
                        sbml_model.createCompartment()
                    )
                    compartment.setId(f"{obj}")
                    compartment.setConstant(True)
                    compartment.setSize(1e-9)
                    compartment.setSpatialDimensions(3)
                    compartment.setUnits("litre")

                case PhysicalEntity():
                    species: libsbml.Species = sbml_model.createSpecies()
                    species.setId(f"{obj}")
                    species.setCompartment("default_compartment")
                    species.setConstant(False)
                    species.setSubstanceUnits("mole")
                    species.setBoundaryCondition(False)
                    species.setHasOnlySubstanceUnits(False)
                    species.setInitialConcentration(0.0)

                    species_mean: libsbml.Parameter = (
                        sbml_model.createParameter()
                    )
                    species_mean.setId(f"mean_{obj}")
                    species_mean.setConstant(False)
                    species_mean.setValue(0.0)
                    species_mean_rule: libsbml.RateRule = (
                        sbml_model.createRateRule()
                    )
                    species_mean_rule.setVariable(species_mean.getId())
                    species_mean_rule.setFormula(
                        f"({species.getId()} - {species_mean.getId()}) / (time_ + 10e-6)"
                    )

                    if (
                        obj.id in biological_network.input_physical_entities
                        and obj.id
                        in biological_network.output_physical_entities
                    ):
                        stable_constant: libsbml.Parameter = (
                            sbml_model.createParameter()
                        )
                        stable_constant.setId(f"k_{obj}")
                        stable_constant.setValue(0.0)
                        stable_constant.setConstant(True)
                        kinetic_constants.add(stable_constant.getId())

                        rule: libsbml.AssignmentRule = (
                            sbml_model.createAssignmentRule()
                        )
                        rule.setVariable(f"{species.getId()}")
                        rule.setMath(
                            libsbml.parseFormula(stable_constant.getId())
                        )
                        sbml_model.addRule(rule)
                        species.setConstant(True)
                    elif (
                        obj.id in biological_network.input_physical_entities
                        or obj.id in biological_network.output_physical_entities
                    ):
                        e_reaction: libsbml.Reaction = (
                            sbml_model.createReaction()
                        )
                        e_reaction.setReversible(False)
                        e_reaction.setFast(False)

                        e_kinetic_constant: libsbml.Parameter = (
                            sbml_model.createParameter()
                        )
                        e_kinetic_constant.setValue(0.0)
                        e_kinetic_constant.setConstant(True)

                        e_species_ref: libsbml.SpeciesReference = (
                            sbml_model.createProduct()
                            if obj.id
                            in biological_network.input_physical_entities
                            else sbml_model.createReactant()
                        )

                        e_species_ref.setSpecies(f"{obj}")
                        e_species_ref.setConstant(False)
                        e_species_ref.setStoichiometry(1)
                        e_kinetic_law: libsbml.KineticLaw = (
                            e_reaction.createKineticLaw()
                        )

                        if obj.id in biological_network.input_physical_entities:
                            e_reaction.setId(f"r_in_{obj}")
                            e_kinetic_constant.setId(f"k_f_in_{obj}")
                            e_kinetic_law.setMath(
                                libsbml.parseL3Formula(
                                    f"({e_kinetic_constant.getId()})"
                                )
                            )
                        else:
                            e_reaction.setId(f"r_out_{obj}")
                            e_kinetic_constant.setId(f"k_r_out_{obj}")
                            e_kinetic_law.setMath(
                                libsbml.parseL3Formula(
                                    f"({e_kinetic_constant.getId()} * {obj})"
                                )
                            )

                        kinetic_constants.add(e_kinetic_constant.getId())

                case ReactionLikeEvent():
                    reaction: libsbml.Reaction = sbml_model.createReaction()
                    reaction.setId(f"{obj}")
                    reaction.setReversible(obj.is_reversible)
                    reaction.setFast(False)
                    reaction.setCompartment("default_compartment")

                    for physical_entity, metadata in obj.species():
                        species_ref: libsbml.SpeciesReference
                        match metadata.category:
                            case Category.INPUT:
                                species_ref = reaction.createReactant()
                            case Category.OUTPUT:
                                species_ref = reaction.createProduct()

                        species_ref.setSpecies(repr(physical_entity))
                        species_ref.setConstant(False)
                        species_ref.setStoichiometry(
                            int(metadata.stoichiometry)
                        )

                    for physical_entity, _ in obj.modifiers():
                        modifier_species_ref: libsbml.ModifierSpeciesReference = reaction.createModifier()
                        modifier_species_ref.setSpecies(f"{physical_entity}")

                    kinetic_law_procedure = self.kinetic_laws.get(
                        obj, self.default_kinetic_law
                    )
                    l3_formula, reaction_kinetic_constants = (
                        kinetic_law_procedure(sbml_model, obj)
                    )
                    kinetic_law: libsbml.KineticLaw = (
                        reaction.createKineticLaw()
                    )
                    kinetic_law.setMath(libsbml.parseL3Formula(l3_formula))

                    kinetic_constants = (
                        kinetic_constants | reaction_kinetic_constants
                    )

                    for modifier, metadata in obj.modifiers():
                        for modifier_reaction_id in metadata.produced_by:
                            if modifier_reaction_id != obj.id:
                                reaction_like_events_constraints.add(
                                    (modifier_reaction_id, obj.id)
                                )
                            reaction_like_events_constraints.add(
                                (modifier.id, obj.id)
                            )

        kinetic_constants_constraints: PartialOrder[SId] = set()
        for reaction_1, reaction_2 in reaction_like_events_constraints:
            for kinetic_constant_1 in kinetic_constants:
                for kinetic_constant_2 in kinetic_constants:
                    if (
                        repr(reaction_1) in kinetic_constant_1
                        and repr(reaction_2) in kinetic_constant_2
                        and kinetic_constant_1.startswith("k_f")
                        and kinetic_constant_2.startswith("k_f")
                    ):
                        kinetic_constants_constraints.add(
                            (kinetic_constant_1, kinetic_constant_2)
                        )

        constraints_node: libsbml.XMLNode = libsbml.XMLNode.convertStringToXMLNode(
            f"""
            <p>
                {{
                    "kinetic_constants_constraints": [{", ".join(f"[{left}, {right}]" for (left, right) in kinetic_constants_constraints)}],
                    "physical_entities_constraints": [{", ".join(f"[{int(left)}, {int(right)}]" for (left, right) in self.constraints)}]
                }}
            </p>
            """
        )

        rdf: libsbml.XMLNode = libsbml.RDFAnnotationParser.createRDFAnnotation()
        _ = rdf.addChild(constraints_node)
        node: libsbml.XMLNode = libsbml.RDFAnnotationParser.createAnnotation()
        _ = node.addChild(rdf)
        sbml_model.setAnnotation(node)

        return BiologicalModel(
            sbml_document=sbml_document,
            kinetic_constants=kinetic_constants,
            physical_entities_constraints=self.constraints,
            kinetic_constants_constraints=kinetic_constants_constraints,
        )
