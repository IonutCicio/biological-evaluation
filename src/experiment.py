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
        "k_f_in_s_113592": -0.7198331811703405,
        "k_f_in_s_29364": -3.9859031717292837,
        "k_f_in_s_29368": -17.780539345504536,
        "k_f_in_s_29468": 2.7773528823700673,
        "k_f_in_s_70106": -1.2040737490595106,
        "k_f_out_s_111294": -13.259931781206799,
        "k_f_out_s_202124": -11.477076297010251,
        "k_f_out_s_29356": 12.936580313124615,
        "k_f_out_s_29366": 3.539591082798875,
        "k_f_out_s_29968": 10.443254836461648,
        "k_f_out_s_30389": -13.420874728652066,
        "k_f_r_111930": 15.326610343493947,
        "k_f_r_170676": 16.73922167987312,
        "k_f_r_202127": -2.2870031170308778,
        "k_f_r_392129": 1.5195710812460632,
        "k_f_r_5610727": 2.714918179865286,
        "k_h_0_r_111930": 1.5259115070208153,
        "k_h_0_r_170676": 15.523274810062503,
        "k_h_0_r_202127": -10.967658779035707,
        "k_h_0_r_392129": -8.733188635564876,
        "k_h_0_r_5610727": -4.352625044845393,
        "k_h_1_r_111930": 3.701675028353545,
        "k_h_1_r_202127": -15.509516794040202,
        "k_h_1_r_392129": -14.224250407766,
        "k_h_1_r_5610727": 19.462781323874275,
        "k_h_2_r_111930": 3.5904950969766283,
        "k_h_2_r_392129": 11.78450892094396,
        "k_h_2_r_5610727": 18.230334582469354,
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
