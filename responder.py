# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import sys
import time
import zmq
from  multiprocessing import Process

GW_DOWN_IP = "127.0.0.1"
GW_DOWN_PORT = 5556

BACKEND_IP = "127.0.0.1"
BACKEND_PORT = 6667


def lora_responder(gw_ip, gw_port, backend_ip, backend_port):
    # keeps track of when the packed should be answered
    # writes directly to gw
    context = zmq.Context()

    # no zmq socket...
    gw = context.socket(zmq.PAIR)
    gw.connect("tcp://%s:%d" % (gw_ip, gw_port))

    sub = context.socket(zmq.SUB)
    sub.connect("tcp://%s:%d" % (backend_ip, backend_port))
    sub.setsockopt(zmq.SUBSCRIBE, b"responder")


    while True:
        message = sub.recv()
        #print("responder: Received - %s" % message)
	# wait until we should answer the package
	#if respond[node_id]:

def main():
    Process(target=lora_responder, args=(GW_DOWN_IP, GW_DOWN_PORT, BACKEND_IP, BACKEND_PORT)).start()

if __name__ == '__main__':
	main()
