"""Trajectory dataset tooling: reading, validation, manifest, replay verification, fuzzing, seed ranges.

Format and invariants: docs/DATA_CONTRACT.md. Command line: `balatro-data --help`.
"""

from balatro_env.data.legality import check_action
from balatro_env.data.trajectory import Trajectory, read_trajectory
from balatro_env.data.validate import ValidationReport, validate_trajectory

__all__ = ["Trajectory", "ValidationReport", "check_action", "read_trajectory", "validate_trajectory"]
