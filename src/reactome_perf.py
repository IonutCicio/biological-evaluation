import os

import neo4j
from biological_scenarios_generation.core import IntGTZ
from biological_scenarios_generation.model import PhysicalEntity, ReactomeDbId
from biological_scenarios_generation.reactome import Pathway
from biological_scenarios_generation.scenario import (
    BiologicalScenarioDefinition,
)

from core.lib import init

_, _ = init()


def main() -> None:
    # signal_transduction = Pathway(id=ReactomeDbId(162582))
    transport_of_small_molecules = Pathway(id=ReactomeDbId(382551))
    # co_2_cytosol = PhysicalEntity(id=ReactomeDbId(113528))
    ca_2_plus = PhysicalEntity(id=ReactomeDbId(74016))

    adenosine_triphsphate = PhysicalEntity(id=ReactomeDbId(113592))
    adenosine_diphsphate = PhysicalEntity(id=ReactomeDbId(29370))

    try:
        for _ in range(5):
            for max_depth in range(1, 6):
                with neo4j.GraphDatabase.driver(
                    uri=os.getenv("REACTOME_URL", default=""),
                    auth=(
                        os.getenv("REACTOME_USERNAME", default=""),
                        os.getenv("REACTOME_PASSWORD", default=""),
                    ),
                    database=os.getenv("REACTOME_DATABASE"),
                ) as driver:
                    biological_scenario_definition: BiologicalScenarioDefinition = BiologicalScenarioDefinition(
                        physical_entities={ca_2_plus},
                        # pathways={transport_of_small_molecules},
                        pathways=set(),
                        excluded_physical_entities={
                            adenosine_triphsphate,
                            adenosine_diphsphate,
                        },
                        constraints=set(),
                        max_depth=IntGTZ(max_depth),
                    )
                    _ = biological_scenario_definition.generate_biological_model(
                        driver
                    )
                    driver.close()
    except Exception:
        pass

        # pathways=set(),


if __name__ == "__main__":
    main()
