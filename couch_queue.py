# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import sys
import time
import zmq
from  multiprocessing import Process

BACKEND_IP = "127.0.0.1"
BACKEND_PORT = 6667

COUCH_FRONT_IP = "127.0.0.1"
COUCH_FRONT_PORT = 7776

COUCH_BACK_IP = "127.0.0.1"
COUCH_BACK_PORT = 7778

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
        print("Received reply ", "[", reply, "]")

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

def main():
    Process(target=queue_couch, args=(COUCH_FRONT_IP, COUCH_FRONT_PORT, COUCH_BACK_IP, COUCH_BACK_PORT)).start()
    time.sleep(2)
    Process(target=couch_queuer, args=(BACKEND_IP, BACKEND_PORT, COUCH_FRONT_IP, COUCH_FRONT_PORT)).start()

if __name__ == '__main__':
	main()
