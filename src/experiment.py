import os
from pathlib import Path

import libsbml
import neo4j
from biological_scenarios_generation.core import IntGTZ
from biological_scenarios_generation.model import BiologicalModel
from biological_scenarios_generation.reactome import (
    Pathway,
    PhysicalEntity,
    ReactomeDbId,
)
from biological_scenarios_generation.scenario import (
    BiologicalScenarioDefinition,
)
from neo4j.exceptions import ServiceUnavailable

from core.blackbox import objective_function_multi_objective, plot
from core.lib import init, openbox_config_multiobjective

_, logger = init()


def main() -> None:
    signal_transduction = Pathway(id=ReactomeDbId(162582))
    nitric_oxide = PhysicalEntity(id=ReactomeDbId(202124))
    cyclic_amp = PhysicalEntity(id=ReactomeDbId(30389))
    adenosine_triphsphate = PhysicalEntity(id=ReactomeDbId(113592))
    adenosine_diphsphate = PhysicalEntity(id=ReactomeDbId(29370))

    biological_scenario_definition: BiologicalScenarioDefinition = (
        BiologicalScenarioDefinition(
            physical_entities={nitric_oxide, cyclic_amp},
            pathways={signal_transduction},
            excluded_physical_entities={
                adenosine_triphsphate,
                adenosine_diphsphate,
            },
            constraints={(nitric_oxide, cyclic_amp)},
            max_depth=IntGTZ(2),
        )
    )

    filename = Path(f"{Path(__file__).stem}.sbml")

    try:
        with neo4j.GraphDatabase.driver(
            uri=os.getenv("REACTOME_URL", default=""),
            auth=(
                os.getenv("REACTOME_USERNAME", default=""),
                os.getenv("REACTOME_PASSWORD", default=""),
            ),
            database=os.getenv("REACTOME_DATABASE"),
        ) as driver:
            driver.verify_connectivity()
            biological_model = (
                biological_scenario_definition.generate_biological_model(driver)
            )

        with filename.open("w") as file:
            _ = file.write(
                libsbml.writeSBMLToString(biological_model.sbml_document)
            )
    except ServiceUnavailable:
        assert filename.exists()
        assert filename.is_file()

        sbml_document: libsbml.SBMLDocument = libsbml.readSBML(filename)
        biological_model: BiologicalModel = BiologicalModel.load(sbml_document)
    # exit()

    virtual_patient = biological_model()
    kinetic_constants = {
        "k_consumption_reaction_species_111294": -3.383393426368393,
        "k_consumption_reaction_species_202124": -14.628761149027586,
        "k_consumption_reaction_species_29356": -2.920354876655381,
        "k_consumption_reaction_species_29366": -18.320619359990737,
        "k_consumption_reaction_species_29968": -9.926029745901985,
        "k_consumption_reaction_species_30389": -13.300479621125936,
        "k_half_saturation_species_111865_reaction_111930": -3.571008297698409,
        "k_half_saturation_species_1497830_reaction_202127": 14.477588523079405,
        "k_half_saturation_species_163622_reaction_392129": -18.42084805278949,
        "k_half_saturation_species_164358_reaction_5610727": 15.332729945868557,
        "k_half_saturation_species_170655_reaction_170676": -8.814861403959844,
        "k_half_saturation_species_170665_reaction_111930": 2.621957345801377,
        "k_half_saturation_species_392049_reaction_392129": -15.159792920689581,
        "k_half_saturation_species_396910_reaction_392129": 17.56622317010514,
        "k_half_saturation_species_5610577_reaction_5610727": 14.835350078113606,
        "k_half_saturation_species_5610579_reaction_5610727": -10.092448357062755,
        "k_half_saturation_species_5693375_reaction_202127": 12.629495564313828,
        "k_half_saturation_species_74294_reaction_111930": -6.232220822328976,
        "k_production_reaction_species_113592": -13.00167585725755,
        "k_production_reaction_species_29364": -12.184781486073813,
        "k_production_reaction_species_29368": -12.59112771850305,
        "k_production_reaction_species_29468": -12.138575861270716,
        "k_production_reaction_species_70106": -15.913681630092489,
        "k_reaction_111930": 7.600394708822883,
        "k_reaction_170676": -13.52729400263678,
        "k_reaction_202127": 19.79219259694281,
        "k_reaction_392129": -5.886432458934859,
        "k_reaction_5610727": -14.06840430059594,
        "k_species_111865": -6.06197067973268,
        "k_species_1497830": -15.846879773763154,
        "k_species_163622": -18.20326144459247,
        "k_species_164358": -8.227159546480161,
        "k_species_170655": -11.208242693753167,
        "k_species_170665": -16.832639232286667,
        "k_species_392049": -1.4026162723039413,
        "k_species_396910": -1.6500825680241036,
        "k_species_5610577": -3.4655248606601994,
        "k_species_5610579": -8.52253658231885,
        "k_species_5693375": -13.44500084118787,
        "k_species_74294": -4.428266838957356,
    }
    # {
    #     "k_consumption_reaction_species_111294": 14.431382471352798,
    #     "k_consumption_reaction_species_202124": 19.595923086733542,
    #     "k_consumption_reaction_species_29356": 0.888788982428963,
    #     "k_consumption_reaction_species_29366": 18.16979676123539,
    #     "k_consumption_reaction_species_29968": -7.799687458256868,
    #     "k_consumption_reaction_species_30389": 15.733758494265004,
    #     "k_half_saturation_species_111865_reaction_111930": 7.292478946286025,
    #     "k_half_saturation_species_1497830_reaction_202127": 2.08965218807322,
    #     "k_half_saturation_species_163622_reaction_392129": 1.8522765509973738,
    #     "k_half_saturation_species_164358_reaction_5610727": -6.0333762695868955,
    #     "k_half_saturation_species_170655_reaction_170676": 17.890865138805175,
    #     "k_half_saturation_species_170665_reaction_111930": 16.853729684163703,
    #     "k_half_saturation_species_392049_reaction_392129": -9.768048053572155,
    #     "k_half_saturation_species_396910_reaction_392129": 12.094445805834525,
    #     "k_half_saturation_species_5610577_reaction_5610727": 7.372873251177765,
    #     "k_half_saturation_species_5610579_reaction_5610727": 7.260144836184498,
    #     "k_half_saturation_species_5693375_reaction_202127": -19.377178153668538,
    #     "k_half_saturation_species_74294_reaction_111930": -3.9929995309157853,
    #     "k_production_reaction_species_113592": -14.456703906567832,
    #     "k_production_reaction_species_29364": -15.537688121594844,
    #     "k_production_reaction_species_29368": -17.539874708515654,
    #     "k_production_reaction_species_29468": -16.401943615642665,
    #     "k_production_reaction_species_70106": -9.10815380890905,
    #     "k_reaction_111930": -12.626711841297041,
    #     "k_reaction_170676": -16.49025877598026,
    #     "k_reaction_202127": -11.499766479424771,
    #     "k_reaction_392129": -8.83834115087696,
    #     "k_reaction_5610727": 16.894102811535433,
    #     "k_species_111865": -1.8292904825554537,
    #     "k_species_1497830": -17.988275948729587,
    #     "k_species_163622": -19.480490648589093,
    #     "k_species_164358": -19.85276213845687,
    #     "k_species_170655": -12.469887089342542,
    #     "k_species_170665": -4.0969799745185025,
    #     "k_species_392049": -8.908777394911503,
    #     "k_species_396910": -12.034050204988148,
    #     "k_species_5610577": -8.78620840125405,
    #     "k_species_5610579": -10.682418342269147,
    #     "k_species_5693375": -5.51451202989578,
    #     "k_species_74294": -16.93212990333383,
    # }

    _, num_objectives, _ = openbox_config_multiobjective(biological_model)
    logger.info(
        objective_function_multi_objective(biological_model, num_objectives)(
            kinetic_constants
        )
    )

    try:
        virtual_patient = {
            kinetic_constant: 10**value
            for kinetic_constant, value in kinetic_constants.items()
        }
        cost = plot(biological_model, virtual_patient=virtual_patient)
        logger.info("NORMALIZATION - %s", cost.normalization)
        logger.info("TRANSITORY - %s", cost.transitory)
        logger.info("MODIFIERS - %s", cost.modifiers)
        logger.info("ORDER - %s", cost.order)
    except Exception:
        logger.exception("")
        logger.info("inf")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("")
