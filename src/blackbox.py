import math
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TypeAlias

import libsbml
import numpy as np
import pylab
import roadrunner
from biological_scenarios_generation.core import IntGTZ
from biological_scenarios_generation.model import (
    BiologicalModel,
    VirtualPatient,
)

from lib import init

_ = init()


Trajectory: TypeAlias = np.ndarray[tuple[int, ...], np.dtype[np.float64]]


class ViolatedKineticConstantsPartialOrderError(Exception): ...


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class Cost:
    normalization: list[float] = field(default_factory=list)
    transitory: list[float] = field(default_factory=list)
    order: list[float] = field(default_factory=list)
    modifiers: list[float] = field(default_factory=list)


def _blackbox(
    biological_model: BiologicalModel, virtual_patient: VirtualPatient
) -> tuple[Trajectory, roadrunner.RoadRunner, Cost]:
    simulation_start: int = int(os.getenv("SIMULATION_START", default="0"))
    simulation_end: int = int(os.getenv("SIMULATION_END", default="10000"))
    simulation_points: int = int(
        os.getenv("SIMULATION_POINTS", default="100000")
    )
    transitory: float = float(os.getenv("TRANSITORY", default="0.75"))

    rr: roadrunner.RoadRunner = roadrunner.RoadRunner(
        libsbml.writeSBMLToString(biological_model.sbml_document)
    )

    for k, value in virtual_patient.items():
        rr[k] = value

    result: Trajectory = rr.simulate(
        start=simulation_start, end=simulation_end, points=simulation_points
    )

    cost: Cost = Cost()

    for column_number, column_name in enumerate(rr.timeCourseSelections):
        _column_name = column_name.removeprefix("[").removesuffix("]")
        if f"mean_{_column_name}" in biological_model.other_parameters:
            points_violating_normalization_constraint: int = 0
            for species_concentration in result[:, column_number]:
                if species_concentration < 0 or species_concentration > 1:
                    points_violating_normalization_constraint += 1

            cost.normalization.append(
                float(points_violating_normalization_constraint)
                / float(simulation_points)
            )

        if "mean_" in column_name:
            x_1: int = int((simulation_points - 1) * transitory)
            x_2: int = simulation_points - 1
            y_1: float = result[x_1, column_number]
            y_2: float = result[x_2, column_number]

            cost.transitory.append(
                float(np.arctan(abs((y_2 - y_1) / float(x_2 - x_1))))
            )

    for species_1, species_2 in biological_model.species_order:
        diff: float = (
            result[-1, rr.timeCourseSelections.index(f"[{species_1}]")]
            - result[-1, rr.timeCourseSelections.index(f"[{species_2}]")]
        )
        cost.order.append(float(math.log(max(diff, 0) + 1)))

    for (
        kinetic_constant_1,
        kinetic_constant_2,
    ) in biological_model.kinetic_constants_order:
        diff: float = (
            virtual_patient[kinetic_constant_1]
            - virtual_patient[kinetic_constant_2]
        )
        cost.modifiers.append(float(math.log(max(diff, 0) + 1)))

    return (result, rr, cost)


SIMULATION_FAIL_COST: float = sys.float_info.max


def objective_function(
    biological_model: BiologicalModel, num_objectives: IntGTZ
) -> Callable[[VirtualPatient], dict[str, list[float]]]:
    def _objective_function(
        virtual_patient: VirtualPatient,
    ) -> dict[str, list[float]]:
        objectives: list[float]
        try:
            cost = blackbox(biological_model, virtual_patient)
            objectives = cost.normalization + cost.transitory
        except:
            objectives = [SIMULATION_FAIL_COST] * num_objectives

        return {"objectives": objectives}

    return _objective_function


def blackbox(
    biological_model: BiologicalModel, virtual_patient: VirtualPatient
) -> Cost:
    (_, _, cost) = _blackbox(
        biological_model=biological_model, virtual_patient=virtual_patient
    )
    return cost


def plot(
    biological_model: BiologicalModel, virtual_patient: VirtualPatient
) -> Cost:
    (trajectory, rr, cost) = _blackbox(
        biological_model=biological_model, virtual_patient=virtual_patient
    )

    time = trajectory[:, 0]
    for col_number, col_name in enumerate(rr.timeCourseSelections):
        if "mean" in col_name:
            name = col_name
            _ = pylab.plot(time, trajectory[:, col_number], label=str(name))
            _ = pylab.legend()

    pylab.show()

    return cost
