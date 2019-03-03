#!/usr/bin/env python3
import datetime
from pkg_resources import get_distribution
import traceback


__version__ = get_distribution('snips-common').version


def french_number(number, digits=2):
    """Fix the pronunciation of numbers in French."""
    number = float(number)
    if int(number) == number:
        number = int(number)
    else:
        # TODO keep meaningful zeros, e.g. 0.000001
        number = round(number, digits)
    return str(number).replace(".", ",")


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


class ActionWrapper:
    reactions = {}

    def __init__(self, hermes, intent_message):
        self.hermes = hermes
        self.intent_message = intent_message

    @classmethod
    def callback(cls, hermes, intent_message):
        print(
            "Starting action",
            cls.__name__,
            "for intent",
            intent_message.intent.intent_name,
        )
        action_wrapper = cls(hermes, intent_message)
        try:
            action_wrapper.action()
        except Exception as exc:
            traceback.print_exc()
            action_wrapper.react_to_exception(exc)
        else:
            print("Action finished without error")

    def action(self):
        raise NotImplementedError

    def react_to_exception(self, exc):
        reaction = self.reactions.get(exc.__class__, "Désolée, il y a eu une erreur.")
        reaction = reaction.format(exc)
        self.end_session(reaction)

    def end_session(self, message, *args):
        current_session_id = self.intent_message.session_id
        message = message + " " + " ".join(args)
        print('Ending session with message "%s"' % message)
        self.hermes.publish_end_session(current_session_id, message)
