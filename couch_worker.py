# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import sys
import time
import base64
import json
import zmq
from cloudant import couchdb
from  multiprocessing import Process
from config import *

WORKER_COUNT = 3

def couch_worker(couch_back_ip, couch_back_port, worker_id):
    # gets all data
    # puts them into couchdb
    context = zmq.Context()
    rep = context.socket(zmq.REP)
    rep.connect("tcp://%s:%s" % (couch_back_ip, couch_back_port))

    server_id=1
    # TODO
    while True:
        message = rep.recv()
        print(message)
        couch_document = {}
        #print("Received request: ", message)
	# open couchdb connection
        with couchdb(COUCHDB_USERNAME, COUCHDB_PASSWORD, url=COUCHDB_HOST) as client:
            # Perform client tasks...
            session = client.session()
            print('Username: {0}'.format(session['userCtx']['name']))
            #print('Databases: {0}'.format(client.all_dbs()))
            
            # Create a database
            print("creating database")
            #node_db = client.create_database(node_id)
            node_db = client['lora_test']
            
            if node_db.exists():
                doc_created = node_db.create_document(couch_document)
                
            if doc_created.exists():
                print("node data saved in couchdb")
                rep.send_string("Worker #%d processed: %s" % (worker_id, message))
	

def main():
    for worker in range(WORKER_COUNT):
        print("Starting worker #%d" % worker)
        Process(target=couch_worker, args=(COUCH_BACK_IP, COUCH_BACK_PORT, worker)).start()

if __name__ == '__main__':
	main()
