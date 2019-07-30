#! /usr/bin/python3

import argparse
import json
import os
import sys
from time import sleep

from components import print_line, sd_notifier
from components.mi_sensor import MiFloraSensor, MiTempBtSensor, mitemp_parameters, miflora_parameters
from components.mqtt_client import MqttNode

config = None

sensors_list = []

sd_notifier.notify('READY=1')


def mqtt_send_config(mqtt_node, parameters):
    topic_path = '{}/sensor/{}'.format(mqtt_node.base_topic, mqtt_node.node_id)
    base_payload = {"state_topic": "{}/state".format(topic_path).lower()}
    for sensor_type, params in parameters.items():
        payload = dict(base_payload.items())
        payload['unit_of_measurement'] = params['unit']
        payload['value_template'] = "{{ value_json.%s }}" % (sensor_type,)
        payload['name'] = "{} {}".format(mqtt_node.node_id, sensor_type.title())
        if 'device_class' in params:
            payload['device_class'] = params['device_class']
        mqtt_node.client.publish('{}/{}_{}/config'.format(topic_path, mqtt_node.node_id, sensor_type).lower(), json.dumps(payload), 1, True)


def mqtt_send_data(sensor, mqtt_node):
    data = sensor.update()
    if not sensor.status:
        return
    topic = '{}/sensor/{}/state'.format(mqtt_node.base_topic, mqtt_node.node_id).lower()
    print_line("Send Data:%s %s" % (topic, json.dumps(data)))
    mqtt_node.client.publish(topic, json.dumps(data))


def load_sensors():
    if 'sensors' in config:
        sensors_config = config['sensors']

        for sensor_config in sensors_config:
            device_id = sensor_config['device_id']
            mac = sensor_config['mac']
            node = MqttNode(device_id, config['mqtt'])
            if sensor_config['type'] == "mi_flora":
                sensor = MiFloraSensor(device_id, mac)
                mqtt_send_config(node, miflora_parameters)
            elif sensor_config['type'] == "mi_tempbt":
                sensor = MiTempBtSensor(device_id, mac)
                mqtt_send_config(node, mitemp_parameters)
            else:
                raise Exception()
            sensors_list.append({"sensor": sensor, "mqtt_node": node})
    return True


project_name = 'MQTT Gateway'
project_url = "https://github.com/meishild/mqtt-gateway"
parser = argparse.ArgumentParser(description=project_name, epilog='For further details see: ' + project_url)
parser.add_argument('--config_dir', help='set directory where config.ini is located', default=sys.path[0])
parse_args = parser.parse_args()

# Load configuration file
config_dir = parse_args.config_dir

with open(os.path.join(config_dir, 'config.json')) as f:
    config = json.loads(f.read())

while True:
    print_line("Load Sensors Data:")
    for item in sensors_list:
        mqtt_send_data(item['sensor'], item['mqtt_node'])
    sleep(300)
