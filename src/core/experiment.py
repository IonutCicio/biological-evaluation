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

from blackbox import objective_function, plot
from lib import init, openbox_config

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
        "k_consumption_reaction_species_111294": -20.0,
        "k_consumption_reaction_species_202124": -20.0,
        "k_consumption_reaction_species_29356": -20.0,
        "k_consumption_reaction_species_29366": -20.0,
        "k_consumption_reaction_species_29968": -20.0,
        "k_consumption_reaction_species_30389": -20.0,
        "k_half_saturation_0_reaction_111930": -20.0,
        "k_half_saturation_0_reaction_170676": -20.0,
        "k_half_saturation_0_reaction_202127": -20.0,
        "k_half_saturation_0_reaction_392129": -20.0,
        "k_half_saturation_0_reaction_5610727": -20.0,
        "k_half_saturation_1_reaction_111930": -20.0,
        "k_half_saturation_1_reaction_202127": -20.0,
        "k_half_saturation_1_reaction_392129": -20.0,
        "k_half_saturation_1_reaction_5610727": -20.0,
        "k_half_saturation_2_reaction_111930": -20.0,
        "k_half_saturation_2_reaction_392129": -20.0,
        "k_half_saturation_2_reaction_5610727": -20.0,
        "k_production_reaction_species_113592": -20.0,
        "k_production_reaction_species_29364": -20.0,
        "k_production_reaction_species_29368": -20.0,
        "k_production_reaction_species_29468": -20.0,
        "k_production_reaction_species_70106": -20.0,
        "k_reaction_111930": -20.0,
        "k_reaction_170676": -20.0,
        "k_reaction_202127": -20.0,
        "k_reaction_392129": -20.0,
        "k_reaction_5610727": -20.0,
        "k_species_111865": -20.0,
        "k_species_1497830": -20.0,
        "k_species_163622": -20.0,
        "k_species_164358": -20.0,
        "k_species_170655": -20.0,
        "k_species_170665": -20.0,
        "k_species_392049": -20.0,
        "k_species_396910": -20.0,
        "k_species_5610577": -20.0,
        "k_species_5610579": -20.0,
        "k_species_5693375": -20.0,
        "k_species_74294": -20.0,
    }
    virtual_patient = {
        kinetic_constant: 10**value
        for kinetic_constant, value in kinetic_constants.items()
    }
    _, num_objectives, _ = openbox_config(biological_model)
    logger.info(
        objective_function(biological_model, num_objectives)(kinetic_constants)
    )

    try:
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
