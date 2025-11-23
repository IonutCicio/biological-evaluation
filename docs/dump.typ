// , and the parameters $epsilon, delta in (0, 1)$ for the evalation of the constraints

// #box(
//     stroke: (y: .25pt),
//     inset: (y: .5em),
//     width: 100%,
//     [ *Algorithm 1*: eval],
// )
// #box(stroke: (bottom: .25pt), inset: (bottom: 1em))[
//     #indent[
//         *input*: $S_T$, set of #logic[PhysicalEntity]\; \
//         *input*: $P_T$, set of target #logic[Pathway]\; \
//         *input*: $C_T$, set of constraints on $S_T$; \
//         *input*: $epsilon, delta in (0, 1)$; \
//         *input*: seed, random seed; \
//
//         #logic[
//             scenario $<-$ biological_scenario_definition($S_T$, $P_T$, $C_T$)] \
//         #logic[(sbml_model, vp_definition, env) $<-$ yield_sbml_model(scenario)]
//         \
//
//         $V$ = $emptyset$ #logic(text(comment-color)[\/\/ set of virtual
//             patients]) \
//         *while* $not$ halt requested *do* \
//         ~ $v$ $<-$ #logic[instantiate(vp_definition)] #logic(text(
//             comment-color,
//         )[\/\/ virtual patient]) \
//         ~ *if* ( \
//         $quad quad$ $v$ satisfies structural constraints $and$ \
//         $quad quad$ #logic[APSG(sbml_model, $v$, env, seed, $epsilon$, $delta$)]
//         \
//         ~ ) *then* \
//         $quad quad$ $V <- V union { v }$; \
//
//         *return* V
//     ]
// ]

// $S$ $union$ constraints($S$) $union$ $C$ \
// env $<-$ define env for model \
// instantiate
// generate
// biological
// model
// instance

// *input*: horizon?
// EAA()
// ~ model_instance $<-$ model + $v$ \
// ~ env_instance $<-$ random instance of env
// *function* fixed_point($S_T$)

// ```
// ~ test
// ```

// Algorithm

// #proj-name is a tool meant to help study the plausability of a given biological system.
// biological
// system.


// Different scnearios can be compared by comparing the subsets of virtual
// patients obtained from those models.


// #proj-name The software shall take as input the species which I want to expand (backwards reachability), it shall somehow take the as input which section of Reactome we want to confine the backwards reachability to (i.e. cutoff species / reactions?).
// Then, it should generate a model from these reactions (how do I encode the model?)
// == Formalities


// The bulk of the logic is in the #logic[yield_sbml_model()] function.
// The idea is to expand a portion of Reactome


// #definition("SBML model")[
//     A _SBML model_ $G$ is a tuple $(S_T, S, R, E)$ s.t.
//     - $S_T$ the set of target species
//     - $S$ is the finite set of species s.t.
//         - $S_T subset.eq S$
//         - $S$ is the transitive closure of $S_I$ within the Reactome graph (to
//             be more precise, the closure within the specified bounds, bounds yet
//             to be defined)
//         - $S' = S union {s_"avg" | s in S }$.
//         - $accent(s, dot) = f(s_1, s_2, s_3, ..., s_n)$
//     - $R$ is the finite set of reactions
//         - $R = R_"fast" union R_"slow"$
//     - $E$ is the set edges in the graph (where and edge goes from a species to a
//         reaction, it also has a stoichiometry)
//         - $E subset.eq S times R times NN^1$
//         - $E = E_"reactant" union E_"product" union E_"modifier"$
// ]

// #let proj-name = text(font: "LMMonoCaps10", "Bsys_eval")
// heading(numbering: none, outlined: false, text(size: 2em, proj-name))
//
// proj-name is a tool meant to help study the likelihood of a given scenario in a
// biological system.

// = proj-name


// == Requirements
//
// The basic idea behind the software is to take the description of a scenario
// (with _target species_, _target pathways_ and ordering constraints on the
// _target species_), to generate a SBML model with
// - the reactions within the _target pathways_ that, both directly and indirectly,
//     generate the _target species_
// - parameters for the speeds of the reactions
// - constraints on the quantities of the species _(for which the model needs to be
//     simulated)_
//
```python
# half_saturation_constant.setId(f"k_h_{modifier_id}_{reaction}")
# half_saturation_constant.setConstant(True)
# half_saturation_constant.setValue(0.0)
# kinetic_constants.add(half_saturation_constant.getId())

# kinetic_constants = set[SId]()

# forward_kinetic_constant.setId(f"k_f_{reaction}")
# forward_kinetic_constant.setValue(0.0)
# forward_kinetic_constant.setConstant(True)
# kinetic_constants.add(forward_kinetic_constant.getId())

# TODO: set the species (HUMAN) of the entities! Otherwise you look for other stuff

# network=physical_entities | reaction_like_events | compartments,
# tuple[ReactomeDbId, ReactomeDbId]
# print(ConstantTypology("reaction_speed"))
# print(ConstantTypology("ciao"))

# for parameter in document.getModel().getListOfParameters():
#     print(parameter)
#     print(
#         parameter.getAnnotationString()
#         .replace("<annotation>", "")
#         .replace("</annotation>", "")
#     )

# reachable
# biochemical
# network
# biological
# model

# kinetic_constants=
#
# {
#     parameter.getId(): Constant(
#         parameter.getAnnotationString()
#         .replace("<annotation>", "")
#         .replace("</annotation>", "")
#     )
#     for parameter in document.getModel().getListOfParameters()
#     if parameter.getId().startswith("k_")
# },
# species_order={
#     (PhysicalEntity(species_1), PhysicalEntity(species_2))
#     for species_1, species_2 in orders["species_order"]
# },
# kinetic_constants_order={
#     (kinetic_constant_1, kinetic_constant_2)
#     for kinetic_constant_1, kinetic_constant_2 in orders[
#         "kinetic_constants_order"
#     ]
# },

# libsbml.XMLNode.convertXMLNodeToString(
#     document.getModel()
#     .getAnnotation()
#     .getChild(0)
#     .getChild(0)
#     .getChild(0)
# ).replace("&quot;", '"')

# p: libsbml.Parameter = document.getModel().createParameter()
# node = document.create
# p.setNotes("ciao")
# p.setAnnotation("hola soy dora")
# print(p.getNotes())
# print(
#     p.getAnnotationString()
#     .replace("<annotation>", "")
#     .replace("</annotation>", "")
# )
# exit()
# -20, 0.0 if kinetic_constant.startswith("k_s_") else 20.0

# kinetic_constants = kinetic_constants | reaction_kinetic_constants
# for obj in reachable_biochemical_network.network:
# match obj:
#     case Compartment():

# case PhysicalEntity():
# case ReactionLikeEvent():

# list(
#     map(lambda x: list(map(int, x)), self.constraints)
# ),


# constraints_node: libsbml.XMLNode = (
#     libsbml.XMLNode.convertStringToXMLNode()
# )
#
# rdf: libsbml.XMLNode = libsbml.RDFAnnotationParser.createRDFAnnotation()
# _ = rdf.addChild(constraints_node)
# node: libsbml.XMLNode = libsbml.RDFAnnotationParser.createAnnotation()
# _ = node.addChild(rdf)
# f"""
#     {{
#         "kinetic_constants_constraints": [{", ".join(f"[{left}, {right}]" for (left, right) in kinetic_constants_constraints)}],
#         "physical_entities_constraints": [{", ".join(f"[{int(left)}, {int(right)}]" for (left, right) in self.constraints)}]
#     }}
# """


# rr.setIntegrator("rk45")

# is_species_re: re.Pattern[str] = re.compile(r"^\[s_\d+\]$")
# is_species_re.match(column_name)
# and "k_" + column_name[1:-1] not in virtual_patient
# in biological_model.other_parameters


# ORCHESTRATOR_URL: str = f"http://{os.getenv('VM_HOST')}:8080/"

# transfer_learning_history=[],
# advisor_type=os.getenv("ADVISOR_TYPE", default="default"),
# surrogate_type="gp",
# task_id="parallel_async",
# task_id = buckpass.openbox_api.register_task(
#     config_space=_space,
#     server_ip="localhost",
#     port=8000,
#     email=str(os.getenv("OPENBOX_EMAIL")),
#     password=str(os.getenv("OPENBOX_PASSWORD")),
#     task_name=filepath,
#     num_objectives=int(num_objectives),
#     num_constraints=0,
#     advisor_type=os.getenv("ADVISOR_TYPE", default="default"),
#     sample_strategy=os.getenv("SAMPLE_STRATEGY", default="bo"),
#     surrogate_type=os.getenv("SURROGATE_TYPE", default="prf"),
#     acq_type=os.getenv("ACQ_TYPE", default="mesmo"),
#     acq_optimizer_type=os.getenv(
#         "ACQ_OPTIMIZER_TYPE", default="random_scipy"
#     ),
#     parallel_type="async",
#     initial_runs=0,
#     random_state=1,
#     active_worker_num=int(os.getenv("RANDOM_STATE", default="1")),
#     max_runs=max_runs,
# )

# num_objectives = (
#     biological_model.sbml_document.getModel().getNumSpecies()
#     - len(
#         {
#             kinetic_constant
#             for kinetic_constant in biological_model.kinetic_constants
#             if re.match(r"k_s_\d+", kinetic_constant)
#         }
#     )
# ) * 2
```
