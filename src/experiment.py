import logging
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

NEO4J_URL_REACTOME = "neo4j://localhost:7687"
AUTH = ("noe4j", "neo4j")
REACTOME_DATABASE = "graph.db"

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(
        filename=f"{Path(__file__).stem}.log", level=logging.INFO
    )

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
            uri=NEO4J_URL_REACTOME, auth=AUTH, database=REACTOME_DATABASE
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

    # virtual_patient={
    #     kinetic_constant: 10**value
    #     for kinetic_constant, value in kinetic_constants.items()
    # },

    try:
        cost = plot(biological_model, virtual_patient=biological_model())
        logger.info(cost)
        print(cost.normalization, cost.transitory, sep="\n")
    except Exception:
        logger.exception("")
        logger.info("inf")


if __name__ == "__main__":
    main()
