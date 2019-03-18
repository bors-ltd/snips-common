import datetime

import babel.numbers
from hermes_python.ontology.dialogue import DurationValue


def french_number(number, digits=2):
    """Optimize the pronunciation of numbers for picoTTS."""
    number = float(number)
    if int(number) == number:
        # Remove useless zeroes
        number = int(number)
    else:
        # Increase precision to keep meaningful zeros, e.g. 0.000001
        while round(number, digits) == int(number):
            digits += 1
            if digits > 15:
                # 1.0000000000000001 become 1.0 anyway
                break
        number = round(number, digits)

    return babel.numbers.format_decimal(number, locale='fr_FR', decimal_quantization=False)


def french_duration(duration_slot):
    """Express the duration heard by Snips as a sentence."""
    # TODO precision field?
    sentence = []
    for unit, word in [
        ('years', "ans"),
        ('quarters', "trimestres"),
        ('months', "mois"),
        ('weeks', "semaines"),
        ('days', "jours"),
        ('hours', "heures"),
        ('minutes', "minutes"),
        ('seconds', "secondes"),
    ]:
        value = getattr(duration_slot, unit, None)
        if value:
            if value == 1 and word in ('semaines', 'heures', 'minutes', 'secondes'):
                value = "une"
            else:
                value = str(value)
            sentence.append(value)
            sentence.append(word)

    if not sentence:
        return ""
    return " ".join(sentence)


def french_timedelta(delta):
    """Express a Python timedelta as a sentence."""
    seconds = int(delta.total_seconds())
    duration_slot = DurationValue(0, 0, 0, 0, 0, 0, 0, 0, precision=1)

    if seconds < 60:
        # Only say the seconds under a minute
        duration_slot.seconds = seconds
    else:
        duration_slot.minutes = seconds // 60
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

    return french_duration(duration_slot)
