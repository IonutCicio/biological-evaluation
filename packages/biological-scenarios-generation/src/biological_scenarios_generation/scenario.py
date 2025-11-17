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
    Compartment,
    DatabaseObject,
    MathML,
    ModifierCategory,
    ModifierMetadata,
    Pathway,
    PhysicalEntity,
    PhysicalEntityMetadata,
    ReactionLikeEvent,
    ReactomeDbId,
    SpeciesCategory,
    SpeciesMetadata,
    Stoichiometry,
)


def law_of_mass_action(
    sbml_model: libsbml.Model, reaction: ReactionLikeEvent
) -> tuple[MathML, set[SId]]:
    kinetic_constants = set[SId]()

    def repr_stoichiometry(
        physical_entity_metadata: tuple[PhysicalEntity, SpeciesMetadata],
    ) -> str:
        (physical_entity, metadata) = physical_entity_metadata
        return f"({physical_entity}^{metadata.stoichiometry})"

    forward_kinetic_constant: libsbml.Parameter = sbml_model.createParameter()
    forward_kinetic_constant.setId(f"k_f_{reaction}")
    forward_kinetic_constant.setValue(0.0)
    forward_kinetic_constant.setConstant(True)
    kinetic_constants.add(forward_kinetic_constant.getId())
    formula_forward_reaction = f"({forward_kinetic_constant.getId()} * {'*'.join(map(repr_stoichiometry, reaction.entities(SpeciesCategory.INPUT)))})"

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
    """Definition of a target scenario to expand for simulations."""

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
    class _BiologicalNetwork:
        input_physical_entities: set[ReactomeDbId]
        output_physical_entities: set[ReactomeDbId]
        network: set[PhysicalEntity | ReactionLikeEvent | Compartment]

        def __post_init__(self) -> None:
            assert self.network
            assert self.input_physical_entities

    def __biological_network(
        self, neo4j_driver: neo4j.Driver
    ) -> _BiologicalNetwork:
        reactions_of_interest: LiteralString = "reactionsOfInterest"
        network_reaction: LiteralString = "networkReactionLikeEvent"
        network_reactions: LiteralString = "networkReactionLikeEvents"
        network_physical_entity: LiteralString = "networkPhysicalEntity"
        network_compartment: LiteralString = "networkCompartment"
        network_reaction_physical_entity: LiteralString = (
            "networkReactionPhysicalEntity"
        )
        network_reaction_physical_entities: LiteralString = (
            "networkReactionPhysicalEntities"
        )
        category: LiteralString = "category"

        query_reaction_of_interest_subset: LiteralString = f"""
        MATCH (pathway:Pathway)
        WHERE pathway.dbId IN $scenario_pathways
        CALL
            apoc.path.subgraphNodes(
                pathway,
                {{relationshipFilter: "hasEvent>", labelFilter: ">ReactionLikeEvent"}}
            )
            YIELD node
        WITH COLLECT(DISTINCT node) AS {reactions_of_interest}
        """

        query_transitive_closure_of_scenario: LiteralString = f"""
        MATCH (physicalEntity:PhysicalEntity)
        WHERE physicalEntity.dbId IN $scenario_physical_entities
        CALL
            apoc.path.subgraphNodes(
                physicalEntity,
                {{
                    relationshipFilter: "<output|input>|catalystActivity>|physicalEntity>|<regulatedBy|regulator>",
                    labelFilter: ">ReactionLikeEvent",
                    maxLevel: $max_depth,
                    denylistNodes: $excluded_physical_entities
                }}
            )
            YIELD node AS {network_reaction}
        """

        query_reaction_species: LiteralString = f"""
        CALL {{
            WITH {network_reaction}
            MATCH ({network_reaction})-[metadata:input|output]->({network_physical_entity}:PhysicalEntity)
            RETURN
                COLLECT({{
                    physicalEntity: {network_physical_entity},
                    stoichiometry: metadata.stoichiometry,
                    {category}: type(metadata)
                }}) AS species
        }}
        """

        query_reaction_enzymes: LiteralString = f"""
        CALL {{
            WITH {network_reaction}
            MATCH ({network_reaction})-[:catalystActivity]->(:CatalystActivity)-[:physicalEntity]->({network_physical_entity}:PhysicalEntity)
            RETURN
                COLLECT({{
                    physicalEntity: {network_physical_entity},
                    {category}: "enzyme"
                }}) AS enzymes
        }}
        """

        query_reaction_regulators: LiteralString = f"""
        CALL {{
            WITH {network_reaction}
            MATCH ({network_reaction})-[:regulatedBy]->(regulation:Regulation)-[:regulator]->({network_physical_entity}:PhysicalEntity)
            RETURN
                COLLECT({{
                    physicalEntity: {network_physical_entity},
                    {category}: CASE
                        WHEN "PositiveRegulation" in labels(regulation) THEN "positive_regulator"
                        WHEN "NegativeRegulation" in labels(regulation) THEN "negative_regulator"
                        ELSE ""
                    END
                }}) AS regulators
        }}
        """

        query_reaction_compartments: LiteralString = f"""
        CALL {{
            WITH {network_reaction}
            MATCH ({network_reaction})-[:compartment]->({network_compartment}:Compartment)
            RETURN COLLECT({network_compartment}.dbId) AS compartments
        }}
        """

        query_reaction_physical_entities_metadata: LiteralString = f"""
        WITH *, species + enzymes + regulators AS {network_reaction_physical_entities}
        CALL {{
            WITH {network_reaction_physical_entities}, {network_reactions}
            UNWIND {network_reaction_physical_entities} AS {network_reaction_physical_entity}
            CALL {{
                WITH {network_reaction_physical_entity}
                WITH {network_reaction_physical_entity}.physicalEntity AS {network_physical_entity}
                MATCH ({network_physical_entity})-[:compartment]->({network_compartment}:Compartment)
                RETURN COLLECT({network_compartment}.dbId) as physicalEntityCompartments
            }}
            CALL {{
                WITH {network_reaction_physical_entity}, {network_reactions}
                WITH {network_reaction_physical_entity}.physicalEntity AS {network_physical_entity}, {network_reactions}

                MATCH ({network_physical_entity})<-[:input]-(r:ReactionLikeEvent)
                WHERE r IN {network_reactions}
                RETURN COLLECT(r.dbId) AS producedBy
            }}
            RETURN
                COLLECT({{
                    id: {network_reaction_physical_entity}.physicalEntity.dbId,
                    {category}: {network_reaction_physical_entity}.{category},
                    stoichiometry: {network_reaction_physical_entity}.stoichiometry,
                    compartments: physicalEntityCompartments,
                    produced_by: producedBy
                }}) as physicalEntities
        }}
        """

        query_network_inputs: LiteralString = f"""
        CALL {{
            WITH {network_reactions}, networkPhysicalEntities
            MATCH (physicalEntity:PhysicalEntity)
            WHERE
                physicalEntity.dbId IN networkPhysicalEntities AND
                NOT EXISTS {{
                    MATCH (physicalEntity)<-[:output]-(reactionLikeEvent:ReactionLikeEvent)
                    WHERE reactionLikeEvent IN {network_reactions}
                }}
            RETURN COLLECT(physicalEntity.dbId) AS networkInputs
        }}
        """

        query_network_outputs: LiteralString = f"""
        CALL {{
            WITH {network_reactions}, networkPhysicalEntities
            MATCH (physicalEntity:PhysicalEntity)
            WHERE
                physicalEntity.dbId IN networkPhysicalEntities AND
                NOT EXISTS {{
                    MATCH (physicalEntity)<-[:input]-(reactionLikeEvent:ReactionLikeEvent)
                    WHERE reactionLikeEvent IN {network_reactions}
                }}
            RETURN COLLECT(physicalEntity.dbId) AS networkOutputs
        }}
        """

        query: LiteralString = f"""
        {query_reaction_of_interest_subset if self.pathways else ""}
        {query_transitive_closure_of_scenario}
        {f"WHERE {network_reaction} IN {reactions_of_interest}" if self.pathways else ""}
        WITH COLLECT(DISTINCT {network_reaction}) AS {network_reactions}
        UNWIND {network_reactions} AS {network_reaction}
        {query_reaction_species}
        {query_reaction_enzymes}
        {query_reaction_regulators}
        {query_reaction_compartments}
        {query_reaction_physical_entities_metadata}
        WITH
            COLLECT({{
                id: {network_reaction}.dbId,
                physical_entities: physicalEntities,
                compartments: compartments
            }}) AS networkReactionsMetadata,
            {network_reactions}
        UNWIND networkReactionsMetadata AS {network_reaction}
        UNWIND {network_reaction}.physical_entities AS {network_physical_entity}
        WITH
            networkReactionsMetadata,
            {network_reactions},
            apoc.convert.toSet(
                apoc.coll.flatten(
                    COLLECT({network_physical_entity}.id)
                )
            ) AS networkPhysicalEntities
        {query_network_inputs}
        {query_network_outputs}
        RETURN networkReactionsMetadata, networkInputs, networkOutputs
        """

        records: list[neo4j.Record]
        records, _, _ = neo4j_driver.execute_query(
            query,
            scenario_pathways=list(map(int, self.pathways)),
            scenario_physical_entities=list(map(int, self.physical_entities)),
            excluded_physical_entities=list(
                map(int, self.excluded_physical_entities)
            ),
            max_depth=int(self.max_depth) if self.max_depth else -1,
        )

        def match_category(obj: dict[str, str]) -> PhysicalEntityMetadata:
            match obj[category]:
                case "input" | "output":
                    return SpeciesMetadata(
                        stoichiometry=Stoichiometry(int(obj["stoichiometry"])),
                        category=SpeciesCategory(obj[category]),
                    )
                case _:
                    return ModifierMetadata(
                        produced_by={
                            DatabaseObject(ReactomeDbId(int(obj_id)))
                            for obj_id in obj["produced_by"]
                        },
                        category=ModifierCategory(obj[category]),
                    )
                    # return ModifierCategory(obj[category])

        input_physical_entities = set[ReactomeDbId](
            map(ReactomeDbId, itertools.chain(records[0]["networkInputs"]))
        )

        output_physical_entities = set[ReactomeDbId](
            map(ReactomeDbId, itertools.chain(records[0]["networkOutputs"]))
        )

        print(records[0]["networkReactionsMetadata"])

        rows: list[dict[str, Any]] = records[0]["networkReactionsMetadata"]
        reaction_like_events: set[ReactionLikeEvent] = {
            ReactionLikeEvent(
                id=ReactomeDbId(reaction["id"]),
                physical_entities={
                    PhysicalEntity(
                        id=ReactomeDbId(obj["id"]),
                        compartments=set(map(Compartment, obj["compartments"])),
                    ): match_category(obj)
                    for obj in reaction["physical_entities"]
                },
                compartments=set(map(Compartment, reaction["compartments"])),
                # is_reversible=bool(reaction["reverse_reaction"]),
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

        return BiologicalScenarioDefinition._BiologicalNetwork(
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
        default_compartment.setSize(1)
        default_compartment.setSpatialDimensions(3)
        default_compartment.setUnits("litre")

        time: libsbml.Parameter = sbml_model.createParameter()
        time.setId("time_")
        time.setConstant(False)
        time.setValue(0.0)

        time_rule: libsbml.RateRule = sbml_model.createRateRule()
        time_rule.setVariable("time_")
        time_rule.setFormula("1")

        # environment_physical_entities = set[PhysicalEntity]()
        kinetic_constants = set[SId]()
        kinetic_constants_constraints = PartialOrder[DatabaseObject]()
        biological_network: BiologicalScenarioDefinition._BiologicalNetwork = (
            self.__biological_network(driver)
        )

        for obj in biological_network.network:
            match obj:
                case Compartment():
                    compartment: libsbml.Compartment = (
                        sbml_model.createCompartment()
                    )
                    compartment.setId(repr(obj))
                    compartment.setConstant(True)
                    compartment.setSize(1)
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
                        species.setInitialConcentration(0.5)
                    elif obj.id in biological_network.input_physical_entities:
                        production_reaction: libsbml.Reaction = (
                            sbml_model.createReaction()
                        )
                        production_reaction.setId(f"r_{obj}")
                        production_reaction.setReversible(False)
                        production_reaction.setFast(False)

                        kinetic_constant: libsbml.Parameter = (
                            sbml_model.createParameter()
                        )
                        kinetic_constant.setId(f"k_f_r_{obj}")
                        kinetic_constant.setValue(1.0)
                        kinetic_constant.setConstant(True)
                        kinetic_constants.add(kinetic_constant.getId())

                        input_species_ref: libsbml.SpeciesReference = (
                            sbml_model.createProduct()
                        )
                        input_species_ref.setSpecies(f"{obj}")
                        input_species_ref.setConstant(False)
                        input_species_ref.setStoichiometry(1)
                        input_kinetic_law: libsbml.KineticLaw = (
                            production_reaction.createKineticLaw()
                        )
                        input_kinetic_law.setMath(
                            libsbml.parseL3Formula(
                                f"({kinetic_constant.getId()})"
                            )
                        )
                    elif obj.id in biological_network.output_physical_entities:
                        consumption_reaction: libsbml.Reaction = (
                            sbml_model.createReaction()
                        )
                        consumption_reaction.setId(f"r_{obj}")
                        consumption_reaction.setReversible(False)
                        consumption_reaction.setFast(False)

                        kinetic_constant: libsbml.Parameter = (
                            sbml_model.createParameter()
                        )
                        kinetic_constant.setId(f"k_r_r_{obj}")
                        kinetic_constant.setValue(0.0)
                        kinetic_constant.setConstant(True)
                        kinetic_constants.add(kinetic_constant.getId())

                        output_species_ref: libsbml.SpeciesReference = (
                            sbml_model.createReactant()
                        )
                        output_species_ref.setSpecies(repr(obj))
                        output_species_ref.setConstant(False)
                        output_species_ref.setStoichiometry(1)
                        output_kinetic_law: libsbml.KineticLaw = (
                            consumption_reaction.createKineticLaw()
                        )
                        output_kinetic_law.setMath(
                            libsbml.parseL3Formula(
                                f"({kinetic_constant.getId()} * {obj})"
                            )
                        )

                case ReactionLikeEvent():
                    reaction: libsbml.Reaction = sbml_model.createReaction()
                    reaction.setId(f"{obj}")
                    reaction.setReversible(obj.is_reversible)
                    reaction.setFast(False)
                    # reaction_compartment = (
                    #     repr(next(iter(obj.compartments)))
                    #     if obj.compartments
                    #     else "default_compartment"
                    # )
                    # reaction.setCompartment(reaction_compartment)
                    reaction.setCompartment("default_compartment")

                    for physical_entity, metadata in obj.entities():
                        species_ref: libsbml.SpeciesReference
                        match metadata.category:
                            case SpeciesCategory.INPUT:
                                species_ref = reaction.createReactant()
                            case SpeciesCategory.OUTPUT:
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
                    for _, metadata in obj.modifiers():
                        for modifier_reaction in metadata.produced_by:
                            kinetic_constants_constraints.add(
                                (modifier_reaction, obj)
                            )

        return BiologicalModel(
            sbml_document=sbml_document,
            kinetic_constants=kinetic_constants,
            physical_entities_constraints=self.constraints,
            kinetic_constants_constraints=kinetic_constants_constraints,
        )
