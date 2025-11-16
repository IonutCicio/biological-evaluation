import itertools
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import reduce
from operator import attrgetter
from typing import Any, LiteralString, TypeAlias

import libsbml
import neo4j

from biological_scenarios_generation.core import IntGTZ, PartialOrder
from biological_scenarios_generation.model import (
    BiologicalModel,
    EnvironmentGenerator,
    SId,
    VirtualPatientGenerator,
)
from biological_scenarios_generation.reactome import (
    Compartment,
    MathML,
    ModifierRole,
    Pathway,
    PhysicalEntity,
    ReactionLikeEvent,
    ReactomeDbId,
    Role,
    StandardRole,
    StandardRoleInformation,
    Stoichiometry,
)


class BaseKineticLaw(Enum):
    """Well known kinetic laws."""

    LAW_OF_MASS_ACTION = auto()
    CONVENIENCE_KINETIC_LAW = auto()

    def __call__(
        self, sbml_model: libsbml.Model, reaction: ReactionLikeEvent
    ) -> tuple[MathML, set[SId]]:
        """Return reaction law and generate parameters."""
        kinetic_constants = set[SId]()

        def repr_stoichiometry(
            physical_entity_role_information: tuple[
                PhysicalEntity, StandardRoleInformation
            ],
        ) -> str:
            (physical_entity, role_information) = (
                physical_entity_role_information
            )
            return f"({physical_entity}^{role_information.stoichiometry})"

        match self:
            case BaseKineticLaw.LAW_OF_MASS_ACTION:
                forward_kinetic_constant: libsbml.Parameter = (
                    sbml_model.createParameter()
                )
                forward_kinetic_constant.setId(f"k_f_{reaction}")
                forward_kinetic_constant.setValue(0.0)
                forward_kinetic_constant.setConstant(True)
                kinetic_constants.add(forward_kinetic_constant.getId())
                formula_forward_reaction = f"({forward_kinetic_constant.getId()} * {'*'.join(map(repr_stoichiometry, reaction.entities(StandardRole.INPUT)))})"

                formula_reverse_reaction: str = ""
                # if reaction.is_reversible:
                #     reverse_kinetic_constant: libsbml.Parameter = (
                #         sbml_model.createParameter()
                #     )
                #     reverse_kinetic_constant.setValue(0.0)
                #     reverse_kinetic_constant.setId(f"k_r_{reaction}")
                #     reverse_kinetic_constant.setConstant(True)
                #     kinetic_constants.add(reverse_kinetic_constant.getId())
                #
                #     formula_reverse_reaction = f"- ({reverse_kinetic_constant.getId()} * {'*'.join(map(repr_stoichiometry, reaction.entities(StandardRole.OUTPUT)))})"

                formula_hill_component: str = ""
                modifiers_functions: list[str] = []
                for mod_id, (modifier, role) in enumerate(reaction.modifiers()):
                    half_saturation_constant: libsbml.Parameter = (
                        sbml_model.createParameter()
                    )
                    half_saturation_constant.setId(f"k_h_{mod_id}_{reaction}")
                    half_saturation_constant.setConstant(True)
                    half_saturation_constant.setValue(0.5)
                    kinetic_constants.add(half_saturation_constant.getId())

                    hill_function: str = ""
                    match role:
                        case ModifierRole.NEGATIVE_REGULATOR:
                            hill_function = f"({half_saturation_constant.getId()} / ({half_saturation_constant.getId()} + {modifier}^10))"
                        case _:
                            hill_function = f"({modifier}^10 / ({half_saturation_constant.getId()} + {modifier}^10))"
                    modifiers_functions.append(hill_function)

                if modifiers_functions:
                    formula_hill_component = (
                        f"* ({'*'.join(modifiers_functions)})"
                    )

                formula_regulation: str = ""

                return (
                    f"({formula_forward_reaction} {formula_reverse_reaction}) {formula_hill_component} {formula_regulation}",
                    kinetic_constants,
                )

            case BaseKineticLaw.CONVENIENCE_KINETIC_LAW:
                return ("", set[SId]())


CustomKineticLaw: TypeAlias = Callable[
    [libsbml.Model, ReactionLikeEvent], tuple[MathML, set[SId]]
]

KineticLaw: TypeAlias = BaseKineticLaw | CustomKineticLaw


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class BiologicalScenarioDefinition:
    """Definition of a target scenario to expand for simulations."""

    physical_entities: set[PhysicalEntity]
    pathways: set[Pathway]
    constraints: PartialOrder[PhysicalEntity]
    max_depth: IntGTZ | None = field(default=None)
    ignored_physical_entities: set[PhysicalEntity] = field(default_factory=set)
    default_kinetic_law: KineticLaw = field(
        default=BaseKineticLaw.LAW_OF_MASS_ACTION
    )
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
        _network_reaction: LiteralString = "networkReactionLikeEvent"
        _network_physical_entity: LiteralString = "networkPhysicalEntity"
        _network_compartment: LiteralString = "networkCompartment"
        physical_entity_reference: LiteralString = (
            "networkPhysicalEntityReference"
        )

        query_reactions_of_interest_subset: LiteralString = """
        MATCH (pathway:Pathway)
        WHERE pathway.dbId IN $scenario_pathways
        CALL
            apoc.path.subgraphNodes(
                pathway,
                {relationshipFilter: "hasEvent>", labelFilter: ">ReactionLikeEvent"}
            )
            YIELD node
        WITH COLLECT(DISTINCT node) AS reactionsOfInterest
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
                    denylistNodes: $ignored_physical_entities
                }}
            )
            YIELD node AS {_network_reaction}
        """

        filter_reactions_of_interest: LiteralString = (
            f"WHERE {_network_reaction} IN reactionsOfInterest"
        )

        query_network_reaction_inputs: LiteralString = f"""
        CALL {{
            WITH {_network_reaction}
            MATCH ({_network_reaction})-[relationship:input]->({_network_physical_entity}:PhysicalEntity)
            RETURN
                COLLECT({{
                    physicalEntity: {_network_physical_entity},
                    stoichiometry: relationship.stoichiometry,
                    role: "input"
                }}) AS inputs
        }}
        """

        query_network_reaction_outputs: LiteralString = f"""
        CALL {{
            WITH {_network_reaction}
            MATCH ({_network_reaction})-[relationship:output]->({_network_physical_entity}:PhysicalEntity)
            RETURN
                COLLECT({{
                    physicalEntity: {_network_physical_entity},
                    stoichiometry: relationship.stoichiometry,
                    role: "output"
                }}) AS outputs
        }}
        """

        query_network_reaction_enzymes: LiteralString = f"""
        CALL {{
            WITH {_network_reaction}
            MATCH ({_network_reaction})-[:catalystActivity]->(:CatalystActivity)-[:physicalEntity]->({_network_physical_entity}:PhysicalEntity)
            RETURN
                COLLECT({{
                    physicalEntity: {_network_physical_entity},
                    role: "enzyme"
                }}) AS enzymes
        }}
        """

        def query_network_reaction_regulators(
            label: LiteralString, role: LiteralString, collection: LiteralString
        ) -> LiteralString:
            return f"""
            CALL {{
                WITH {_network_reaction}
                MATCH ({_network_reaction})-[:regulatedBy]->(:{label})-[:regulator]->({_network_physical_entity}:PhysicalEntity)
                RETURN
                    COLLECT({{
                        physicalEntity: {_network_physical_entity},
                        role: "{role}"
                    }}) AS {collection}
            }}
            """

        query_network_reaction_positive_regulators: LiteralString = (
            query_network_reaction_regulators(
                label="PositiveRegulation",
                role="positive_regulator",
                collection="positiveRegulators",
            )
        )

        query_network_reaction_negative_regulators: LiteralString = (
            query_network_reaction_regulators(
                label="NegativeRegulation",
                role="negative_regulator",
                collection="negativeRegulators",
            )
        )

        query_network_reaction_compartments: LiteralString = f"""
        CALL {{
            WITH {_network_reaction}
            MATCH ({_network_reaction})-[:compartment]->({_network_compartment}:Compartment)
            RETURN COLLECT({_network_compartment}.dbId) AS compartments
        }}
        """

        query_is_network_reaction_reversible: LiteralString = f"""
        CALL {{
            WITH {_network_reaction}
            OPTIONAL MATCH ({_network_reaction})-[:reverseReaction]->(reverseReactionLikeEvent)
            RETURN reverseReactionLikeEvent
        }}
        """

        query_expand_reaction_physical_entities_information: LiteralString = f"""
        WITH *, inputs + outputs + enzymes + positiveRegulators + negativeRegulators AS references
        CALL {{
            WITH references
            UNWIND references AS {physical_entity_reference}
            CALL {{
                WITH {physical_entity_reference}
                WITH {physical_entity_reference}.physicalEntity AS {_network_physical_entity}
                    MATCH ({_network_physical_entity})-[:compartment]-({_network_compartment}:Compartment)
                    RETURN COLLECT({_network_compartment}.dbId) as physicalEntityCompartments
                }}
                RETURN
                    COLLECT({{
                        id: {physical_entity_reference}.physicalEntity.dbId,
                        role: {physical_entity_reference}.role,
                        stoichiometry: {physical_entity_reference}.stoichiometry,
                        compartments: physicalEntityCompartments
                    }}) as physicalEntities
        }}
        """

        query_network_inputs: LiteralString = """
        CALL {
            WITH networkReactions, networkPhysicalEntities
            MATCH (physicalEntity:PhysicalEntity)
            WHERE
                physicalEntity.dbId IN networkPhysicalEntities AND
                NOT EXISTS {
                    MATCH (physicalEntity)<-[:output]-(reactionLikeEvent:ReactionLikeEvent)
                    WHERE reactionLikeEvent IN networkReactions
                }
            RETURN COLLECT(physicalEntity.dbId) AS networkInputs
        }
        """

        query_network_outputs: LiteralString = """
        CALL {
            WITH networkReactions, networkPhysicalEntities
            MATCH (physicalEntity:PhysicalEntity)
            WHERE
                physicalEntity.dbId IN networkPhysicalEntities AND
                NOT EXISTS {
                    MATCH (physicalEntity)<-[:input]-(reactionLikeEvent:ReactionLikeEvent)
                    WHERE reactionLikeEvent IN networkReactions
                }
            RETURN COLLECT(physicalEntity.dbId) AS networkOutputs
        }
        """

        query: LiteralString = f"""
        {query_reactions_of_interest_subset if self.pathways else ""}
        {query_transitive_closure_of_scenario}
        {filter_reactions_of_interest if self.pathways else ""}
        WITH COLLECT(DISTINCT {_network_reaction}) AS networkReactions
        UNWIND networkReactions AS {_network_reaction}
        {query_network_reaction_inputs}
        {query_network_reaction_outputs}
        {query_network_reaction_enzymes}
        {query_network_reaction_positive_regulators}
        {query_network_reaction_negative_regulators}
        {query_network_reaction_compartments}
        {query_is_network_reaction_reversible}
        {query_expand_reaction_physical_entities_information}
        WITH
            COLLECT({{
                id: {_network_reaction}.dbId,
                physical_entities: physicalEntities,
                compartments: compartments
            }}) AS networkReactionsDetails,
            networkReactions
        UNWIND networkReactionsDetails AS {_network_reaction}
        UNWIND {_network_reaction}.physical_entities AS {_network_physical_entity}
        WITH
            networkReactionsDetails,
            networkReactions,
            apoc.convert.toSet(
                apoc.coll.flatten(
                    COLLECT({_network_physical_entity}.id)
                )
            ) AS networkPhysicalEntities
        {query_network_inputs}
        {query_network_outputs}
        RETURN networkReactionsDetails, networkInputs, networkOutputs
        """

        # query_network_reaction_inputs_which_are_network_inputs: LiteralString = f"""
        # CALL {{
        #     WITH {_network_reaction}, networkReactions
        #     MATCH ({_network_reaction})-[:input]->({_network_physical_entity}:PhysicalEntity)
        #     WHERE NOT EXISTS {{
        #         MATCH ({_network_physical_entity})<-[:output]-(frontierReactionLikeEvent:ReactionLikeEvent)
        #         WHERE frontierReactionLikeEvent IN networkReactions
        #     }}
        #     RETURN COLLECT({_network_physical_entity}.dbId) AS reactionNetworkInputs
        # }}
        # """
        #
        # query_network_reaction_outputs_which_are_network_outputs: LiteralString = f"""
        # CALL {{
        #     WITH {_network_reaction}, networkReactions
        #     MATCH ({_network_reaction})-[:output]->({_network_physical_entity}:PhysicalEntity)
        #     WHERE NOT EXISTS {{
        #         MATCH ({_network_physical_entity})<-[:input]-(frontierReactionLikeEvent:ReactionLikeEvent)
        #         WHERE frontierReactionLikeEvent IN networkReactions
        #     }}
        #     RETURN COLLECT({_network_physical_entity}.dbId) AS reactionNetworkOutputs
        # }}
        # """

        # UNWIND networkReactions AS {_network_reaction}
        # reverse_reaction: reverseReactionLikeEvent,

        # collect_network_reactions: LiteralString = f"""
        # WITH COLLECT(DISTINCT {_network_reaction}) AS networkReactions
        # UNWIND networkReactions AS {_network_reaction}
        # """

        # {query_network_reaction_inputs_which_are_network_inputs}
        # {query_network_reaction_outputs_which_are_network_outputs}
        # COLLECT(reactionNetworkInputs) AS networkInputs,
        # COLLECT(reactionNetworkOutputs) AS networkOutputs;

        records: list[neo4j.Record]
        records, _, _ = neo4j_driver.execute_query(
            query,
            scenario_pathways=list(map(int, self.pathways)),
            scenario_physical_entities=list(map(int, self.physical_entities)),
            ignored_physical_entities=list(
                map(int, self.ignored_physical_entities)
            ),
            max_depth=int(self.max_depth) if self.max_depth else -1,
        )

        def match_role(obj: dict[str, str]) -> Role:
            match obj["role"]:
                case "input" | "output":
                    return StandardRoleInformation(
                        stoichiometry=Stoichiometry(int(obj["stoichiometry"])),
                        role=StandardRole(obj["role"]),
                    )
                case _:
                    return ModifierRole(obj["role"])

        input_physical_entities = set[ReactomeDbId](
            map(ReactomeDbId, itertools.chain(records[0]["networkInputs"]))
        )

        output_physical_entities = set[ReactomeDbId](
            map(ReactomeDbId, itertools.chain(records[0]["networkOutputs"]))
        )

        rows: list[dict[str, Any]] = records[0]["networkReactionsDetails"]
        reaction_like_events: set[ReactionLikeEvent] = {
            ReactionLikeEvent(
                id=ReactomeDbId(reaction["id"]),
                physical_entities={
                    PhysicalEntity(
                        id=ReactomeDbId(obj["id"]),
                        compartments=set(map(Compartment, obj["compartments"])),
                    ): match_role(obj)
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

        # input_physical_entities = (
        #     input_physical_entities - output_physical_entities
        # )
        # input_physical_entities = {1}
        # output_physical_entities = {1}
        # TODO: include in transitive closure reverse reactions!
        # print("| inp |", input_physical_entities, "|")
        # print("| out |", output_physical_entities, "|")
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

        kinetic_constants = set[SId]()
        environment_physical_entities = set[PhysicalEntity]()

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
                    # species.setInitialAmount(0.5)
                    species.setInitialConcentration(0.0)
                    # species.setHasOnlySubstanceUnits(False)

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

                    environment_physical_entities.add(obj)

                    if (
                        obj.id in biological_network.input_physical_entities
                        and obj.id
                        in biological_network.output_physical_entities
                    ):
                        species.setInitialConcentration(0.9)
                    elif obj.id in biological_network.input_physical_entities:
                        frontier_reaction: libsbml.Reaction = (
                            sbml_model.createReaction()
                        )
                        frontier_reaction.setId(f"r_{obj}")
                        frontier_reaction.setReversible(False)
                        frontier_reaction.setFast(False)

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
                            frontier_reaction.createKineticLaw()
                        )
                        input_kinetic_law.setMath(
                            libsbml.parseL3Formula(
                                f"({kinetic_constant.getId()})"
                            )
                        )
                    elif obj.id in biological_network.output_physical_entities:
                        frontier_reaction: libsbml.Reaction = (
                            sbml_model.createReaction()
                        )
                        frontier_reaction.setId(f"r_{obj}")
                        frontier_reaction.setReversible(False)
                        frontier_reaction.setFast(False)

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
                            frontier_reaction.createKineticLaw()
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

                    for physical_entity, role_information in obj.entities():
                        species_ref: libsbml.SpeciesReference
                        match role_information.role:
                            case StandardRole.INPUT:
                                species_ref = sbml_model.createReactant()
                            case StandardRole.OUTPUT:
                                species_ref = sbml_model.createProduct()

                        species_ref.setSpecies(repr(physical_entity))
                        species_ref.setConstant(False)
                        species_ref.setStoichiometry(
                            int(role_information.stoichiometry)
                        )

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

        return BiologicalModel(
            document=sbml_document,
            virtual_patient_generator=VirtualPatientGenerator(
                kinetic_constants
            ),
            environment_generator=EnvironmentGenerator(
                environment_physical_entities
            ),
            constraints=self.constraints,
        )
