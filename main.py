import sys
import time
import zmq
import base64
import json
from cloudant import couchdb

from  multiprocessing import Process

import random

GW_PORT = 1650
PUB_PORT = 5555

COUCHDB_HOST = 'http://smucl.ipc.uni-tuebingen.de:5984'
COUCHDB_USERNAME = ""
COUCHDB_PASSWORD = ""

node_status = {} 


def producer(gw_port, pub_port):

    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect("tcp://localhost:%s" % gw_port)

    pub = context.socket(zmq.PUB)
    pub.connect("tcp://localhost:%s" % pub_port)
    
    while True:
        packet = socket.recv()

        packet_good = packet[12:] != b''

        if packet_good:
            datagram_raw =  json.loads(packet.decode())
            print(datagram_raw)
            tmst = datagram_raw["rxpk"][0]['tmst']
            node_id = base64.b64decode(datagram_raw["rxpk"][0]['data']).decode().split(',')[0]
            data = base64.b64decode(datagram_raw["rxpk"][0]['data']).decode().split(',')[1:]

            if node_id not in node_status:
                node_status[node_id] = {}
            node_status[node_id]['last_rec'] = time.time()
            node_status[node_id]['tmst'] = tmst
            # TODO
            # spawn sub worker with timeout
            pub.send_string("%s %s" % (node_id, data))
            # ALOHA
            # spawn consumer
            print(node_status)


def testsub(sub_port, client_id):
    #print("Worker #%s connecting..." % client_id)
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt_string(zmq.SUBSCRIBE, client_id)
    socket.connect("tcp://localhost:%s" % sub_port)

    while True:
        message = socket.recv()
        print("Client: Received - %s" % message)
        # TODO
        # -> to couchdb

def fake_emitter(gw_port):
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://*:%d" % gw_port)
    
    fake_msg = json.dumps(
    		{ "rxpk": [
    			{
    			    "size": 44,
    			    "codr": "4/5",
    			    "data": "MjQwYWM0OGU0YTgwLDIsMjkuMywzMS41LDQwMCwwLDE3MzEyLDEyODMyLDU=",
    			    "modu": "LORA",
    			    "chan": 1,
    			    "lsnr": 8.2,
    			    "freq": 868.3,
    			    "tmst": 2555639019,
    			    "rfch": 1,
    			    "rssi": -68,
    			    "stat": 1,
    			    "datr": "SF7BW125"
    			}
    		]}
    		)
    while True:
        socket.send_string(fake_msg)
        time.sleep(1)

def main():
    Process(target=fake_emitter, args=(GW_PORT,)).start()
    Process(target=producer, args=(GW_PORT, PUB_PORT)).start()

    Process(target=testsub, args=(PUB_PORT, '240ac48e4a80')).start()

if __name__ == '__main__':
	main()
