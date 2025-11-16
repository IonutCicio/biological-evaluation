import os
import re
from typing import TypeAlias

import libsbml
import numpy as np
import pylab
import roadrunner
from biological_scenarios_generation.core import PartialOrder
from biological_scenarios_generation.model import (
    Environment,
    PhysicalEntity,
    VirtualPatient,
)

Trajectory: TypeAlias = np.ndarray[tuple[int, ...], np.dtype[np.float64]]


def _blackbox(
    document: libsbml.SBMLDocument,
    virtual_patient: VirtualPatient,
    species_partial_order: PartialOrder[PhysicalEntity],
) -> tuple[Trajectory, roadrunner.RoadRunner, float]:
    rr: roadrunner.RoadRunner = roadrunner.RoadRunner(
        libsbml.writeSBMLToString(document)
    )

    for k, value in virtual_patient.items():
        rr[k] = value

    simulation_start: int = int(os.getenv("SIMULATION_START") or 0)
    simulation_end: int = int(os.getenv("SIMULATION_END") or 2)
    simulation_points: int = int(os.getenv("SIMULATION_POINTS") or 100000)

    result: Trajectory = rr.simulate(
        start=simulation_start, end=simulation_end, points=simulation_points
    )

    normalization_loss: float = 0.0
    transitory_loss: float = 0.0
    for column_number, column_name in enumerate(rr.timeCourseSelections):
        if re.match(r"^\[s_\d+\]$", column_name):
            points_violating_normalization_constraint: int = 0
            for concentration in result[:, column_number]:
                if concentration < 0 or concentration > 1:
                    points_violating_normalization_constraint += 1

            normalization_loss += float(
                points_violating_normalization_constraint
            ) / float(simulation_points)

            y_1, y_2 = int((simulation_points - 1) / 2), simulation_points - 1
            x_1, x_2 = result[y_1, column_number], result[y_2, column_number]
            slope = (y_2 - y_1) / (x_2 - x_1) if x_1 != x_2 else 0
            transitory_loss += abs(float(np.arctan(slope)))

    return (result, rr, normalization_loss + transitory_loss)

    # if "time" not in column_name and "mean" not in column_name:
    # print(normalization_loss, transitory_loss)
    # for column_number, column_name in enumerate(rr.timeCourseSelections):


def blackbox(
    document: libsbml.SBMLDocument,
    virtual_patient: VirtualPatient,
    environment: Environment,
    species_partial_order: PartialOrder[PhysicalEntity],
) -> float:
    (_, _, loss) = _blackbox(document, virtual_patient, species_partial_order)
    return loss


def plot_blackbox(
    document: libsbml.SBMLDocument,
    virtual_patient: VirtualPatient,
    environment: Environment,
    species_partial_order: PartialOrder[PhysicalEntity],
) -> float:
    (trajectory, rr, loss) = _blackbox(
        document, virtual_patient, species_partial_order
    )

    time = trajectory[:, 0]
    for col_number, col_name in enumerate(rr.timeCourseSelections):
        if "time" not in col_name and "mean" not in col_name:
            name = col_name
            # for i in range(len(trajectory[:, col_number])):
            # trajectory[i, col_number] = min(trajectory[i, col_number], 1.0)
            _ = pylab.plot(time, trajectory[:, col_number], label=str(name))
            _ = pylab.legend()

    pylab.show()

    return loss

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
