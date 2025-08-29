"""Spaced repetition scheduling using SM-2 rules."""
from dataclasses import dataclass
from typing import Dict


@dataclass
class SRState:
    repetitions: int = 0
    interval_days: int = 0
    easiness: float = 2.5


def schedule(state: Dict, grade: int) -> Dict:
    """Return next state given current `state` and response `grade` (0-5).

    Ensures interval_days >= 1 and easiness >= 1.3.
    """
    reps = state.get('repetitions', 0)
    interval = state.get('interval_days', 0)
    ease = state.get('easiness', 2.5)

    if grade >= 3:
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 6
        else:
            interval = int(round(interval * ease))
        reps += 1
    else:
        reps = 0
        interval = 1

    ease = ease + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    if ease < 1.3:
        ease = 1.3
    if interval < 1:
        interval = 1

    return {'repetitions': reps, 'interval_days': interval, 'easiness': ease}
