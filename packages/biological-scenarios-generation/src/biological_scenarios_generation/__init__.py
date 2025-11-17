# kinetic_constant: 10 ** random.uniform(-20, 0)
# if "half" in kinetic_constant or "k_h_" in kinetic_constant
# else 10 ** random.uniform(-20, 20)
# for kinetic_constant in self.kinetic_constants

# """Check if a value is contained within a the interval."""
# formula_reverse_reaction: str = ""
# virtual_patient_generator=VirtualPatientGenerator(
# ),
# network_reactions_metadata: LiteralString = "networkReactionsMetadata"
# from enum import Enum, auto

# class BaseKineticLaw(Enum):
#     LAW_OF_MASS_ACTION = auto()
#     CONVENIENCE_KINETIC_LAW = auto()
#
#     def __call__(
#         self, sbml_model: libsbml.Model, reaction: ReactionLikeEvent
#     ) -> tuple[MathML, set[SId]]:
#
#             case BaseKineticLaw.CONVENIENCE_KINETIC_LAW:
#                 return ("", set[SId]())
# CustomKineticLaw: TypeAlias = Callable[
#     [libsbml.Model, ReactionLikeEvent], tuple[MathML, set[SId]]
# ]
# KineticLaw: TypeAlias = BaseKineticLaw | CustomKineticLaw

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

# virtual_patient_generator=VirtualPatientGenerator(
#     {
#         parameter.getId()
#         for parameter in sbml_model.getListOfParameters()
#         if "time" not in parameter.getId()
#         and "mean" not in parameter.getId()
#     }
# ),

# virtual_patient_generator: VirtualPatientGenerator


# @dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
# class VirtualPatientGenerator:
#     kinetic_constants: set[SId]
# class NormalizedReal(float):
#     """float in [0, 1]."""
#
#     def __new__(cls, value: float) -> Self:
#         assert Interval(0, 1).contains(value)
#         return super().__new__(cls, value)

# TODO: produced_by attribute of physical entities of network reaction
# TODO: include reverse reactions in network, even if they are not in transitive closure

# standard
# chemical
# partecipant
# species
# entity

# modifier
# metadata
# category
# information

# POSITIVE_GENE_REGULATOR = auto()
# NEGATIVE_GENE_REGULATOR = auto()

# kinetic_constants: dict[SId, KineticConstantPurpose]

# species.setInitialAmount(0.5)
# species.setHasOnlySubstanceUnits(False)
# input_physical_entities = (
#     input_physical_entities - output_physical_entities
# )
# input_physical_entities = {1}
# output_physical_entities = {1}
# TODO: include in transitive closure reverse reactions!
# print("| inp |", input_physical_entities, "|")
# print("| out |", output_physical_entities, "|")

# problem
# biological
# network
# satisfiability
# model
# constraints
# physical_entities

# when looking at a reactions outputs, let's say which are the modified reactions of that output
# so each physical entity has attached the "modified reactions" set, this way I can say
# if reaction1 < reaction2 "if parameter1 matches pattern of reaction1 and and parameter2 matches pattern of reaction2, then parameter1 < parameter2"


# return {
#     kinetic_constant: pow(
#         10,
#         (
#             random.uniform(-20, 0)
#             if purpose == KineticConstantPurpose.HALF_SATURATION
#             else random.uniform(-20, 20)
#         ),
#     )
#     for kinetic_constant, purpose in self.kinetic_constants.items()
# }

# return f"species_{super().__repr__()}"
# return f"compartment_{super().__repr__()}"
# return f"reaction_{super().__repr__()}"
# Role is not enough, I need to know if it's input or not, but it's not related to all reactions, just to model!
# Interesting... I still need to save the info somewhere
# Maybe I should go back to the drawing board for a moment


# virtual_patient_details.extend(
#         map(lambda parameter: parameter.getId(), parameters)
# )
# for l3_formula in self.constraints:
#     constraint: libsbml.Constraint = sbml_model.createConstraint()
#     constraint.setId("constraint_test")
#     constraint.setMath(libsbml.parseL3Formula(l3_formula))


# time_param: libsbml.Parameter = sbml_model.createParameter()
# time_param.setId("t_time")
# time_param.setConstant(False)
# time_param.setValue(0.0)
#
# time_rule: libsbml.Rule = sbml_model.createRateRule()
# time_rule.setVariable("t_time")
# time_rule.setFormula("1")

# class FromSBMLDocument(ABC):
#     @abstractmethod
#     # @classmethod
#     def from_document(cls, document: libsbml.SBMLDocument) -> Self:
#         pass

# @override
# @classmethod
# species: set[Parameter]


# compartment.appendNotes(
#     f'<body xmlns="http://www.w3.org/1999/xhtml"><p>{obj.display_name}</p></body>',
# )

# _ = driver.execute_query(
#     """
#     MATCH (targetReactionLikeEvent:TargetReactionLikeEvent)
#     REMOVE targetReactionLikeEvent:TargetReactionLikeEvent;
#     """
# )

# enzymes
# | reaction_like_event.positive_regulators
# | reaction_like_event.negative_regulators
# | set(
#     map(
#         attrgetter("physical_entity"),
#         reaction_like_event.physical_entities,
#     )
# )


# else:
#     records, _, _ = driver.execute_query(
#         query_reaction_like_events_in_transitive_closure,
#         # + expand_reaction_like_events,
#         max_level=self.max_depth or -1,
#         target_physical_entities=target_physical_entities,
#     )

# PhysicalEntity.ModifierFunction.ENZYME
# PhysicalEntityReactionLikeEvent(
#     physical_entity=PhysicalEntity(
#         e["id"],
#         compartments={
#             Compartment(**c) for c in e["compartments"]
#         },
#     ),
#     stoichiometry=e["stoichiometry"],
#     type=PhysicalEntityReactionLikeEvent.Type.INPUT,
# )

# | {
#     PhysicalEntityReactionLikeEvent(
#         physical_entity=PhysicalEntity(e["id"]),
#         stoichiometry=Stoichiometry(e["stoichiometry"]),
#         type=PhysicalEntityReactionLikeEvent.Type.OUTPUT,
#     )
#     for e in reaction["reactants"]
# },

# [k for k, v in reaction_like_event.physical_entities.items() if v instanceof PhysicalEntity.ModifierFunction],
# if reaction_like_event.is_fast:
#     pass
# formula = f"{formula_forward_reaction}{formula_reverse_reaction}{formula_hill_component}"
# parameters

# is_fast: bool = field(default=False)
# """Open real interval."""
# """int >= 0."""
# """int > 0."""


# @dataclass
# class BiologicalNumber:
#     id: int
#     properties: str
#     organistm: str
#     value: Interval | float | None
#     units: str
#     keywords: set[str]


# @dataclass(frozen=True)
# class Parameter:
#     parameter: libsbml.Parameter
#
#     @override
#     def __hash__(self) -> int:
#         return self.parameter.getId().__hash__()
#
#     @override
#     def __eq__(self, value: object, /) -> bool:
#         return isinstance(value, Parameter) and self.parameter.getId().__eq__(
#             value.parameter.getId(),
#         )


# function
# in
# reaction

# class Modifier(Enum):
#     ENZYME = 0
#     POSITIVE_REGULATOR = 1
#     NEGATIVE_REGULATOR = 2
#     POSITIVE_GENE_REGULATOR = 3
#     NEGATIVE_GENE_REGULATOR = 4


# class PhysicalEntityReaction:
#


# (Enum):
#     INPUT = 1
#     OUTPUT = 2
#     ENZYME = 3
#     POSITIVE_REGULATOR = 4
#     NEGATIVE_REGULATOR = 5


# class Type(Enum):
#     INPUT = 1
#     OUTPUT = 2

# @dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
# class PhysicalEntityReactionLikeEvent:
#     class Type(Enum):
#         INPUT = 1
#         OUTPUT = 2
#
#     stoichiometry: Stoichiometry
#     type: Type

# physical_entity: PhysicalEntity
# @override
# def __hash__(self) -> int:
#     return self.physical_entity.__hash__()
#
# @override
# def __eq__(self, value: object, /) -> bool:
#     return isinstance(
#         value, PhysicalEntityReactionLikeEvent
#     ) and self.physical_entity.__eq__(value.physical_entity)
# @override
# def __repr__(self) -> str:
#     return f"({self.physical_entity}^{self.stoichiometry})"

# physical_entities: set[PhysicalEntityReactionLikeEvent]
# physical_entities: dict[PhysicalEntity, PhysicalEntityReactionLikeEvent]
# enzymes: set[PhysicalEntity] = field(default_factory=set)
# positive_regulators: set[PhysicalEntity] = field(default_factory=set)
# negative_regulators: set[PhysicalEntity] = field(default_factory=set)
# @cache
# def reactants(self) -> set[PhysicalEntityReactionLikeEvent]:
#     return {
#         relationship
#         for relationship in self.physical_entities
#         if relationship.type == PhysicalEntityReactionLikeEvent.Type.INPUT
#     }
#
# @cache
# def products(self) -> set[PhysicalEntityReactionLikeEvent]:
#     return self.physical_entities - self.reactants()

# for reaction in reaction_like_events:
#     print(reaction.id)
#     print(reaction.is_reversible)
#     print("compartments", list(reaction.compartments))
#     print(*[item for item in reaction.physical_entities.items()])

# (
# (
#     p["stoichiometry"],
#     PhysicalEntity.ReactionFunction.OUTPUT,
# )
# )

# compartments={Compartment(c) for c in reaction["compartments"]},
# {
#     Compartment(c) for c in p["compartments"]
# },
# match PhysicalEntity.ReactionFunction(p["function"])
#     case _:
#         (p["stoichiometry"],PhysicalEntity.ReactionFunction.OUTPUT)
# (
#     p["stoichiometry"],
#     # PhysicalEntity.ReactionFunction.OUTPUT,
# )

# print("physical entities", list(reaction.physical_entities))
# print(reaction_like_events)
# exit()
# | {
#     PhysicalEntity(
#         id=p["id"],
#         compartments={
#             Compartment(**c) for c in p["compartments"]
#         },
#     ): (
#         p["stoichiometry"],
#         PhysicalEntity.ReactionFunction.INPUT,
#     )
#     for p in reaction["reactants"]
# },
# enzymes={
#     PhysicalEntity(
#         ReactomeDbId(entity["id"]),
#         compartments={
#             Compartment(**c) for c in entity["compartments"]
#         },
#     )
#     for entity in reaction["enzymes"]
# },
# positive_regulators={
#     PhysicalEntity(**p) for p in reaction["positive_regulators"]
# },
# negative_regulators={
#     PhysicalEntity(**p) for p in reaction["negative_regulators"]
# },

# return set()

# physical_entities: set[tuple[PhysicalEntity, PhysicalEntity.Function]] {
#         for physical_entity, function   in self.physical_entities.items()
#         if isinstance(function, tuple[Stoichiometry, PhysicalEntity.SimpleFunction])
#         }
#
# return {
#     # (physical_entity, physical_entity_function[0])
#     # for physical_entity, physical_entity_function in self.physical_entities.items()
#     # if isinstance(physical_entity_function, tuple[Stoichiometry, PhysicalEntity.SimpleFunction]) and (x, y) = physical_entity_function
# }

# (
#     stoichiometry,
# )
# StandardFunctionInformation: TypeAlias = tuple[
#     Stoichiometry, StandardFunction
# ]

# class Reaction
# @dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
# class SimpleFunctionData:
#     stoichiometry: Stoichiometry
#     function: SimpleFunction


# if(sbo == SBO_ACTIVATOR || sbo == SBO_ENZYME || sbo == SBO_STIMULATOR) {
#     return create_hill_pos_function(model, modifier, h, kinetic_constant_added);
# } else if(sbo == SBO_INHIBITOR) {
#     return create_hill_neg_function(model, modifier, h, kinetic_constant_added);
# } else {
#     eprintf("[FATAL ERROR] the modifier is not an activator on an inhibitor, SBO: %d\n", sbo);
#     exit(5);
# }
#
# std::string create_hill_pos_function(libsbml::Model *model, libsbml::ModifierSpeciesReference *modifier, u_int h, int *kinetic_constant_added) {
#     assert(h > 0);
#     std::string param_k_regulator = "k_activator_"+modifier->getId();
#     libsbml::Parameter *p = model->createParameter();
#     p->setId(param_k_regulator);
#     p->setValue(1.0);
#     p->setConstant(true);
#     *kinetic_constant_added += 1;
#     if(h == 1) {
#         return "(("+ modifier->getSpecies() +")/("+param_k_regulator+"+"+modifier->getSpecies()+"))";
#     } else {
#         std::string h_str = std::to_string(h);
#         return "(("+ modifier->getSpecies() +"^"+h_str+")/(("+param_k_regulator+"^"+h_str+")+("+modifier->getSpecies()+"^"+h_str+")))";
#     }
#
# }
#
# std::string create_hill_neg_function(libsbml::Model *model, libsbml::ModifierSpeciesReference *modifier, u_int h, int *kinetic_constant_added) {
#     assert(modifier->getSBOTerm() == SBO_INHIBITOR);
#     assert(h > 0);
#     std::string param_k_regulator = "k_inhibitor_"+modifier->getId();
#     libsbml::Parameter *p = model->createParameter();
#     p->setId(param_k_regulator);
#     p->setConstant(true);
#     p->setValue(1.0);
#     *kinetic_constant_added += 1;
#     if(h == 1) {
#         return "(("+ param_k_regulator +")/("+param_k_regulator+"+"+modifier->getSpecies()+"))";
#     } else {
#         std::string h_str = std::to_string(h);
#         return "(("+ param_k_regulator +"^"+h_str+")/(("+param_k_regulator+"^"+h_str+")+("+modifier->getSpecies()+"^"+h_str+")))";
#     }
# }


# reaction_enzymes: set[PhysicalEntity] = {
#     physical_entity
#     for physical_entity, function in reaction_like_event.physical_entities.items()
#     if function == PhysicalEntity.ModifierFunction.ENZYME
# }
#
# reaction_positive_regulators

# if reaction_like_event.enzymes:
#     hill_component = "1"
#
# if reaction_like_event.positive_regulators:
#     pass
#
# if reaction_like_event.negative_regulators:
#     pass

# formula = f"{forward_reaction_formula}"

# if reverse_reaction_formula:

# if hill_component:
# formula = f"{hill_component} * {formula}"

# virtual_patient_parameters = set[SId]()
# for parameter in sbml_model.getListOfParameters():
#     virtual_patient_parameters.add(parameter.getId())
#
# environment_physical_entities = set[PhysicalEntity]()
# for physical_entity in sbml_model.getListOfSpecies():
#     environment_physical_entities.add(physical_entity.getId())


# parameters: list[libsbml.Parameter]
# @staticmethod
# def load_document(
#     document: libsbml.SBMLDocument,
# ) -> "VirtualPatientDetails":
#     return VirtualPatientDetails(set())
#


# scenario
# model
# definition
# extract
# loading
# upload
# generation
# consume
# generate
# loading

# class ForwardReactionParameter:
#     reaction_like_event:

# import argparse
# from enum import Enum
# from pathlib import Path
#
# import libsbml
# import neo4j
# import roadrunner
# from biological_scenarios_generation.core import Interval
# from biological_scenarios_generation.generation import (
#     BiologicalScenarioDefinition,
#     Environment,
#     VirtualPatientDetails,
# )
# from biological_scenarios_generation.reactome import (
#     Pathway,
#     PhysicalEntity,
#     ReactomeDbId,
# )
# from packages.buckpass.buckpass.core.fixed_batch_policy import FixedBatchPolicy
# from packages.buckpass.src.buckpass import openbox_api
#
# from blackbox import blackbox
#
# # from packages.buckpass.buckpass.openbox_api import (
# #     URL,
# #     get_suggestion,
# #     update_observation,
# # )
#
#
#
#
#
# class Activity(Enum):
#     GENERATE_DOCUMENT = 0
#     SIMULATE_DOCUMENT = 1
#     ORCHESTRATE_WORKERS = 2
#
#
# def generate_document() -> None:
#     """Find virtual patients for a simple biological scenario."""
#     nitric_oxide = PhysicalEntity(
#         ReactomeDbId(202124),
#         Interval(0.000178, 0.00024),
#     )
#     signal_transduction = Pathway(ReactomeDbId(162582))
#     immune_system = Pathway(ReactomeDbId(168256))
#     adenosine_triphsphate = PhysicalEntity(ReactomeDbId(113592))
#     adenosine_diphsphate = PhysicalEntity(ReactomeDbId(29370))
#
#     biological_scenario_definition: BiologicalScenarioDefinition = (
#         BiologicalScenarioDefinition(
#             target_physical_entities={nitric_oxide},
#             target_pathways={
#                 signal_transduction,
#                 immune_system,
#             },
#             excluded_physical_entities={
#                 adenosine_triphsphate,
#                 adenosine_diphsphate,
#             },
#             constraints=[],
#             max_depth=None,
#         )
#     )
#
#     with neo4j.GraphDatabase.driver(
#         uri=NEO4J_URL_REACTOME,
#         auth=AUTH,
#         database=REACTOME_DATABASE,
#     ) as driver:
#         driver.verify_connectivity()
#
#         sbml_document: libsbml.SBMLDocument
#         (sbml_document, _, _) = biological_scenario_definition.yield_sbml_model(
#             driver,
#         )
#
#     with Path("x.sbml").open("w") as file:
#         _ = file.write(libsbml.writeSBMLToString(sbml_document))
#
#
# OPENBOX_URL = openbox_api.URL(host="open-box", port=8000)
#
#
# def simulate_document() -> None:
#
#     argument_parser = argparse.ArgumentParser()
#     _ = argument_parser.add_argument("openbox_task_id")
#     openbox_task_id = str(argument_parser.parse_args().openbox_task_id)
#
#     config_dict = openbox_api.get_suggestion(
#         url=OPENBOX_URL,
#         task_id=openbox_task_id,
#     )
#
#     with Path("x.sbml").open("r") as file:
#         sbml_str: str = file.read()
#
#     config = Configuration(townsend_cs, config_dict)
#     observation = blackbox(config)
#
#
#     start_time = datetime.datetime.now(tz=datetime.UTC)
#     trial_info = {
#         "cost": (datetime.datetime.now(tz=datetime.UTC) - start_time).seconds,
#         "worker_id": getenv("SLURM_JOB_ID"),
#         "trial_info": None,
#     }
#     openbox_api.update_observation(
#         url=OPENBOX_URL,
#         task_id=openbox_task_id,
#         config_dict=config_dict,
#         objectives=observation["objectives"],
#         constraints=[],
#         trial_info=trial_info,
#         trial_state=SUCCESS,
#     )
#
#     # virtual_patients = []
#     # for _ in range(1):VirtualPatient
#     #     virtual_patient: VirtualPatient = virtual_patient_details()
#     #
#     #     if is_virtual_patient_valid(rr, virtual_patient, environment):
#     #         virtual_patients.append(virtual_patient)
#     # print(len(virtual_patients))
#
#
#
# def orchestrate_workers() -> None:
#     townsend_params = {"float": {"x1": (-2.25, 2.5, 0), "x2": (-2.5, 1.75, 0)}}
#     townsend_cs = ConfigurationSpace()
#     townsend_cs.add_hyperparameters(
#         [
#             UniformFloatHyperparameter(e, *townsend_params["float"][e])
#             for e in townsend_params["float"]
#         ],
#     )
#
#     remote_advisor: RemoteAdvisorDebug = RemoteAdvisorDebug(
#         config_space=townsend_cs,
#         server_ip="open-box",
#         port=8000,
#         email="test@test.test",
#         password="testtest",
#         task_name=f"test_task_{datetime.datetime.now(tz=datetime.UTC).strftime('%Y-%m-%d_%H:%M:%S')}",
#         num_objectives=1,
#         num_constraints=0,
#         sample_strategy="bo",
#         surrogate_type="gp",
#         acq_type="ei",
#         max_runs=100,
#     )
#
#     worker_policy = FixedBatchPolicy(
#         args=remote_advisor.task_id,
#         pool_size=IntGEZ(100),
#         submitter=DockerSlurmSubmitter(),
#     )
#
#
# def main() -> None:
#     argument_parser = argparse.ArgumentParser()
#     _ = argument_parser.add_argument("openbox_task_id")
#     openbox_task_id = str(argument_parser.parse_args().openbox_task_id)
#
#
# if __name__ == "__main__":
#     main()
#

# @dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
# class _ModelEntities:
#     reactions: set[ReactionLikeEvent]
#     compartments: set[Compartment]
#     physical_entities: set[PhysicalEntity]
#     input_physical_entities: set[PhysicalEntity]
# physical_entity: PhysicalEntity
# @override
# def __hash__(self) -> int:
#     return self.physical_entity.__hash__()
# @override
# def __eq__(self, value: object, /) -> bool:
#     return isinstance(
#         value, BiologicalScenarioDefinition._NetworkPhysicalEntity
#     ) and self.physical_entity.__eq__(value.physical_entity)

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

# query_is_network_reaction_reversible: LiteralString = f"""
# CALL {{
#     WITH {_network_reaction}
#     OPTIONAL MATCH ({_network_reaction})-[:reverseReaction]->(reverseReactionLikeEvent)
#     RETURN reverseReactionLikeEvent
# }}
# """

# {query_is_network_reaction_reversible}
# filter_reactions_of_interest: LiteralString = (
#     f"WHERE {_network_reaction} IN reactionsOfInterest"
# )

# def query_network_reaction_regulators(
#     label: LiteralString, role: LiteralString, collection: LiteralString
# ) -> LiteralString:
#     return f"""
#     CALL {{
#         WITH {_network_reaction}
#         MATCH ({_network_reaction})-[:regulatedBy]->(:{label})-[:regulator]->({_network_physical_entity}:PhysicalEntity)
#         RETURN
#             COLLECT({{
#                 physicalEntity: {_network_physical_entity},
#                 role: "{role}"
#             }}) AS {collection}
#     }}
#     """

# query_network_reaction_positive_regulators: LiteralString = (
#     query_network_reaction_regulators(
#         label="PositiveRegulation",
#         role="positive_regulator",
#         collection="positiveRegulators",
#     )
# )
#
# query_network_reaction_negative_regulators: LiteralString = (
#     query_network_reaction_regulators(
#         label="NegativeRegulation",
#         role="negative_regulator",
#         collection="negativeRegulators",
#     )
# )
# positiveRegulators + negativeRegulators

# {query_network_reaction_positive_regulators}
# {query_network_reaction_negative_regulators}

# query_network_reaction_outputs: LiteralString = f"""
# CALL {{
#     WITH {_network_reaction}
#     MATCH ({_network_reaction})-[relationship:output]->({_network_physical_entity}:PhysicalEntity)
#     RETURN
#         COLLECT({{
#             physicalEntity: {_network_physical_entity},
#             stoichiometry: relationship.stoichiometry,
#             role: "output"
#         }}) AS outputs
# }}
# """

# {query_network_reaction_outputs}


# environment_generator=EnvironmentGenerator(
#     environment_physical_entities
# ),

# EnvironmentGenerator,
# """Well known kinetic laws."""
# """Return reaction law and generate parameters."""

# from enum import StrEnum, auto
# class KineticConstantPurpose(StrEnum):
#     HALF_SATURATION = auto()
#     FORWARD_REACTION = auto()
#     REVERSE_REACTION = auto()


# environment_physical_entities.add(obj)

# environment_generator=EnvironmentGenerator(
#     {
#         physical_entity.getId()
#         for physical_entity in sbml_model.getListOfSpecies()
#     }
# ),

# Environment: TypeAlias = dict[SId, NormalizedReal]

# @dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
# class EnvironmentGenerator:
#     """An environment dictates the initial conditions of the simulation (initial amounts of the species)."""
#
#     physical_entities: set[PhysicalEntity]
#
#     def __call__(self) -> Environment:
#         return {
#             repr(physical_entity): NormalizedReal(random.uniform(0, 1))
#             for physical_entity in self.physical_entities
#         }

# environment_generator: EnvironmentGenerator


# ReactionLikeEvent,
# """A virtual patient is described by the set of kinetic."""
