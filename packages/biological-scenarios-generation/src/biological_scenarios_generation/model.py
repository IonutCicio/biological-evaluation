import json
import random
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import TypeAlias

import libsbml

from biological_scenarios_generation.core import Interval, PartialOrder
from biological_scenarios_generation.reactome import (
    PhysicalEntity,
    ReactomeDbId,
)

SId: TypeAlias = str

VirtualPatient: TypeAlias = dict[SId, float]


class ConstantCategory(StrEnum):
    REACTION_SPEED = auto()
    PRODUCTION_SPEED = auto()
    CONSUMPTION_SPEED = auto()
    SPECIES_CONCENTRATION = auto()
    HALF_SATURATION = auto()

    def interval(self) -> Interval:
        return Interval(
            lower_bound=-20.0,
            upper_bound=0.0
            if self == ConstantCategory.SPECIES_CONCENTRATION
            else 20.0,
        )


class OtherParameterCategory(StrEnum):
    SPECIES_MEAN = auto()
    TIME = auto()


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class BiologicalModel:
    sbml_document: libsbml.SBMLDocument
    species_order: PartialOrder[PhysicalEntity]
    kinetic_constants: dict[SId, ConstantCategory]
    kinetic_constants_order: PartialOrder[SId]
    other_parameters: dict[SId, OtherParameterCategory]

    @staticmethod
    def load(sbml_document: libsbml.SBMLDocument) -> "BiologicalModel":
        def _category_from_parameter(
            parameter: libsbml.Parameter,
        ) -> ConstantCategory | OtherParameterCategory:
            category_str: str = (
                parameter.getAnnotationString()
                .replace("<annotation>", "")
                .replace("</annotation>", "")
            )

            try:
                return ConstantCategory(category_str)
            except ValueError:
                return OtherParameterCategory(category_str)

        kinetic_constants: dict[SId, ConstantCategory] = {}
        other_parameters: dict[SId, OtherParameterCategory] = {}

        for parameter in sbml_document.getModel().getListOfParameters():
            parameter_category: ConstantCategory | OtherParameterCategory = (
                _category_from_parameter(parameter)
            )
            if isinstance(parameter_category, ConstantCategory):
                kinetic_constants[parameter.getId()] = parameter_category
            else:
                other_parameters[parameter.getId()] = parameter_category

        model_annotation: dict[str, list[list[str]]] = json.loads(
            sbml_document.getModel()
            .getAnnotationString()
            .replace("<annotation>", "")
            .replace("</annotation>", "")
            .replace("&quot;", '"')
        )

        return BiologicalModel(
            sbml_document=sbml_document,
            species_order={
                (
                    PhysicalEntity(id=ReactomeDbId(int(species_1))),
                    PhysicalEntity(id=ReactomeDbId(int(species_2))),
                )
                for (species_1, species_2) in model_annotation["species_order"]
            },
            kinetic_constants=kinetic_constants,
            kinetic_constants_order={
                (kinetic_constant_1, kinetic_constant_2)
                for (
                    kinetic_constant_1,
                    kinetic_constant_2,
                ) in model_annotation["kinetic_constants_order"]
            },
            other_parameters=other_parameters,
        )

    def __call__(self) -> VirtualPatient:
        return {
            kinetic_constant: 10
            ** random.uniform(
                category.interval().lower_bound, category.interval().upper_bound
            )
            for kinetic_constant, category in self.kinetic_constants.items()
        }
