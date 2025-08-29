from datetime import date, timedelta


def schedule(state, grade):
    """Update SM-2 schedule state.

    Args:
        state (dict): Existing state with keys reps, interval_days, easiness, due_at.
        grade (int): 0-5 performance rating.

    Returns:
        dict: Updated state with same keys.
    """
    reps = state.get("reps", 0)
    interval = state.get("interval_days", 0)
    easiness = state.get("easiness", 2.5)

    if grade >= 3:
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 6
        else:
            interval = round(interval * easiness)
        reps += 1
    else:
        reps = 0
        interval = 1

    easiness = easiness + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    easiness = max(1.3, easiness)

    due_at = date.today() + timedelta(days=interval)

    return {
        "reps": reps,
        "interval_days": interval,
        "easiness": easiness,
        "due_at": due_at.isoformat(),
    }
