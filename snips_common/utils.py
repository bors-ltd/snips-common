import datetime

from hermes_python.ontology.dialogue import DurationValue


def duration_to_timedelta(duration_slot):
    """Convert a Snips duration slot to a Python timedelta object."""
    if duration_slot.years or duration_slot.quarters or duration_slot.months:
        # Can't without a reference date
        raise NotImplementedError

    return datetime.timedelta(
        days=duration_slot.days,
        seconds=duration_slot.seconds,
        minutes=duration_slot.minutes,
        hours=duration_slot.hours,
        weeks=duration_slot.weeks,
    )


def timedelta_to_duration(delta):
    """Convert a Python timedelta object to a Snips duration slot."""
    duration_slot = DurationValue()

    duration_slot.seconds = int(delta.total_seconds())
    if duration_slot.seconds >= 60:
        duration_slot.minutes = duration_slot.seconds // 60
        duration_slot.seconds %= 60
    if duration_slot.minutes >= 60:
        duration_slot.hours = duration_slot.minutes // 60
        duration_slot.minutes %= 60
    if duration_slot.hours >= 24:
        duration_slot.days = duration_slot.hours // 24
        duration_slot.hours %= 24
    if duration_slot.days >= 7:
        duration_slot.weeks = duration_slot.days // 7
        duration_slot.days %= 7
    # I won't go further, there is a reason why timedelta doesn't
    # It would only make sense relative to a datetime

    return duration_slot
