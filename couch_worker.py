# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import sys
import time
import base64
import json
from cloudant import couchdb
from  multiprocessing import Process

COUCH_BACK_PORT = 7778

COUCH_BACK_IP = "loragw1"

COUCHDB_HOST = 'http://localhost:5984'
COUCHDB_USERNAME = ""
COUCHDB_PASSWORD = ""

WORKER_COUNT = 1

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
        time.sleep(1)
        rep.send_string("processed: %s" % message)

def main():
    for worker in range(WORKER_COUNT):
        print("Starting worker #%d" % worker)
        Process(target=couch_worker, args=(COUCH_BACK_IP, COUCH_BACK_PORT)).start()

if __name__ == '__main__':
	main()
