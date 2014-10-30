__author__ = 'szymon'

from enum import Enum


class NagiosReturnValues(Enum):
    state_ok = 0
    state_warning = 1
    state_critical = 2
    state_unknown = 3
