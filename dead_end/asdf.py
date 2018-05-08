import sys
import time
import zmq
import base64
import json
from cloudant import couchdb
from  multiprocessing import Process

GW_PORT = 1650
FRONTEND_PORT = 665
BACKEND_PORT = 667

GW_IP = "127.0.0.1"
FRONTEND_IP = "127.0.0.1"
BACKEND_IP = "127.0.0.1"

COUCHDB_HOST = 'http://smucl.ipc.uni-tuebingen.de:5984'
COUCHDB_USERNAME = ""
COUCHDB_PASSWORD = ""

node_status = {} 

def package_preprocessor(gw_port, queue_port):
    # gets forwarded packages from lora gw
    # pushes to responders
    # puts package into queue for further processing
    # TODO
    # need poller?

    context = zmq.Context()

    # connect to gw port
    socket = context.socket(zmq.PAIR)
    socket.connect("tcp://%s:%s" % (GW_IP, gw_port))

    # push to package responders
    push = context.socket(zmq.PUB)
    push.bind("tcp://%s:%s" % (PUB_IP, pub_port))
    
    while True:
        packet = socket.recv()

        # filter status packages from GW - what do?
        packet_good = packet[12:] != b''

        if packet_good:
            # TODO
            # functions for dissecting packages based on protocol versions

            datagram_raw =  json.loads(packet.decode())
            print(datagram_raw)
            tmst = datagram_raw["rxpk"][0]['tmst']
            tmst = datagram_raw["rxpk"][0]['tmst']
            tmst = datagram_raw["rxpk"][0]['tmst']
            tmst = datagram_raw["rxpk"][0]['tmst']
            tmst = datagram_raw["rxpk"][0]['tmst']
            node_id = base64.b64decode(datagram_raw["rxpk"][0]['data']).decode().split(',')[0]
            data = base64.b64decode(datagram_raw["rxpk"][0]['data']).decode().split(',')[1:]

            if node_id not in node_status:
                node_status[node_id] = {}
            node_status[node_id]['last_rec'] = time.time()
            node_status[node_id]['tmst'] = tmst
            node_status[node_id]['tmst'] = tmst
            node_status[node_id]['tmst'] = tmst
            node_status[node_id]['tmst'] = tmst
            node_status[node_id]['tmst'] = tmst
            # TODO
            # spawn sub worker with timeout
            #pub.send_string("%s %s" % (node_id, data))
            # send to queue

            # ALOHA
            #  push to lora_responder
            # spawn consumer
            print(node_status)

def queue_device(frontend_ip, frontend_port, backend_ip, backend_port):

    queuedevice = ProcessDevice(zmq.QUEUE, zmq.XREP, zmq.XREQ)
    queuedevice.bind_in("tcp://%s:%d" % (frontend_ip, frontend_port))
    queuedevice.bind_out("tcp://%s:%d" % (backend_ip, backend_port))
    queuedevice.setsockopt_in(zmq.HWM, 1)
    queuedevice.setsockopt_out(zmq.HWM, 1)
    queuedevice.start()
    time.sleep (2)



def lora_responder(gw_port, pusher_port)
    # keeps track of when the packed should be answered
    # writes directly to gw
    pass
   

def couch_worker(sub_port, client_ids):
    # requests new node list from queue
    # requests new node data from queue
    #print("Worker #%s connecting..." % client_id)
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt_string(zmq.SUBSCRIBE, client_id)
    socket.connect("tcp://%s:%s" % (PUB_IP, sub_port))

    while True:
        message = socket.recv()
        print("Client: Received - %s" % message)
        # TODO
        # -> to couchdb

def send_zipped_pickle(socket, obj, flags=0, protocol=-1):
    """pickle an object, and zip the pickle before sending it"""
    p = pickle.dumps(obj, protocol)
    z = zlib.compress(p)
    return socket.send(z, flags=flags)

def recv_zipped_pickle(socket, flags=0, protocol=-1):
    """inverse of send_zipped_pickle"""
    z = socket.recv(flags)
    p = zlib.decompress(z)
    return pickle.loads(p)


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
    Process(target=queue_device, args=()).start()
    Process(target=couch_worker, args=()).start()
    Process(target=lora_responder, args=()).start()
    Process(target=package_preprocessor, args=()).start()
    sleep(1)
    print("Starting fake LoRa Package emitter")
    Process(target=fake_emitter, args=(GW_PORT,)).start()


if __name__ == '__main__':
	main()
