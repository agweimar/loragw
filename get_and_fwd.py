# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import sys
import time
import zmq
import json
import base64
from  multiprocessing import Process

GW_UP_IP = "127.0.0.1"
GW_UP_PORT = 5555

FRONTEND_IP = "127.0.0.1"
FRONTEND_PORT = 6665

BACKEND_IP = "127.0.0.1"
BACKEND_PORT = 6667


def package_preprocessor(gw_ip, gw_port, frontend_ip, frontend_port):
    # gets forwarded packages from lora gw
    # preprocesses packages
    # forwards them:
    # topic responder: node_id, tmst
    # topic couch: node_id, data
    # topic node_list:
    # TODO
    # need poller?

    node_status = {} 

    context = zmq.Context()

    # connect to gw port
    socket = context.socket(zmq.PAIR)
    socket.connect("tcp://%s:%d" % (gw_ip, gw_port))

    # publish to forwarder
    feed = context.socket(zmq.PUB)
    feed.connect("tcp://%s:%d" % (frontend_ip, frontend_port))
    
    while True:
        packet = socket.recv()

        # filter status packages from GW - what do?
        packet_good = packet[12:] != b''

        if packet_good:
            # TODO
            # functions for dissecting packages based on protocol versions

            datagram_raw =  json.loads(packet.decode())
            #print(datagram_raw)
            timestamp = time.time()
            tmst = datagram_raw["rxpk"][0]['tmst']
            rssi = datagram_raw["rxpk"][0]['rssi']
            datr = datagram_raw["rxpk"][0]['datr']
            freq = datagram_raw["rxpk"][0]['freq']
            node_id = base64.b64decode(datagram_raw["rxpk"][0]['data']).decode().split(',')[0]
            data = base64.b64decode(datagram_raw["rxpk"][0]['data']).decode().split(',')[1:]

            if node_id not in node_status:
                node_status[node_id] = {}
            node_status[node_id]['last_rec'] = timestamp
            node_status[node_id]['tmst'] = tmst
            node_status[node_id]['rssi'] = rssi
            node_status[node_id]['datr'] = datr
            node_status[node_id]['freq'] = freq

            print(rssi)
            feed.send_string("%s %s" % ("couchdb", data))
            # ALOHA
            #  push to lora_responder
            feed.send_string("%s %s" % ("responder", node_status[node_id]))


def forwarder_device(frontend_ip, frontend_port, backend_ip, backend_port):

    try:
        context = zmq.Context(1)
        # Socket facing clients
        frontend = context.socket(zmq.SUB)
        frontend.bind("tcp://%s:%d" % (frontend_ip, frontend_port))
        frontend.setsockopt(zmq.SUBSCRIBE, b"")
        # Socket facing services
        backend = context.socket(zmq.PUB)
        backend.bind("tcp://%s:%d" % (backend_ip, backend_port))
        
        print("starting forwarder")
        zmq.device(zmq.FORWARDER, frontend, backend)
    except KeyboardInterrupt:
        pass
    finally:
        frontend.setsockopt(zmq.LINGER, 0)
        frontend.close()
        backend.setsockopt(zmq.LINGER, 0)
        backend.close()
        context.term()

def fake_emitter(gw_ip, gw_port):
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://%s:%d" % (gw_ip, gw_port))
    
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

    fake_msg2 = json.dumps(
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
    			    "rssi": -69,
    			    "stat": 1,
    			    "datr": "SF7BW125"
    			}
    		]}
    		)
    while True:
        socket.send_string(fake_msg)
        socket.send_string(fake_msg2)
        time.sleep(1)

def main():
    Process(target=forwarder_device, args=(FRONTEND_IP, FRONTEND_PORT, BACKEND_IP, BACKEND_PORT)).start()
    time.sleep(2)
    Process(target=package_preprocessor, args=(GW_UP_IP, GW_UP_PORT, FRONTEND_IP, FRONTEND_PORT)).start()
    print("Starting fake LoRa Package emitter")
    Process(target=fake_emitter, args=(GW_UP_IP, GW_UP_PORT)).start()


if __name__ == '__main__':
	main()
