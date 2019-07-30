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


class MiSensor:
    def __init__(self, device_id, bt_poller, parameters, cache_timeout=600, force_update=False):
        self._force_update = force_update
        self._cache_timeout = cache_timeout
        self._poller = bt_poller
        self.device_id = device_id
        self.parameters = parameters
        self.status = None
        self.load_sensor()

    def load_sensor(self):
        firmware = None
        name = self.device_id
        mac = self._poller._mac
        try:
            firmware = self._poller.firmware_version()
        except (IOError, BluetoothBackendException):
            print('Initial connection to Mi Flora sensor "{}" ({}) failed.'.format(name, mac))
            self.status = False
            return

        print('Device Id:   "{}"'.format(name))
        print('MAC address:   {}'.format(mac))
        print('Firmware:      {}'.format(firmware))
        print('Initial connection to Mi sensor "{}" ({}) successful'.format(name, mac))
        self.status = True

    def update(self):
        if not self.status:
            self.load_sensor()
            return None

        data = {}
        for param, _ in self.parameters.items():
            data[param] = self._poller.parameter_value(param)
        print('Update sensor "{}" ({}) successful'.format(self.device_id, json.dumps(data)))
        return data


def get_backend():
    backend = None
    try:
        import bluepy.btle  # noqa: F401 pylint: disable=unused-import
        from btlewrap import BluepyBackend
        backend = BluepyBackend
    except ImportError:
        from btlewrap import GatttoolBackend
        backend = GatttoolBackend
    print('MiTempBt is using %s backend.', backend.__name__)
    return backend


mitemp_parameters = OrderedDict([
    (MI_TEMPERATURE, dict(name="AirTemperature", name_pretty='Air Temperature', typeformat='%.1f', unit='°C', device_class="temperature")),
    (MI_BATTERY, dict(name="Battery", name_pretty='Sensor Battery Level', typeformat='%d', unit='%', device_class="battery")),
    (MI_HUMIDITY, dict(name="Humidity", name_pretty='Air Humidity', typeformat='%d', unit='%', device_class="humidity"))
])


class MiTempBtSensor(MiSensor):
    def __init__(self, device_id, mac, cache_timeout=600, force_update=False):
        poller = mitemp_bt_poller.MiTempBtPoller(mac=mac, backend=get_backend(), cache_timeout=cache_timeout)
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
        poller = miflora_poller.MiFloraPoller(mac=mac, backend=get_backend(), cache_timeout=cache_timeout)
        super().__init__(device_id, poller, miflora_parameters, cache_timeout, force_update)
