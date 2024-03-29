# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2019-07-29
# version         :1.0
# python_version  :3.4.3
# description     :
# ==============================================================================
import json

from mitemp_bt import mitemp_bt_poller
from mitemp_bt.mitemp_bt_poller import MI_TEMPERATURE, MI_BATTERY, MI_HUMIDITY
from miflora.miflora_poller import MiFloraPoller, MI_BATTERY, MI_CONDUCTIVITY, MI_LIGHT, MI_MOISTURE, MI_TEMPERATURE
from miflora import miflora_poller
from btlewrap import BluetoothBackendException, GatttoolBackend
from collections import OrderedDict

from components import print_line


class MiSensor:
    def __init__(self, device_id, bt_poller, parameters, cache_timeout=600, force_update=False):
        self._force_update = force_update
        self._cache_timeout = cache_timeout
        self._poller = bt_poller
        self.device_id = device_id
        self.parameters = parameters
        self.status = None
        self._data = {}
        self.load_sensor()

    def load_sensor(self):
        name = self.device_id
        mac = self._poller._mac
        try:
            print_line('Update Sensor fill cache {}'.format(self.device_id))
            self._poller.clear_cache()
            self._poller.fill_cache()
            print_line('Success Update Sensor fill cache {}'.format(self.device_id))
            firmware = self._poller.firmware_version()
            for param, _ in self.parameters.items():
                self._data[param] = self._poller.parameter_value(param)
            print_line('Update sensor "{}" ({}) successful'.format(self.device_id, json.dumps(self._data)))
        except (IOError, BluetoothBackendException):
            print_line('Initial connection to Mi Sensor "{}" ({}) failed.'.format(name, mac), error=True)
            self.status = False
            return

        if self.status:
            return
        print('Device Id:   "{}"'.format(name))
        print('MAC address:   {}'.format(mac))
        print('Firmware:      {}'.format(firmware))
        print_line('Initial connection to Mi Sensor "{}" ({}) successful'.format(name, mac))
        self.status = True

    def update(self):
        self.load_sensor()
        if not self.status:
            return None
        return self._data


mitemp_parameters = OrderedDict([
    (MI_TEMPERATURE, dict(name="AirTemperature", name_pretty='Air Temperature', typeformat='%.1f', unit='°C', device_class="temperature")),
    (MI_BATTERY, dict(name="Battery", name_pretty='Sensor Battery Level', typeformat='%d', unit='%', device_class="battery")),
    (MI_HUMIDITY, dict(name="Humidity", name_pretty='Air Humidity', typeformat='%d', unit='%', device_class="humidity"))
])


class MiTempBtSensor(MiSensor):
    def __init__(self, device_id, mac, cache_timeout=600, force_update=False):
        from btlewrap import BluepyBackend
        poller = mitemp_bt_poller.MiTempBtPoller(mac=mac, backend=BluepyBackend, cache_timeout=cache_timeout)
        super().__init__(device_id, poller, mitemp_parameters, cache_timeout, force_update)


miflora_parameters = OrderedDict([
    (MI_LIGHT, dict(name="LightIntensity", name_pretty='Sunlight Intensity', typeformat='%d', unit='lux', device_class="illuminance")),
    (MI_TEMPERATURE, dict(name="AirTemperature", name_pretty='Air Temperature', typeformat='%.1f', unit='°C', device_class="temperature")),
    (MI_MOISTURE, dict(name="SoilMoisture", name_pretty='Soil Moisture', typeformat='%d', unit='%', device_class="humidity")),
    (MI_CONDUCTIVITY, dict(name="SoilConductivity", name_pretty='Soil Conductivity/Fertility', typeformat='%d', unit='µS/cm')),
    (MI_BATTERY, dict(name="Battery", name_pretty='Sensor Battery Level', typeformat='%d', unit='%', device_class="battery"))
])


class MiFloraSensor(MiSensor):
    def __init__(self, device_id, mac, cache_timeout=600, force_update=False):
        from btlewrap import BluepyBackend
        poller = miflora_poller.MiFloraPoller(mac=mac, backend=BluepyBackend, cache_timeout=cache_timeout)
        super().__init__(device_id, poller, miflora_parameters, cache_timeout, force_update)
