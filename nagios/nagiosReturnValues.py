__author__ = 'szymon'

from enum import Enum


class NagiosReturnValues(Enum):
    state_ok = 0
    state_warning = 1
    state_critical = 2
    state_unknown = 3

    @staticmethod
    def value_to_string(value):
        if value == NagiosReturnValues.state_ok:
            return "OK"
        elif value == NagiosReturnValues.state_warning:
            return "WARNING"
        elif value == NagiosReturnValues.state_critical:
            return "CRITICAL"
        elif value == NagiosReturnValues.state_unknown:
            return "UNKNOWN"
