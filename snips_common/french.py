import datetime

import babel.numbers
from hermes_python.ontology.dialogue import DurationValue

from .utils import timedelta_to_duration

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
    # XXX precision field?
    sentence = []
    for name, singular, plural in [
        ('years', "un an", "{} ans"),
        ('quarters', "un trimestre", "{} trimestres"),
        ('months', "un mois", "{} mois"),
        ('weeks', "une semaine", "{} semaines"),
        ('days', "un jour", "{} jours"),
        ('hours', "une heure", "{} heures"),
        ('minutes', "une minute", "{} minutes"),
        ('seconds', "une seconde", "{} secondes"),
    ]:
        try:
            value = getattr(duration_slot, name)
        except AttributeError:
            pass
        else:
            sentence.append(singular if value == 1 else plural.format(value))

    return " ".join(sentence)


def french_timedelta(delta):
    """Express a Python timedelta as a sentence."""
    return french_duration(timedelta_to_duration(delta))
