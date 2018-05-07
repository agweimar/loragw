import sys
import time
import base64
import json
#from cloudant import couchdb
import zmq
from zmq.devices.basedevice import ProcessDevice
from  multiprocessing import Process

GW_UP_PORT = 5555
GW_DOWN_PORT = 5556

FRONTEND_PORT = 6665
BACKEND_PORT = 6667

COUCH_FRONT_PORT = 7776
COUCH_BACK_PORT = 7778

GW_UP_IP = "127.0.0.1"
GW_DOWN_IP = "127.0.0.1"

FRONTEND_IP = "127.0.0.1"
BACKEND_IP = "127.0.0.1"

COUCH_FRONT_IP = "127.0.0.1"
COUCH_BACK_IP = "127.0.0.1"

COUCHDB_HOST = 'http://smucl.ipc.uni-tuebingen.de:5984'
COUCHDB_USERNAME = ""
COUCHDB_PASSWORD = ""


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
            tmst = datagram_raw["rxpk"][0]['tmst']
            rssi = datagram_raw["rxpk"][0]['rssi']
            tmst = datagram_raw["rxpk"][0]['tmst']
            node_id = base64.b64decode(datagram_raw["rxpk"][0]['data']).decode().split(',')[0]
            data = base64.b64decode(datagram_raw["rxpk"][0]['data']).decode().split(',')[1:]

            if node_id not in node_status:
                node_status[node_id] = {}
            node_status[node_id]['last_rec'] = time.time()
            node_status[node_id]['tmst'] = tmst
            node_status[node_id]['tmst'] = tmst
            node_status[node_id]['tmst'] = tmst

            print(rssi)
            feed.send_string("%s %s" % ("couchdb", rssi))
            # ALOHA
            #  push to lora_responder
            feed.send_string("%s %s" % ("responder", rssi))

            #print(node_status)
            #print(node_status[node_id])

def lora_responder(gw_ip, gw_port, backend_ip, backend_port):
    # keeps track of when the packed should be answered
    # writes directly to gw
    context = zmq.Context()
    sub = context.socket(zmq.SUB)
    sub.connect("tcp://%s:%d" % (backend_ip, backend_port))
    sub.setsockopt(zmq.SUBSCRIBE, b"responder")

    while True:
        message = sub.recv()
        #print("responder: Received - %s" % message)


def couch_worker(couch_back_ip, couch_back_port):
    # gets all data
    # puts them into couchdb
    context = zmq.Context()
    rep = context.socket(zmq.REP)
    rep.connect("tcp://%s:%s" % (couch_back_ip, couch_back_port))

    server_id=1
    # TODO
    while True:
        message = rep.recv()
        #print("Received request: ", message)
        # -> to couchdb
        time.sleep (1)
        rep.send_string("data processed: %s" % message)

def couch_queuer(backend_ip, backend_port, couch_front_ip, couch_front_port):
    # gets all data
    # puts them into couchdb queue
    context = zmq.Context()
    sub = context.socket(zmq.SUB)
    sub.connect("tcp://%s:%s" % (backend_ip, backend_port))
    sub.setsockopt(zmq.SUBSCRIBE, b"couchdb")

    context = zmq.Context()
    req = context.socket(zmq.REQ)
    req.connect("tcp://%s:%s" % (couch_front_ip, couch_front_port))

    # TODO
    while True:
        message = sub.recv()
        #print("Sending request ", message,"...")
        # put into queue
        req.send(message)
        #  Get the reply.
        reply = req.recv()
        #print("Received reply ", "[", reply, "]")

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

def queue_couch(frontend_ip, frontend_port, backend_ip, backend_port):

    try:
        context = zmq.Context(1)
        # Socket facing clients
        frontend = context.socket(zmq.XREP)
        frontend.bind("tcp://%s:%d" % (frontend_ip, frontend_port))
        # Socket facing services
        backend = context.socket(zmq.XREQ)
        backend.bind("tcp://%s:%d" % (backend_ip, backend_port))
        
        print("starting couch queue")
        zmq.device(zmq.QUEUE, frontend, backend)
    except KeyboardInterrupt:
        pass
    finally:
        frontend.setsockopt(zmq.LINGER, 0)
        frontend.close()
        backend.setsockopt(zmq.LINGER, 0)
        backend.close()
        context.term()

def streamer_device(frontend_ip, frontend_port, backend_ip, backend_port):

    try:
        context = zmq.Context(1)
        # Socket facing clients
        frontend = context.socket(zmq.PULL)
        frontend.bind("tcp://%s:%d" % (frontend_ip, frontend_port))
        # Socket facing services
        backend = context.socket(zmq.PUSH)
        backend.bind("tcp://%s:%d" % (backend_ip, backend_port))
        
        zmq.device(zmq.STREAMER, frontend, backend)
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
    Process(target=queue_couch, args=(COUCH_FRONT_IP, COUCH_FRONT_PORT, COUCH_BACK_IP, COUCH_BACK_PORT)).start()
    time.sleep(2)
    Process(target=couch_worker, args=(COUCH_BACK_IP, COUCH_BACK_PORT)).start()
    Process(target=couch_queuer, args=(BACKEND_IP, BACKEND_PORT, COUCH_FRONT_IP, COUCH_FRONT_PORT)).start()
    Process(target=lora_responder, args=(GW_DOWN_IP, GW_DOWN_PORT, BACKEND_IP, BACKEND_PORT)).start()
    Process(target=package_preprocessor, args=(GW_UP_IP, GW_UP_PORT, FRONTEND_IP, FRONTEND_PORT)).start()
    print("Starting fake LoRa Package emitter")
    Process(target=fake_emitter, args=(GW_UP_IP, GW_UP_PORT)).start()


if __name__ == '__main__':
	main()
