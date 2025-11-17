import random
from dataclasses import dataclass
from typing import TypeAlias

import libsbml

from biological_scenarios_generation.core import PartialOrder
from biological_scenarios_generation.reactome import (
    DatabaseObject,
    PhysicalEntity,
)

SId: TypeAlias = str

VirtualPatient: TypeAlias = dict[SId, float]


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class BiologicalModel:
    sbml_document: libsbml.SBMLDocument
    kinetic_constants: set[SId]
    kinetic_constants_constraints: PartialOrder[DatabaseObject]
    physical_entities_constraints: PartialOrder[PhysicalEntity]

    @staticmethod
    def load(document: libsbml.SBMLDocument) -> "BiologicalModel":
        return BiologicalModel(
            sbml_document=document,
            kinetic_constants={
                p.getId()
                for p in document.getModel().getListOfParameters()
                if "time" not in p.getId() and "mean" not in p.getId()
            },
            physical_entities_constraints=set(),
            kinetic_constants_constraints=set(),
        )

    def __call__(self) -> VirtualPatient:
        return {
            kinetic_constant: 10 ** random.uniform(-20, 20)
            for kinetic_constant in self.kinetic_constants
        }
