import os
import re
from dataclasses import dataclass, field
from typing import TypeAlias

import libsbml
import numpy as np
import pylab
import roadrunner
from biological_scenarios_generation.model import (
    BiologicalModel,
    VirtualPatient,
)

from lib import source_env

_ = source_env()

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
    rr: roadrunner.RoadRunner = roadrunner.RoadRunner(
        libsbml.writeSBMLToString(biological_model.sbml_document)
    )

    for k, value in virtual_patient.items():
        rr[k] = value

    simulation_start: int = int(os.getenv("SIMULATION_START") or 0)
    simulation_end: int = int(os.getenv("SIMULATION_END") or 10000)
    simulation_points: int = int(os.getenv("SIMULATION_POINTS") or 100000)
    transitory: float = float(os.getenv("TRANSITORY") or 0.5)

    result: Trajectory = rr.simulate(
        start=simulation_start, end=simulation_end, points=simulation_points
    )

    cost: Cost = Cost()

    is_species_re: re.Pattern[str] = re.compile(r"^\[s_\d+\]$")

    for column_number, column_name in enumerate(rr.timeCourseSelections):
        if (
            is_species_re.match(column_name)
            and "k_" + column_name[1:-1] not in virtual_patient
        ):
            points_violating_normalization_constraint: int = 0
            for species_concentration in result[:, column_number]:
                if species_concentration < 0 or species_concentration > 1:
                    points_violating_normalization_constraint += 1

            cost.normalization.append(
                float(points_violating_normalization_constraint)
                / float(simulation_points)
            )

        if "mean_s_" in column_name:
            x_1: int = int((simulation_points - 1) * transitory)
            x_2: int = simulation_points - 1
            y_1: float = result[x_1, column_number]
            y_2: float = result[x_2, column_number]

            cost.transitory.append(
                float(np.arctan(abs((y_2 - y_1) / float(x_2 - x_1))))
            )

    for s_1, s_2 in biological_model.physical_entities_constraints:
        pass

    for k_1, k_2 in biological_model.kinetic_constants_constraints:
        cost.modifiers.append(
            float(
                np.log(max(virtual_patient[k_1] - virtual_patient[k_2], 0) + 1)
            )
        )

    return (result, rr, cost)


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
