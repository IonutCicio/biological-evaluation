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
    # virtual_patient = {
    #     kinetic_constant: 10**value
    #     for kinetic_constant, value in kinetic_constants.items()
    # }
    _, num_objectives = openbox_config(biological_model)
    logger.info(
        objective_function(biological_model, num_objectives)(virtual_patient)
    )

    try:
        cost = plot(biological_model, virtual_patient=virtual_patient)
        logger.info(cost.normalization)
        logger.info(cost.transitory)
        logger.info(cost.modifiers)
        logger.info(cost.order)
    except Exception:
        logger.exception("")
        logger.info("inf")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("")
