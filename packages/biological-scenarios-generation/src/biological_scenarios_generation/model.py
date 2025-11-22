import json
import random
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any, TypeAlias

import libsbml

from biological_scenarios_generation.core import PartialOrder
from biological_scenarios_generation.reactome import PhysicalEntity

SId: TypeAlias = str

VirtualPatient: TypeAlias = dict[SId, float]


class ParameterTypology(StrEnum):
    K_REACTION = auto()
    K_CONSUME_SPECIES = auto()
    K_PRODUCE_SPECIES = auto()
    K_SPECIES_CONCENTRATION = auto()
    SPECIES_MEAN = auto()
    TIME = auto()


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class BiologicalModel:
    sbml_document: libsbml.SBMLDocument
    species_order: PartialOrder[PhysicalEntity]
    kinetic_constants: dict[SId, ParameterTypology]
    kinetic_constants_order: PartialOrder[SId]

    @staticmethod
    def load(document: libsbml.SBMLDocument) -> "BiologicalModel":
        # tuple[ReactomeDbId, ReactomeDbId]
        orders: dict[str, list[Any]] = json.loads(
            document.getModel()
            .getAnnotationString()
            .replace("<annotation>", "")
            .replace("</annotation>", "")
            .replace("&quot;", '"')
        )

        # for parameter in document.getModel().getListOfParameters():
        #     print(parameter)
        #     print(
        #         parameter.getAnnotationString()
        #         .replace("<annotation>", "")
        #         .replace("</annotation>", "")
        #     )

        return BiologicalModel(
            sbml_document=document,
            kinetic_constants={
                parameter.getId(): ParameterTypology(
                    parameter.getAnnotationString()
                    .replace("<annotation>", "")
                    .replace("</annotation>", "")
                )
                for parameter in document.getModel().getListOfParameters()
                if parameter.getId().startswith("k_")
            },
            species_order={
                (PhysicalEntity(species_1), PhysicalEntity(species_2))
                for species_1, species_2 in orders["species_order"]
            },
            kinetic_constants_order={
                (kinetic_constant_1, kinetic_constant_2)
                for kinetic_constant_1, kinetic_constant_2 in orders[
                    "kinetic_constants_order"
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

        # libsbml.XMLNode.convertXMLNodeToString(
        #     document.getModel()
        #     .getAnnotation()
        #     .getChild(0)
        #     .getChild(0)
        #     .getChild(0)
        # ).replace("&quot;", '"')

        # p: libsbml.Parameter = document.getModel().createParameter()
        # node = document.create
        # p.setNotes("ciao")
        # p.setAnnotation("hola soy dora")
        # print(p.getNotes())
        # print(
        #     p.getAnnotationString()
        #     .replace("<annotation>", "")
        #     .replace("</annotation>", "")
        # )
        # exit()
