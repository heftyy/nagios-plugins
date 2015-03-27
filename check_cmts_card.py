#!/usr/bin/python
import json

from pysnmp.proto.rfc1902 import ObjectName

from nagios.checkPlugin import CheckPlugin
from nagios.nagiosReturnValues import NagiosReturnValues


CMTS_CARD_NAME = '1.3.6.1.4.1.4998.1.1.10.1.4.2.1.3'
CMTS_CARD_TEMP = '1.3.6.1.4.1.4998.1.1.10.1.4.2.1.29'
CMTS_CARD_IDLE = '1.3.6.1.4.1.4998.1.1.5.3.1.1.1.8'


class CmtsCard():
    def __init__(self, index, name, temp, cpu):
        self.index = index
        self.name = name
        self.temp = temp if temp != 999 else 0
        self.cpu = cpu

    def get_json_temperature(self, **kwargs):
        json_temp = {
            "index": int(self.index),
            "name": self.name,
            "temp": int(self.temp),
            "type": "temperature-card-%d" % int(self.index),
            "output": "%s card-%s temperatura: %s" % (self.name, self.index, self.temp)
        }
        for key, value in kwargs.iteritems():
            json_temp[key] = value
        return json_temp

    def get_json_cpu(self, **kwargs):
        json_cpu = {
            "index": int(self.index),
            "name": self.name,
            "cpu": int(self.cpu),
            "type": "cpu-card-%d" % int(self.index),
            "output": "%s card-%s cpu: %s" % (self.name, self.index, self.cpu)
        }
        for key, value in kwargs.iteritems():
            json_cpu[key] = value
        return json_cpu

    @staticmethod
    def get_by_name(card_list, name):
        for card in card_list:
            if card.name == name:
                return card


class CheckCmtsCard(CheckPlugin):

    def get_cmts_card_data(self):
        request_card_name_oid = ObjectName(CMTS_CARD_NAME)

        card_list = []

        card_names_results = self.snmp_requester.do_walk(request_card_name_oid)
        if card_names_results and len(card_names_results) > 0:
            for oid, value in card_names_results.items():
                if value is None or len(value) == 0:
                    continue
                else:
                    last = oid[len(oid) - 1]

                    request_temp_oid = ObjectName("%s.1.%d" % (CMTS_CARD_TEMP, last))

                    temp_result = self.snmp_requester.do_get(request_temp_oid)
                    if temp_result and len(temp_result) == 1:
                        temp_result = temp_result[request_temp_oid]
                    else:
                        temp_result = None

                    request_idle_oid = ObjectName("%s.%d" % (CMTS_CARD_IDLE, last))

                    idle_result = self.snmp_requester.do_get(request_idle_oid)
                    if idle_result and len(idle_result) == 1:
                        idle_result = idle_result[request_idle_oid]
                    else:
                        idle_result = None

                    card = CmtsCard(
                        last,
                        value.prettyPrint(),
                        temp_result,
                        None if idle_result is None else 100 - idle_result
                    )
                    card_list.append(card)

        else:
            raise ValueError("didn't get values from the device for oid %s" % request_card_name_oid)

        if len(card_list) == 0:
            raise ValueError("values received from the device could not be used %s" % request_card_name_oid)

        return card_list

    def validate_card(self, cmts_cards_settings, cards_data):

        status_list = []
        for card in cmts_cards_settings:
            if 'name' not in card:
                return NagiosReturnValues.state_unknown

            card_data = CmtsCard.get_by_name(cards_data, card['name'])

            if 'temperature' in card:
                status = self.validate_value_lt(card_data.temp, card['temperature'])
                print "!%s" % json.dumps(card_data.get_json_temperature(nagios_status=status))
                status_list.append(status)

            if 'cpu' in card:
                status = self.validate_value_lt(card_data.cpu, card['cpu'])
                print "!%s" % json.dumps(card_data.get_json_cpu(nagios_status=status))
                status_list.append(status)

        return self.get_device_status(status_list)

    def check(self, settings):
        cmts_cards_settings = settings.get_cmts_cards()

        if not cmts_cards_settings:
            return NagiosReturnValues.state_ok

        try:
            cards_data = self.get_cmts_card_data()
        except ValueError as e:
            print "ValueError %s" % e
            return NagiosReturnValues.state_unknown

        validate = self.validate_card(cmts_cards_settings, cards_data)
        if validate != NagiosReturnValues.state_ok:
            return validate

        return NagiosReturnValues.state_ok


if __name__ == '__main__':
    CheckCmtsCard().start()
