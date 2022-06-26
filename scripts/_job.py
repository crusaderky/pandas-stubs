import time
from dataclasses import dataclass
from subprocess import CalledProcessError
from typing import Callable, List, Optional, Deque

from loguru import logger
from collections import deque

@dataclass
class Step:
    name: str
    run: Callable[[], None]
    rollback: Optional[Callable[[], None]] = None


def __rollback_job(steps: Deque[Step]):
    """
    Responsible to run rollback of steps.
    """

    while steps:
        step = steps.pop()
        if step.rollback is not None:
            logger.warning(f"Undoing: {step.name}")
            try:
                step.rollback()
            except Exception:
                logger.error(f"Rollback of Step: '{step.name}' failed!")



def run_job(steps: List[Step]) -> None:
    """
    Responsible to run steps with logs.
    """

    rollback_steps = Deque[Step]()

    for step in steps:
        start = time.perf_counter()
        logger.info(f"Beginning: '{step.name}'")

        try:
                            
            rollback_steps.append(step)
            step.run()

        except CalledProcessError:

            logger.error(f"Step: '{step.name}' failed!")
            __rollback_job(rollback_steps)
            
            break

        end = time.perf_counter()
        logger.success(f"End: '{step.name}', runtime: {end - start:.3f} seconds.")
