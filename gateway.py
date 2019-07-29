# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2019-07-29
# version         :1.0
# python_version  :3.4.3
# description     :
# ==============================================================================
import json
from time import sleep

from components.mi_sensor import MiFloraSensor, MiTempBtSensor, mitemp_parameters, miflora_parameters
from components.mqtt_client import MqttNode

config_path = "config.json"
config = None

with open(config_path) as f:
    config = json.loads(f.read())

sensors_list = []


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
    topic = '{}/sensor/{}/state'.format(mqtt_node.base_topic, mqtt_node.node_id).lower()
    print("Send Data:%s %s" % (topic, json.dumps(data)))
    mqtt_node.client.publish(topic, json.dumps(data))


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

    while True:
        for item in sensors_list:
            mqtt_send_data(item['sensor'], item['mqtt_node'])
        sleep(10)
