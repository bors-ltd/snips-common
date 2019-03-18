#!/usr/bin/env python3
from pkg_resources import get_distribution

from .actions import ActionWrapper
from .french import french_duration, french_number, french_timedelta
from .utils import duration_to_timedelta


__version__ = get_distribution('snips-common').version

# TODO keep this or import subpackages?
__all__ = [
    'ActionWrapper',
    'duration_to_timedelta',
    'french_duration',
    'french_number',
    'french_timedelta',
]
