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
from lib import config, init

_, logger = init()


def main() -> None:
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

    filename = Path(f"{Path(__file__).stem}.sbml")

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

        with filename.open("w") as file:
            _ = file.write(
                libsbml.writeSBMLToString(biological_model.sbml_document)
            )
    except ServiceUnavailable:
        assert filename.exists()
        assert filename.is_file()

        sbml_document: libsbml.SBMLDocument = libsbml.readSBML(filename)
        biological_model: BiologicalModel = BiologicalModel.load(sbml_document)
        print("here")

    exit()

    virtual_patient = biological_model()
    kinetic_constants = {
        "k_f_in_s_113592": 5.067613205815622,
        "k_f_in_s_29364": 15.07548713215445,
        "k_f_in_s_29368": -15.349314216519634,
        "k_f_in_s_29468": 7.179804149895837,
        "k_f_in_s_70106": -5.287341738797174,
        "k_f_r_111930": 5.901850543610951,
        "k_f_r_170676": -6.643366225540422,
        "k_f_r_202127": -18.820104069450675,
        "k_f_r_392129": 9.709978414522162,
        "k_f_r_5610727": 0.7160424650977113,
        "k_h_0_r_111930": 5.114840620424729,
        "k_h_0_r_170676": 0.9091276659299581,
        "k_h_0_r_202127": -0.9130105320028079,
        "k_h_0_r_392129": 12.514388585672314,
        "k_h_0_r_5610727": 16.182477125699386,
        "k_h_1_r_111930": -5.95168342778198,
        "k_h_1_r_202127": -12.973610043584465,
        "k_h_1_r_392129": -14.937265512466919,
        "k_h_1_r_5610727": -18.60804121665734,
        "k_h_2_r_111930": 11.238842540095678,
        "k_h_2_r_392129": 11.274639834934966,
        "k_h_2_r_5610727": -7.700911386375715,
        "k_r_out_s_111294": -8.465541546649881,
        "k_r_out_s_202124": 5.0770311009283375,
        "k_r_out_s_29356": -0.4432980011661023,
        "k_r_out_s_29366": -8.261828595932826,
        "k_r_out_s_29968": 2.3002221758149233,
        "k_r_out_s_30389": -3.6061965685921464,
        "k_s_111865": -6.817310908738017,
        "k_s_1497830": -13.664543770597085,
        "k_s_163622": -11.709076819361417,
        "k_s_164358": -3.672138782285124,
        "k_s_170655": -13.30873061872558,
        "k_s_170665": -9.951817648874645,
        "k_s_392049": -12.8567264893327,
        "k_s_396910": -11.478895872329018,
        "k_s_5610577": -5.599323703327254,
        "k_s_5610579": -14.02491535146071,
        "k_s_5693375": -19.86435764570679,
        "k_s_74294": -5.250313066194256,
    }
    virtual_patient = {
        kinetic_constant: 10**value
        for kinetic_constant, value in kinetic_constants.items()
    }
    _, num_objectives = config(biological_model)
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
