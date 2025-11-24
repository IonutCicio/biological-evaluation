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

from core.blackbox import objective_function, plot
from core.lib import init, openbox_config

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
    _, num_objectives, _ = openbox_config(biological_model)
    logger.info(
        objective_function(biological_model, num_objectives)(kinetic_constants)
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
