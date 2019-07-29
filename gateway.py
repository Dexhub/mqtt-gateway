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

from mqtt_gateway.components.mi_flora import MiFloraSensor
from mqtt_gateway.components.mqtt_client import MqttNode

config_path = "config.json"
config = None

with open(config_path) as f:
    config = json.loads(f.read())

mi_floras = []

if 'mi_flora' in config:
    c_mi_floras = config['mi_flora']

    for flora in c_mi_floras:
        mi_flora_node = MqttNode(flora['device_id'], config['mqtt'])
        sensor = MiFloraSensor(mi_flora_node, flora['device_id'], flora['mac'])
        sensor.mqtt_send_config()
        mi_floras.append(sensor)

while True:
    for flora in mi_floras:
        flora.mqtt_send_data()

    sleep(5)
