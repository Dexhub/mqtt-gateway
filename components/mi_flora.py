# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2019-07-27
# version         :1.0
# python_version  :3.4.3
# description     :
# ==============================================================================
import json

from miflora import miflora_poller
from btlewrap import BluepyBackend, BluetoothBackendException
from collections import OrderedDict

from miflora.miflora_poller import MiFloraPoller, MI_BATTERY, MI_CONDUCTIVITY, MI_LIGHT, MI_MOISTURE, MI_TEMPERATURE

parameters = OrderedDict([
    (MI_LIGHT, dict(name="LightIntensity", name_pretty='Sunlight Intensity', typeformat='%d', unit='lux', device_class="illuminance")),
    (MI_TEMPERATURE, dict(name="AirTemperature", name_pretty='Air Temperature', typeformat='%.1f', unit='°C', device_class="temperature")),
    (MI_MOISTURE, dict(name="SoilMoisture", name_pretty='Soil Moisture', typeformat='%d', unit='%', device_class="humidity")),
    (MI_CONDUCTIVITY, dict(name="SoilConductivity", name_pretty='Soil Conductivity/Fertility', typeformat='%d', unit='µS/cm')),
    (MI_BATTERY, dict(name="Battery", name_pretty='Sensor Battery Level', typeformat='%d', unit='%', device_class="battery"))
])


class MiFloraSensor:
    def __init__(self, mqtt_node, device_id, mac, cache_timeout=600, force_update=False):
        self._mac_addr = mac
        self._force_update = force_update
        self._cache_timeout = cache_timeout
        self.device_id = device_id
        self.mqtt_node = mqtt_node
        self.client = mqtt_node.client
        self.poller = miflora_poller.MiFloraPoller(mac=mac, backend=BluepyBackend, cache_timeout=cache_timeout)

    def update(self):
        attempts = 2
        self.poller._cache = None
        self.poller._last_read = None
        data = {}

        while attempts != 0 and not self.poller._cache:
            try:
                self.poller.fill_cache()
                self.poller.parameter_value(MI_LIGHT)
            except (IOError, BluetoothBackendException):
                attempts = attempts - 1
                if attempts > 0:
                    print('Retrying ...')
                self.poller._cache = None
                self.poller._last_read = None
            except Exception as _:
                print("SYSTEM LOAD ERROR", _)

        for param, _ in parameters.items():
            data[param] = self.poller.parameter_value(param)

    def set_cache_timeout(self, cache_timeout):
        if cache_timeout < 10:
            print("cache_timeout to short %s", cache_timeout)
            return
        if cache_timeout != self._cache_timeout:
            self.poller = miflora_poller.MiFloraPoller(self._mac_addr, BluepyBackend, cache_timeout)
            self._cache_timeout = cache_timeout

    def mqtt_send_config(self):
        topic_path = '{}/sensor/{}'.format(self.mqtt_node._base_topic, self.device_id)
        base_payload = {
            "state_topic": "{}/state".format(topic_path).lower()
        }
        for sensor, params in parameters.items():
            payload = dict(base_payload.items())
            payload['unit_of_measurement'] = params['unit']
            payload['value_template'] = "{{ value_json.%s }}" % (sensor,)
            payload['name'] = "{} {}".format(self.device_id, sensor.title())
            if 'device_class' in params:
                payload['device_class'] = params['device_class']
            self.client.publish('{}/{}_{}/config'.format(topic_path, self.device_id, sensor).lower(), json.dumps(payload), 1, True)

    def mqtt_send_data(self):
        data = self.update()
        self.client.publish('{}/sensor/{}/state'.format(self.mqtt_node._base_topic, self.device_id).lower(), json.dumps(data))
