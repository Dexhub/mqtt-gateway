# -*- coding:utf8 -*-

# author          :haiyang.song
# email           :meishild@gmail.com
# datetime        :2019-07-27
# version         :1.0
# python_version  :3.4.3
# description     :
# ==============================================================================
import ssl
import sys

import paho.mqtt.client as mqtt

_sub_dict = {

}


def on_connect(client, userdata, flags, rc):
    client.publish(userdata['topic'], 'on')
    print("Connected with result code " + str(rc) + userdata + flags)


def on_message(client, userdata, msg):
    print("SEND:" + msg.topic + " " + str(msg.payload.decode('utf-8')))
    if msg.topic in _sub_dict:
        _sub_dict[msg.topic](userdata, msg)


def on_subscribe(client, userdata, mid, granted_qos):
    print("On Subscribed: qos = %d" % granted_qos)


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection %s" % rc)


class MqttNode:
    def __init__(self, node_id, mqtt_config):
        self._property = None
        self._advertise = None
        self._node_id = node_id
        self._base_topic = mqtt_config['base_topic']
        self.client = self.load_client(node_id, mqtt_config)

    @property
    def node_id(self):
        return self._node_id

    @property
    def base_topic(self):
        return self._base_topic

    def load_client(self, node_id, mqtt_config):
        topic = "{}/sensor/{}/device".format(self._base_topic, node_id).lower()
        client = mqtt.Client(node_id)
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_subscribe = on_subscribe
        client.on_disconnect = on_disconnect
        client.will_set(topic, 'off')
        if mqtt_config.get('tls', False):
            # According to the docs, setting PROTOCOL_SSLv23 "Selects the highest protocol version
            # that both the client and server support. Despite the name, this option can select
            # “TLS” protocols as well as “SSL”" - so this seems like a resonable default
            client.tls_set(
                ca_certs=mqtt_config.get('tls_ca_cert', None),
                keyfile=mqtt_config.get('tls_keyfile', None),
                certfile=mqtt_config.get('tls_certfile', None),
                tls_version=ssl.PROTOCOL_SSLv23
            )

        if mqtt_config.get('username'):
            client.username_pw_set(mqtt_config.get('username'), mqtt_config.get('password', None))

        try:
            client.connect(mqtt_config['host'], mqtt_config['port'], keepalive=60)
        except:
            print('MQTT connection error. Please check your settings in the configuration file "config.ini"')
            sys.exit(1)
        client.loop_start()
        client.user_data_set({"topic": topic})
        return client

    def advertise(self, advertise):
        self._advertise = advertise
        return self

    def set_table(self, func):
        if self._advertise is None:
            raise Exception("Subscribe topic: advertise is not Null")
        topic = "%s/cmnd/%s/%s" % (self._base_topic, self._node_id, self._advertise)
        _sub_dict[topic] = func
        return self

    def set_property(self, prop):
        self._property = prop
        return self

    def send(self, message):
        if self._property is None:
            raise Exception("Publish topic message: property is not Null")
        self.client.publish(self._node_id + "/" + self._property, message)
        return self
