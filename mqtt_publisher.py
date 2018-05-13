# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import sys
import time
import zmq
import json
from  multiprocessing import Process

from config import *

import paho.mqtt.client as mqtt

#client = mqtt.Client()
#client.username_pw_set('hacktm','hacktimi210')
#client.connect('eos.ipc.uni-tuebingen.de')
#client.loop_start()

def mqtt_publisher(backend_ip, backend_port):
    # keeps track of when the packed should be answered
    # writes directly to gw
    import paho.mqtt.client as mqtt
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.connect('eos.ipc.uni-tuebingen.de')
    client.loop_start()

    context = zmq.Context()

    sub = context.socket(zmq.SUB)
    sub.connect("tcp://%s:%d" % (backend_ip, backend_port))
    sub.setsockopt(zmq.SUBSCRIBE, b"rangetest")

    while True:
        raw = sub.recv()
        #print("WAAAAAH: Received - %s" % raw)
        #thomas: 240ac48ddd1c
        msg = json.loads(raw.decode().split(" ",1)[1])

        node_id = str(msg['data']['mac'])
        rssi = str(msg['packet_raw']['rxpk'][0]['rssi'])

        print("node_id: {0} --- message: {1}".format(node_id,msg))
        client.publish("loras", node_id)
        #thomas 
        client.publish(node_id, rssi)

def main():
    Process(target=range_tester, args=(BACKEND_IP, BACKEND_PORT)).start()
 
if __name__ == '__main__':
	main()
