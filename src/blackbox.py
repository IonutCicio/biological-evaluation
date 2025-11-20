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
    transitory_phi: float = float(os.getenv("TRANSITORY") or 0.5)

    result: Trajectory = rr.simulate(
        start=simulation_start, end=simulation_end, points=simulation_points
    )

    cost: Cost = Cost()

    for column_number, column_name in enumerate(rr.timeCourseSelections):
        if (
            re.match(r"^\[s_\d+\]$", column_name)  # check if its a species
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

        if "mean" in column_name:
            x_1, x_2 = (
                int((simulation_points - 1) * transitory_phi),
                simulation_points - 1,
            )
            y_1, y_2 = result[x_1, column_number], result[x_2, column_number]
            slope = (y_2 - y_1) / (x_2 - x_1)
            cost.transitory.append(float(np.arctan(abs(slope))))

    for left, right in biological_model.physical_entities_constraints:
        pass

    # for k_1, k_2 in biological_model.kinetic_constants_constraints:
    #     if virtual_patient[k_1] > virtual_patient[k_2]:
    #         raise ViolatedKineticConstantsPartialOrderError
    # normalization_cost: list[float] = []
    # transitory_cost: list[float] = []

    # for k_1, k_2 in biological_model.kinetic_constants_constraints:
    #     if virtual_patient[k_1] > virtual_patient[k_2]:
    # TODO: better or worse

    # + transitory_cost
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
        # if "time" not in col_name and "mean" not in col_name:
        if trajectory[-1, col_number] > 1:
            print(col_name)

        if "mean" in col_name:
            name = col_name
            _ = pylab.plot(time, trajectory[:, col_number], label=str(name))
            _ = pylab.legend()

    pylab.show()

    return cost


# print(
#     "k1",
#     kinetic_constant_1,
#     "\nk2",
#     kinetic_constant_2,
#     "\nk1_v",
#     virtual_patient[kinetic_constant_1],
#     "\nk2_v",
#     virtual_patient[kinetic_constant_2],
# )


# document: libsbml.SBMLDocument,
# physical_entities_constraints: PartialOrder[PhysicalEntity],
# kinetic_constants_constraints: PartialOrder[ReactomeDbId],

# bioloidocument,
# virtual_patient,
# physical_entities_constraints,
# kinetic_constants_constraints,

# document,
# virtual_patient,
# physical_entities_constraints,
# kinetic_constants_constraints,


# for i in range(len(trajectory[:, col_number])):
# trajectory[i, col_number] = min(trajectory[i, col_number], 1.0)
# if "time" not in column_name and "mean" not in column_name:
# print(normalization_loss, transitory_loss)
# for column_number, column_name in enumerate(rr.timeCourseSelections):
# environment: Environment,
# environment: Environment,
# TODO: use the angle of the line as a measure of "how bad is it", maybe with abs (angular coefficient can be negative)
# simulation_end: int = int(os.getenv("SIMULATION_END") or 10)
# simulation_points: int = int(os.getenv("SIMULATION_POINTS") or 10000)
# normalization_loss += 1

# if concentration > 1:
#     normalization_loss += concentration - 1
# elif concentration < 0:
#     normalization_loss += abs(concentration)
# print(normalization_loss, transitory_loss)
# print(
#     column_name, "slope:", slope, " - angle:", np.arctan(abs(slope))
# )
# slope: float = (simulation_points / 2) / (
#     result[simulation_points - 1, column_number]
#     - result[int(simulation_points / 2), column_number]
# )
# transitory_loss += min(
#     abs(
#         result[-1, column_number]
#         - result[int(simulation_points * (1 / 2)), column_number]
#     ),
#     1,
# )
# TODO: pass tuple too
