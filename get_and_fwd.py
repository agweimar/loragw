#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import sys
import time
import zmq
import socket
import json
import pickle
import base64
from  multiprocessing import Process

from config import *

def package_preprocessor(gw_ip, gw_port, frontend_ip, frontend_port):
    # gets forwarded packages from lora gw
    # preprocesses packages
    # forwards them:
    # topic responder: node_id, tmst
    # topic couch: node_id, data
    # topic node_list:

    # Create UDP socket
    gw = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Bind UDP socket to local port
    gw.bind((gw_ip, gw_port))

    context = zmq.Context()
    # publish to forwarder
    feed = context.socket(zmq.PUB)
    feed.connect("tcp://%s:%d" % (frontend_ip, frontend_port))

    node_status = {} 

    while True:

        packet = gw.recv(2048)

        datagram_raw =  json.loads(packet[12:].decode())
        if "rxpk" in datagram_raw:
            packet_good = True
        else:
            packet_good = False

        # filter status packages from GW - what do?
        if packet_good is True:
            # TODO
            # functions for dissecting packages based on protocol versions
        
            timestamp = time.time()
            tmst = datagram_raw["rxpk"][0]['tmst']
            rssi = datagram_raw["rxpk"][0]['rssi']
            datr = datagram_raw["rxpk"][0]['datr']
            freq = datagram_raw["rxpk"][0]['freq']
            node_id = base64.b64decode(datagram_raw["rxpk"][0]['data']).decode().split(',')[0]
            data = base64.b64decode(datagram_raw["rxpk"][0]['data']).decode().split(',')
        
            protocol_version = int(data[1])
        
            if node_id not in node_status:
                node_status[node_id] = {}
            
            if protocol_version is 2:
                """
                   LoRaWAN Class C
                """
            
                data_structure = [ "mac", "protocol_version", "T", "RH", "CO2eq", "Tvoc", "EtOH_raw", "H2_raw"]
                data_dict = dict(zip(data_structure, data))
            
                couch_document = {
                        'tmst': timestamp,
                        #'node_uuid': node_id,
                        #'data':  ast.literal_eval(data),
                        'data': data_dict,
                        'packet_raw': datagram_raw
                        }
        
                print("sending:{0}".format(json.dumps(couch_document)))
                feed.send_string("%s %s" % ("couchdb", json.dumps(couch_document)))
        
            if protocol_version is 3:
                """
                   LoRaWAN Class C
                """
                # ALOHA
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


def main():
    Process(target=forwarder_device, args=(FRONTEND_IP, FRONTEND_PORT, BACKEND_IP, BACKEND_PORT)).start()
    time.sleep(2)
    Process(target=package_preprocessor, args=(GW_UP_IP, GW_UP_PORT, FRONTEND_IP, FRONTEND_PORT)).start()
    print("Starting fake LoRa Package emitter")
    Process(target=fake_emitter, args=(GW_UP_IP, GW_UP_PORT)).start()


if __name__ == '__main__':
	main()
