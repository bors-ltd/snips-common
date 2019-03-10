#!/usr/bin/env python3
import datetime
from pkg_resources import get_distribution
import traceback

import babel.numbers
from hermes_python.ontology.dialogue import DurationValue

from . import configs


__version__ = get_distribution('snips-common').version


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


class ActionWrapper:
    config_parser = configs.SnipsConfigParser
    reactions = {}

    def __init__(self, hermes, intent_message, config):
        self.hermes = hermes
        self.intent_message = intent_message
        self.config = config

    @classmethod
    def callback(cls, hermes, intent_message):
        print(
            "Starting action",
            cls.__name__,
            "for intent",
            intent_message.intent.intent_name,
        )
        config = cls.config_parser.read_configuration_file()
        action_wrapper = cls(hermes, intent_message, config)
        try:
            action_wrapper.action()
        except Exception as exc:
            traceback.print_exc()
            action_wrapper.react_to_exception(exc)
        else:
            print("Action finished without error")

    def message_for_this_site(self):
        match = self.intent_message.site_id == self.config['secret']['site_id']
        if not match:
            print("This message is not for us, ignoring.")
        return match

    def action(self):
        raise NotImplementedError

    def react_to_exception(self, exc):
        reaction = self.reactions.get(
            exc.__class__, "Désolée, il y a eu une erreur."
        )
        reaction = reaction.format(exc)
        self.end_session(reaction)

    def end_session(self, message, *args):
        current_session_id = self.intent_message.session_id
        message = message + " " + " ".join(args)
        print('Ending session with message "%s"' % message)
        self.hermes.publish_end_session(current_session_id, message)
