import datetime


def duration_to_timedelta(duration_slot):
    """Convert a Snips duration slot to a Python timedelta object

    Should already be in the Duration API!
    """
    if duration_slot.years or duration_slot.quarters or duration_slot.months:
        # I should find a higher-level package on PyPI
        raise NotImplementedError

    return datetime.timedelta(
        days=duration_slot.days,
        seconds=duration_slot.seconds,
        minutes=duration_slot.minutes,
        hours=duration_slot.hours,
        weeks=duration_slot.weeks,
    )


