import logging
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

from blackbox import plot
from lib import source_env

_ = source_env()


def main() -> None:
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        filename=f"{Path(__file__).stem}.log", level=logging.INFO
    )
    # logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    signal_transduction = Pathway(ReactomeDbId(162582))
    nitric_oxide = PhysicalEntity(ReactomeDbId(202124))
    cyclic_amp = PhysicalEntity(ReactomeDbId(30389))
    adenosine_triphsphate = PhysicalEntity(ReactomeDbId(113592))
    adenosine_diphsphate = PhysicalEntity(ReactomeDbId(29370))

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

    model_filename: str = f"{Path(__file__).stem}.sbml"
    model_path = Path(model_filename)

    try:
        with neo4j.GraphDatabase.driver(
            uri=os.getenv("REACTOME_URL") or "",
            auth=(
                os.getenv("REACTOME_USERNAME") or "",
                os.getenv("REACTOME_PASSWORD") or "",
            ),
            database=os.getenv("REACTOME_DATABASE"),
        ) as driver:
            driver.verify_connectivity()
            biological_model = (
                biological_scenario_definition.generate_biological_model(driver)
            )

        with model_path.open("w") as file:
            _ = file.write(
                libsbml.writeSBMLToString(biological_model.sbml_document)
            )
    except ServiceUnavailable:
        assert model_path.exists()
        assert model_path.is_file()

        document: libsbml.SBMLDocument = libsbml.readSBML(model_filename)
        biological_model: BiologicalModel = BiologicalModel.load(document)

    virtual_patient = dict.fromkeys(biological_model.kinetic_constants, 1.0)

    try:
        cost = plot(biological_model, virtual_patient=virtual_patient)
        logger.info(cost)
    except Exception:
        logger.exception("")
        logger.info("inf")


if __name__ == "__main__":
    main()
