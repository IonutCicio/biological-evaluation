import json
import random
from dataclasses import dataclass
from typing import Any, TypeAlias

import libsbml

from biological_scenarios_generation.core import PartialOrder
from biological_scenarios_generation.reactome import (
    PhysicalEntity,
    ReactomeDbId,
)

SId: TypeAlias = str

VirtualPatient: TypeAlias = dict[SId, float]


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class BiologicalModel:
    sbml_document: libsbml.SBMLDocument
    kinetic_constants: set[SId]
    kinetic_constants_constraints: PartialOrder[SId]
    physical_entities_constraints: PartialOrder[PhysicalEntity]

    @staticmethod
    def load(document: libsbml.SBMLDocument) -> "BiologicalModel":
        # tuple[ReactomeDbId, ReactomeDbId]
        constraints: dict[str, list[Any]] = json.loads(
            libsbml.XMLNode.convertXMLNodeToString(
                document.getModel()
                .getAnnotation()
                .getChild(0)
                .getChild(0)
                .getChild(0)
            ).replace("&quot;", '"')
        )

        return BiologicalModel(
            sbml_document=document,
            kinetic_constants={
                parameter.getId()
                for parameter in document.getModel().getListOfParameters()
                if parameter.getId().startswith("k_")
            },
            physical_entities_constraints={
                (PhysicalEntity(left), PhysicalEntity(right))
                for (left, right) in constraints[
                    "physical_entities_constraints"
                ]
            },
            kinetic_constants_constraints={
                (left, right)
                for (left, right) in constraints[
                    "kinetic_constants_constraints"
                ]
            },
        )

    def __call__(self) -> VirtualPatient:
        return {
            kinetic_constant: 10
            ** random.uniform(
                -20, 0.0 if kinetic_constant.startswith("k_s_") else 20.0
            )
            for kinetic_constant in self.kinetic_constants
        }
