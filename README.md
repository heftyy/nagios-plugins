nagios-plugins
==========

nagios-plugins.js is a javascript file that contains sample code for generating nagios settings that the plugins use


check_type config option, available only for server

---

* lt - current value on the device has to be lower than warning/critical
* gt - current value on the device has to be higher than warning/critical

##### Examples of plugin input data below.

----

Arris C4 CMTS:
```json
{
  "cmts_card": [
    {
      "name": "SCM A",
      "temperature": {
        "warning": 33,
        "critical": 38,
      },
      "cpu": {
        "warning": 90,
        "critical": 100,
      }
    }
  ],
  "cmts_snr": [
    {
      "warning": 26,
      "critical": 25
    }
  ]
}
```

Router:
```json
{
  "traffic": [
    {
      "itfIndex": 526,
      "min": 10,
      "max": 20,
      "warning_min": 12,
      "warning_max": 18,
      "type": "IN"
    }
  ],
  "bgp": [
    {
      "remote_ip": "83.238.40.153",
      "warning": 6895050,
      "critical": 4895050
    }
  ]
}
```

Sensors:
```json
{
  "sensor": [
    {
      "warning": 26,
      "critical": 31,
      "input": "LAN_CONTROLLER_IN6"
    }
  ]
}
```

```json
{
  "sensor": [
    {
      "warning": 26,
      "critical": 31,
      "input": "LB487",
      "id": 1,
      "name": "First sensor"
    },
    {
      "warning": 27,
      "critical": 30,
      "input": "LB487",
      "id": 8,
      "name": "Seconds sensor"
    },
    {
      "warning": 74,
      "critical": 74,
      "input": "LB487",
      "id": 2,
      "name": "Outside sensor"
    }
  ]
}
```

Switch:
```json
{
  "switch_heat": [
    {
      "warning": 50,
      "critical": 55
    }
  ],
  "port": [
    {
      "itfIndex": 8,
      "oper_status": "1"
    }
  ],
  "traffic": [
    {
      "itfIndex": 9,
      "min": 0,
      "max": 5000001,
      "type": "OUT"
    },
    {
      "itfIndex": 9,
      "min": 0,
      "max": 4999994,
      "type": "IN"
    }
  ]
}
```

UPS:
```json
{
  "ups": [
    {
      "voltage": {
        "warning": 170,
        "critical": 0,
      },
      "temperature": {
        "warning": 55,
        "critical": 60,
      }
    }
  ]
}
```

Server:
```json
{
  "server": [
    {
      "fifteen_minute_load": {
        "warning": 3,
        "critical": 4,
        "check_type": "lt"
      },
      "storage_used": {
        "warning": 70,
        "critical": 90,
        "check_type": "lt"
      }
    }
  ]
}
```
