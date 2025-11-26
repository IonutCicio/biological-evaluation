import json
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import reduce
from operator import attrgetter
from time import perf_counter
from typing import Any, LiteralString, TypeAlias

import libsbml
import neo4j

from biological_scenarios_generation.core import IntGTZ, PartialOrder
from biological_scenarios_generation.model import (
    BiologicalModel,
    ConstantCategory,
    OtherParameterCategory,
    SId,
)
from biological_scenarios_generation.reactome import (
    Compartment,
    DatabaseObject,
    EntityCategory,
    EntityMetadata,
    MathML,
    ModifierCategory,
    ModifierMetadata,
    Pathway,
    PhysicalEntity,
    PhysicalEntityMetadata,
    ReactionLikeEvent,
    ReactomeDbId,
    Stoichiometry,
)


def _set_parameter_category(
    sbml_parameter: libsbml.Parameter,
    parameter_category: ConstantCategory,
    obj: DatabaseObject,
    extra: str = "",
) -> tuple[SId, ConstantCategory]:
    sbml_parameter.setAnnotation(str(parameter_category))
    sbml_parameter.setValue(0.0)
    sbml_parameter.setConstant(True)

    match parameter_category:
        case ConstantCategory.REACTION_SPEED:
            sbml_parameter.setId(f"k_{obj}")
        case ConstantCategory.PRODUCTION_SPEED:
            sbml_parameter.setId(f"k_production_reaction_{obj}")
        case ConstantCategory.CONSUMPTION_SPEED:
            sbml_parameter.setId(f"k_consumption_reaction_{obj}")
        case ConstantCategory.SPECIES_CONCENTRATION:
            sbml_parameter.setId(f"k_{obj}")
        case ConstantCategory.HALF_SATURATION:
            sbml_parameter.setId(f"k_half_saturation_{extra}_{obj}")

    return (sbml_parameter.getId(), parameter_category)


def law_of_mass_action(
    sbml_model: libsbml.Model,
    reaction_like_event: ReactionLikeEvent,
    kinetic_constants: dict[SId, ConstantCategory],
) -> MathML:
    def repr_stoichiometry(
        physical_entity_metadata: tuple[PhysicalEntity, EntityMetadata],
    ) -> str:
        (physical_entity, metadata) = physical_entity_metadata
        return f"({physical_entity}^{metadata.stoichiometry})"

    forward_kinetic_constant: libsbml.Parameter = sbml_model.createParameter()
    (_id, category) = _set_parameter_category(
        sbml_parameter=forward_kinetic_constant,
        parameter_category=ConstantCategory.REACTION_SPEED,
        obj=reaction_like_event,
    )
    kinetic_constants[_id] = category
    formula_forward_reaction = f"({_id} * {'*'.join(map(repr_stoichiometry, reaction_like_event.species(EntityCategory.INPUT)))})"

    formula_hill_component: str = ""
    modifiers_functions: list[str] = []
    for modifier, metadata in reaction_like_event.modifiers():
        half_saturation_constant: libsbml.Parameter = (
            sbml_model.createParameter()
        )
        (_id, category) = _set_parameter_category(
            sbml_parameter=half_saturation_constant,
            parameter_category=ConstantCategory.HALF_SATURATION,
            obj=reaction_like_event,
            extra=f"{modifier}",
        )
        kinetic_constants[_id] = category

        hill_function: str = ""
        match metadata.category:
            case ModifierCategory.NEGATIVE_REGULATOR:
                hill_function = f"({half_saturation_constant.getId()} / ({half_saturation_constant.getId()} + {modifier}^10))"
            case _:
                hill_function = f"({modifier}^10 / ({half_saturation_constant.getId()} + {modifier}^10))"
        modifiers_functions.append(hill_function)

    if modifiers_functions:
        formula_hill_component = f"* ({'*'.join(modifiers_functions)})"

    return f"({formula_forward_reaction}) {formula_hill_component}"


KineticLaw: TypeAlias = Callable[
    [libsbml.Model, ReactionLikeEvent, dict[SId, ConstantCategory]], MathML
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
        assert self.physical_entities  # 1..*

        # {disjoint, complete}
        assert not self.physical_entities.intersection(
            self.excluded_physical_entities
        )

        for physical_entity_1, physical_entity_2 in self.constraints:
            assert (
                physical_entity_2,
                physical_entity_1,
            ) not in self.constraints

    @dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
    class _BiochemicalNetwork:
        interface__inputs: set[ReactomeDbId]
        interface_outputs: set[ReactomeDbId]
        physical_entities: set[PhysicalEntity]
        reaction_like_events: set[ReactionLikeEvent]
        compartments: set[Compartment]

        def __post_init__(self) -> None:
            assert len(
                self.physical_entities
                | self.reaction_like_events
                | self.compartments
            ) == len(self.physical_entities) + len(
                self.reaction_like_events
            ) + len(self.compartments)

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

        def query_interface(
            reachable_physical_entities: LiteralString,
            reachable_reactions: LiteralString,
            network__inputs: LiteralString,
            network_outputs: LiteralString,
        ) -> LiteralString:
            def __query_interface(
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
            {__query_interface("output", network__inputs)}
            {__query_interface("input", network_outputs)}
            """

        def query(
            reachable_reactions_attributes: LiteralString,
            network__inputs: LiteralString,
            network_outputs: LiteralString,
        ) -> LiteralString:
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
                query_interface(
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

        reachable_reactions_attributes: LiteralString = (
            "reachableReactionLikeEventAttributes"
        )
        network__inputs: LiteralString = "networkInputs"
        network_outputs: LiteralString = "networkOutputs"
        records: list[neo4j.Record]
        summary: neo4j.ResultSummary

        start = perf_counter()
        records, summary, _ = neo4j_driver.execute_query(
            query(
                reachable_reactions_attributes, network__inputs, network_outputs
            ),
            scenario_pathways=list(map(int, self.pathways)),
            scenario_physical_entities=list(map(int, self.physical_entities)),
            excluded_physical_entities=list(
                map(int, self.excluded_physical_entities)
            ),
            max_depth=int(self.max_depth) if self.max_depth else -1,
        )
        end = perf_counter()

        result_record = records[0]

        interface__inputs = set[ReactomeDbId](
            map(ReactomeDbId, result_record[network__inputs])
        )

        interface_outputs = set[ReactomeDbId](
            map(ReactomeDbId, result_record[network_outputs])
        )

        def get_metadata(obj: dict[str, Any]) -> PhysicalEntityMetadata:
            match obj["category"]:
                case "input" | "output":
                    return EntityMetadata(
                        stoichiometry=Stoichiometry(int(obj["stoichiometry"])),
                        category=EntityCategory(obj["category"]),
                    )
                case _:
                    return ModifierMetadata(
                        produced_by=set(map(ReactomeDbId, obj["producedBy"])),
                        category=ModifierCategory(obj["category"]),
                    )

        rows: list[dict[str, Any]] = result_record[
            reachable_reactions_attributes
        ]
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

        print(
            json.dumps(
                {
                    "perf": end - start,
                    "available_after": summary.result_available_after,  # milliseconds
                    "consumed_after": summary.result_consumed_after,  # milliseconds
                    "physical_entities": len(physical_entities),
                    "reaction_like_events": len(reaction_like_events),
                }
            ),
            ",",
        )

        # raise Exception()

        return BiologicalScenarioDefinition._BiochemicalNetwork(
            interface__inputs=interface__inputs,
            interface_outputs=interface_outputs,
            physical_entities=physical_entities,
            reaction_like_events=reaction_like_events,
            compartments=compartments,
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

        time: libsbml.Parameter = sbml_model.createParameter()
        time.setId("time_")
        time.setConstant(False)
        time.setValue(0.0)
        time.setAnnotation(str(OtherParameterCategory.TIME))

        time_rate_rule: libsbml.RateRule = sbml_model.createRateRule()
        time_rate_rule.setVariable("time_")
        time_rate_rule.setFormula("1")

        kinetic_constants: dict[SId, ConstantCategory] = {}
        other_parameters: dict[SId, OtherParameterCategory] = {
            time.getId(): OtherParameterCategory.TIME
        }
        reaction_like_events_order = PartialOrder[ReactomeDbId]()
        reachable_biochemical_network: BiologicalScenarioDefinition._BiochemicalNetwork = self.__reachable_biochemical_network(
            driver
        )

        default_compartment: libsbml.Compartment = (
            sbml_model.createCompartment()
        )
        default_compartment.setId("default_compartment")
        default_compartment.setConstant(True)
        default_compartment.setSize(1e-9)
        default_compartment.setSpatialDimensions(3)
        default_compartment.setUnits("litre")

        for obj in reachable_biochemical_network.compartments:
            sbml_compartment: libsbml.Compartment = (
                sbml_model.createCompartment()
            )
            sbml_compartment.setId(f"{obj}")
            sbml_compartment.setConstant(True)
            sbml_compartment.setSize(1e-9)
            sbml_compartment.setSpatialDimensions(3)
            sbml_compartment.setUnits("litre")

        for obj in reachable_biochemical_network.physical_entities:
            sbml_species: libsbml.Species = sbml_model.createSpecies()
            sbml_species.setId(f"{obj}")
            sbml_species.setCompartment(default_compartment.getId())
            sbml_species.setConstant(False)
            sbml_species.setSubstanceUnits("mole")
            sbml_species.setBoundaryCondition(False)
            sbml_species.setHasOnlySubstanceUnits(False)
            sbml_species.setInitialConcentration(0.0)

            if (
                obj.id in reachable_biochemical_network.interface__inputs
                and obj.id in reachable_biochemical_network.interface_outputs
            ):
                # If a species is not produced and not consumed by any reaction
                # in the network then it can be set to a constant concentration.
                sbml_parameter: libsbml.Parameter = sbml_model.createParameter()
                (_id, category) = _set_parameter_category(
                    sbml_parameter=sbml_parameter,
                    parameter_category=ConstantCategory.SPECIES_CONCENTRATION,
                    obj=obj,
                )
                kinetic_constants[_id] = category

                sbml_assignment_rule: libsbml.AssignmentRule = (
                    sbml_model.createAssignmentRule()
                )
                sbml_assignment_rule.setVariable(f"{sbml_species.getId()}")
                sbml_assignment_rule.setMath(
                    libsbml.parseFormula(sbml_parameter.getId())
                )

                sbml_model.addRule(sbml_assignment_rule)
                sbml_species.setConstant(True)
                continue

            # If the species is involved in a reaction of the network then
            # its mean needs to be computed.
            sbml_species_mean: libsbml.Parameter = sbml_model.createParameter()
            sbml_species_mean.setId(f"mean_{obj}")
            other_parameters[sbml_species_mean.getId()] = (
                OtherParameterCategory.SPECIES_MEAN
            )
            sbml_species_mean.setAnnotation(
                str(OtherParameterCategory.SPECIES_MEAN)
            )
            sbml_species_mean.setConstant(False)
            sbml_species_mean.setValue(0.0)

            sbml_species_mean_rule: libsbml.RateRule = (
                sbml_model.createRateRule()
            )
            sbml_species_mean_rule.setVariable(sbml_species_mean.getId())
            sbml_species_mean_rule.setFormula(
                f"({sbml_species.getId()} - {sbml_species_mean.getId()}) / ({time.getId()} + 10e-6)"
            )

            if (
                obj.id in reachable_biochemical_network.interface__inputs
                or obj.id in reachable_biochemical_network.interface_outputs
            ):
                sbml_reaction: libsbml.Reaction = sbml_model.createReaction()
                sbml_reaction.setReversible(False)
                sbml_reaction.setFast(False)

                sbml_parameter: libsbml.Parameter = sbml_model.createParameter()

                _species_ref: libsbml.SpeciesReference = (
                    sbml_model.createProduct()
                    if obj.id in reachable_biochemical_network.interface__inputs
                    else sbml_model.createReactant()
                )

                _species_ref.setSpecies(f"{obj}")
                _species_ref.setConstant(False)
                _species_ref.setStoichiometry(1)
                _kinetic_law: libsbml.KineticLaw = (
                    sbml_reaction.createKineticLaw()
                )
                _id: SId
                category: ConstantCategory
                if obj.id in reachable_biochemical_network.interface__inputs:
                    sbml_reaction.setId(f"reaction_production_{obj}")
                    (_id, category) = _set_parameter_category(
                        sbml_parameter=sbml_parameter,
                        parameter_category=ConstantCategory.PRODUCTION_SPEED,
                        obj=obj,
                    )
                    _kinetic_law.setMath(
                        libsbml.parseL3Formula(f"({sbml_parameter.getId()})")
                    )
                else:
                    sbml_reaction.setId(f"reaction_consumption_{obj}")
                    (_id, category) = _set_parameter_category(
                        sbml_parameter=sbml_parameter,
                        parameter_category=ConstantCategory.CONSUMPTION_SPEED,
                        obj=obj,
                    )
                    _kinetic_law.setMath(
                        libsbml.parseL3Formula(f"({_id} * {obj})")
                    )
                kinetic_constants[_id] = category

        for obj in reachable_biochemical_network.reaction_like_events:
            reaction: libsbml.Reaction = sbml_model.createReaction()
            reaction.setId(f"{obj}")
            reaction.setReversible(obj.is_reversible)
            reaction.setFast(False)
            reaction.setCompartment(default_compartment.getId())

            for physical_entity, metadata in obj.species():
                species_ref: libsbml.SpeciesReference
                match metadata.category:
                    case EntityCategory.INPUT:
                        species_ref = reaction.createReactant()
                    case EntityCategory.OUTPUT:
                        species_ref = reaction.createProduct()

                species_ref.setSpecies(repr(physical_entity))
                species_ref.setConstant(False)
                species_ref.setStoichiometry(int(metadata.stoichiometry))

            for physical_entity, _ in obj.modifiers():
                modifier_species_ref: libsbml.ModifierSpeciesReference = (
                    reaction.createModifier()
                )
                modifier_species_ref.setSpecies(f"{physical_entity}")

            kinetic_law_procedure = self.kinetic_laws.get(
                obj, self.default_kinetic_law
            )
            kinetic_law: libsbml.KineticLaw = reaction.createKineticLaw()
            kinetic_law.setMath(
                libsbml.parseL3Formula(
                    kinetic_law_procedure(sbml_model, obj, kinetic_constants)
                )
            )

            for modifier, metadata in obj.modifiers():
                for modifier_reaction_id in metadata.produced_by:
                    if modifier_reaction_id != obj.id:
                        reaction_like_events_order.add(
                            (modifier_reaction_id, obj.id)
                        )
                    reaction_like_events_order.add((modifier.id, obj.id))

        # All reactions that have a modifier as product are slower than
        # reactions that are modified.
        kinetic_constants_order: PartialOrder[SId] = set()
        for reaction_1, reaction_2 in reaction_like_events_order:
            for kinetic_constant_1 in kinetic_constants:
                if str(reaction_1) in kinetic_constant_1 and (
                    kinetic_constant_1.startswith(
                        ("k_production_", "k_reaction_")
                    )
                ):
                    for kinetic_constant_2 in kinetic_constants:
                        if (
                            str(reaction_2) in kinetic_constant_2
                            and kinetic_constant_2.startswith(
                                ("k_production_", "k_reaction_")
                            )
                        ):
                            kinetic_constants_order.add(
                                (kinetic_constant_1, kinetic_constant_2)
                            )

        sbml_model.setAnnotation(
            json.dumps(
                {
                    "kinetic_constants_order": list(
                        map(list, kinetic_constants_order)
                    ),
                    "species_order": [
                        list(map(int, order)) for order in self.constraints
                    ],
                }
            )
        )

        return BiologicalModel(
            sbml_document=sbml_document,
            species_order=self.constraints,
            other_parameters=other_parameters,
            kinetic_constants=kinetic_constants,
            kinetic_constants_order=kinetic_constants_order,
        )
