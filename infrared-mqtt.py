#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import json
import time

class IRDecoderstation:
    def __init__(self, client):
        self.client = client

    def power(self):
        self.send_ir("0x807F50AF", "0x01FE0AF5")

    def mute(self):
        self.send_ir("0x807FD02F", "0x01FE0BF4")

    def optical1(self):
        self.send_ir("0x807F609F", "0x01FE06F9")

    def optical2(self):
        self.send_ir("0x807FF00F", "0x01FE0FF0")

    def mode(self):
        self.send_ir("0x807FE21D", "0x01FE47B8")

    def left(self):
        self.send_ir("0x807FDA25", "0x01FE5BA4")

    def right(self):
        self.send_ir("0x807F1AE5", "0x01FE58A7")

    def volume_up(self):
        self.send_ir("0x807F7A85","0x01FE5EA1")

    def volume_down(self):
        self.send_ir("0x807F6A95", "0x01FE56A9")

    def return_menu(self):
        self.send_ir("0x807FC03F", "0x01FE03FC")

    def send_ir(self, data, data_lsb):
        data = {"Protocol":"NEC","Bits":32,"Data":data,"DataLSB":data_lsb,"Repeat":0}
        self.client.publish("cmnd/IR/irsend", json.dumps(data));

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("cmnd/IRAPI/#")

def on_message(client, userdata, msg):
    topic = msg.topic.split("/")[2]
    if msg.payload.decode() == "true":
        global published_topic
        published_topic = topic

client = mqtt.Client()
client.connect("192.168.1.22",1883,60)
client.username_pw_set("mqtt", "mqtt")

client.on_connect = on_connect
client.on_message = on_message
published_topic = ""

client.loop_start()

ds = IRDecoderstation(client)
try:
    while True:
        global published_topic
        if (published_topic == "Power"):
            ds.power()
            published_topic = ""
        if (published_topic == "Optical2"):
            ds.power()
            time.sleep(10)
            ds.optical2()
            time.sleep(0.5)
            ds.mode()
            time.sleep(0.5)
            for i in range(6):
                ds.right()
                time.sleep(0.5)
            ds.return_menu()
            published_topic = ""
        if (published_topic == "Optical1"):
            ds.power()
            time.sleep(10)
            ds.optical1()
            published_topic = ""
except KeyboardInterrupt:
    print('Interrupted!')

client.loop_stop();
