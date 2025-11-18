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

from blackbox import blackbox_with_plot

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

    kinetic_constants = {
        "k_f_in_s_113592": 14.328361940667243,
        "k_f_in_s_29364": -14.645923090093596,
        "k_f_in_s_29368": -3.666184769386497,
        "k_f_in_s_29468": -6.655446481612252,
        "k_f_in_s_70106": 19.995833254870348,
        "k_f_out_s_111294": -16.24930155474223,
        "k_f_out_s_202124": 13.539860321494885,
        "k_f_out_s_29356": 17.364226080755472,
        "k_f_out_s_29366": -15.639413233721612,
        "k_f_out_s_29968": -12.707404283622337,
        "k_f_out_s_30389": -18.555619523713013,
        "k_f_r_111930": -16.07852402604366,
        "k_f_r_170676": -13.272720268302232,
        "k_f_r_202127": 6.484081187648606,
        "k_f_r_392129": -6.030365028963768,
        "k_f_r_5610727": -15.773010661934407,
        "k_h_0_r_111930": 18.5344161526313,
        "k_h_0_r_170676": -17.630580240020592,
        "k_h_0_r_202127": 14.831322322032577,
        "k_h_0_r_392129": 8.100447080029877,
        "k_h_0_r_5610727": 0.011805346441796871,
        "k_h_1_r_111930": 16.56931397107507,
        "k_h_1_r_202127": 9.60577792732532,
        "k_h_1_r_392129": 14.79084088160321,
        "k_h_1_r_5610727": -3.937092933294849,
        "k_h_2_r_111930": -5.971446534354072,
        "k_h_2_r_392129": -5.3610493665096435,
        "k_h_2_r_5610727": 6.357011965040343,
        "k_s_111865": -19.582278622559418,
        "k_s_1497830": -16.691195224669983,
        "k_s_163622": -14.164308251720128,
        "k_s_164358": -11.297913802428711,
        "k_s_170655": -17.752473738439377,
        "k_s_170665": -5.687533258306413,
        "k_s_392049": -9.884582799460818,
        "k_s_396910": -13.674404713721113,
        "k_s_5610577": -2.744347246747516,
        "k_s_5610579": -4.160368708463393,
        "k_s_5693375": -15.185455974106926,
        "k_s_74294": -11.067932444307738,
    }

    try:
        loss = blackbox_with_plot(
            biological_model,
            virtual_patient={
                kinetic_constant: 10**value
                for kinetic_constant, value in kinetic_constants.items()
            },
        )
        logger.info(loss)
    except Exception:
        logger.exception("")
        logger.info("inf")


if __name__ == "__main__":
    main()
