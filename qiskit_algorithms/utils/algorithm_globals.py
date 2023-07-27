# This code is part of a Qiskit project.
#
# (C) Copyright IBM 2019, 2023.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Algorithm Globals"""

from typing import Optional
import logging

import numpy as np

from qiskit.tools import parallel
from qiskit.user_config import get_config
from ..exceptions import AlgorithmError


logger = logging.getLogger(__name__)


class QiskitAlgorithmGlobals:
    """Class for global properties."""

    CPU_COUNT = parallel.local_hardware_info()["cpus"]

    def __init__(self) -> None:
        self._random_seed = None  # type: Optional[int]
        self._num_processes = QiskitAlgorithmGlobals.CPU_COUNT
        self._random = None
        self._massive = False
        try:
            settings = get_config()
            self.num_processes = settings.get("num_processes", QiskitAlgorithmGlobals.CPU_COUNT)
        except Exception as ex:  # pylint: disable=broad-except
            logger.debug("User Config read error %s", str(ex))

    @property
    def random_seed(self) -> Optional[int]:
        """Return random seed."""
        return self._random_seed

    @random_seed.setter
    def random_seed(self, seed: Optional[int]) -> None:
        """Set random seed."""
        self._random_seed = seed
        self._random = None

    @property
    def num_processes(self) -> int:
        """Return num processes."""
        return self._num_processes

    @num_processes.setter
    def num_processes(self, num_processes: Optional[int]) -> None:
        """Set num processes.
        If 'None' is passed, it resets to QiskitAlgorithmGlobals.CPU_COUNT
        """
        if num_processes is None:
            num_processes = QiskitAlgorithmGlobals.CPU_COUNT
        elif num_processes < 1:
            raise AlgorithmError(f"Invalid Number of Processes {num_processes}.")
        elif num_processes > QiskitAlgorithmGlobals.CPU_COUNT:
            raise AlgorithmError(
                "Number of Processes {} cannot be greater than cpu count {}.".format(
                    num_processes, QiskitAlgorithmGlobals.CPU_COUNT
                )
            )
        self._num_processes = num_processes
        # TODO: change Terra CPU_COUNT until issue
        # gets resolved: https://github.com/Qiskit/qiskit-terra/issues/1963
        try:
            parallel.CPU_COUNT = self.num_processes
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning(
                "Failed to set qiskit.tools.parallel.CPU_COUNT to value: '%s': Error: '%s'",
                self.num_processes,
                str(ex),
            )

    @property
    def random(self) -> np.random.Generator:
        """Return a numpy np.random.Generator (default_rng)."""
        if self._random is None:
            self._random = np.random.default_rng(self._random_seed)
        return self._random

    @property
    def massive(self) -> bool:
        """Return massive to allow processing of large matrices or vectors."""
        return self._massive

    @massive.setter
    def massive(self, massive: bool) -> None:
        """Set massive to allow processing of large matrices or  vectors."""
        self._massive = massive


# Global instance to be used as the entry point for globals.
algorithm_globals = QiskitAlgorithmGlobals()
