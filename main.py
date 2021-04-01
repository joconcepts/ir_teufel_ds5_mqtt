#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import json
import time
import threading
import uuid

class IRDecoderstation:
    def __init__(self):
        pass

    def power(self):
        return self.ir_cmnd("0x807F50AF", "0x01FE0AF5")

    def mute(self):
        return self.ir_cmnd("0x807FD02F", "0x01FE0BF4")

    def optical1(self):
        return self.ir_cmnd("0x807F609F", "0x01FE06F9")

    def optical2(self):
        return self.ir_cmnd("0x807FF00F", "0x01FE0FF0")

    def mode(self):
        return self.ir_cmnd("0x807FE21D", "0x01FE47B8")

    def left(self):
        return self.ir_cmnd("0x807FDA25", "0x01FE5BA4")

    def right(self):
        return self.ir_cmnd("0x807F1AE5", "0x01FE58A7")

    def volume_up(self):
        return self.ir_cmnd("0x807F7A85","0x01FE5EA1")

    def volume_down(self):
        return self.ir_cmnd("0x807F6A95", "0x01FE56A9")

    def return_menu(self):
        return self.ir_cmnd("0x807FC03F", "0x01FE03FC")

    def ir_cmnd(self, data, data_lsb):
        return {"Protocol":"NEC","Bits":32,"Data":data,"DataLSB":data_lsb,"Repeat":0}

class Client:
    def __init__(self, host, port, user, passwd):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.uuid = str(uuid.uuid4())
        self.ds = IRDecoderstation()

    def connect(self):
        c = mqtt.Client(client_id=self.uuid)
        c.username_pw_set(self.user, self.passwd)
        c.on_connect = self.on_connect
        c.on_disconnect = self.on_disconnect
        c.on_message = self.on_message
        c.on_log = self.on_log
        c.connect(self.host, self.port, 60)
        self.client = c

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.publish("tele/IRAPI/LWT", "ON")
        client.subscribe("cmnd/IRAPI/#")

    def on_disconnect(self, client, userdata, flags):
        client.publish("tele/IRAPI/LWT", "OFF")

    def on_message(self, client, userdata, msg):
        if msg.payload.decode() != "true":
            return

        if msg.topic == "cmnd/IRAPI/Power":
            arr = self.power()

        if msg.topic == "cmnd/IRAPI/Optical1":
            arr = self.optical1()

        if msg.topic == "cmnd/IRAPI/Optical2":
            arr = self.optical2()

        t = threading.Thread(target=self.send_data, args=(arr,))
        t.start()

    def send_data(self, arr):
        c = Client(HOST, PORT, USER, PASSWD)
        c.connect()
        c.client.loop_start()
    
        for data in arr:
            if "sleep" in data:
                time.sleep(data["sleep"])
                next
    
            c.client.publish("cmnd/IR/irsend", json.dumps(data))
            time.sleep(0.1)
    
        c.client.loop_stop()
        c.client.disconnect()

    def on_log(self, client, userdata, level, buf):
        print("log: ",buf)

    def power(self):
        arr = [
                self.ds.power()
                ]
        return arr

    def optical1(self):
        arr = [
                self.ds.power(),
                {"sleep": 9},
                self.ds.optical1()
                ]
        return arr

    def optical2(self):
        arr = [
                self.ds.power(),
                {"sleep": 9},
                self.ds.optical2(),
                {"sleep": 0.2},
                self.ds.mode(),
                {"sleep": 0.2}
                ]
        for i in range(5):
            arr.append(self.ds.left())
            arr.append({"sleep": 0.2})

        arr.append(self.ds.right())
        arr.append({"sleep": 0.2})

        arr.append(self.ds.return_menu())
        return arr


HOST = "192.168.1.2"
PORT = 1883
USER = "mqtt"
PASSWD = "mqtt"

main_client = Client(HOST, PORT, USER, PASSWD)
main_client.connect()

main_client.client.loop_forever()
