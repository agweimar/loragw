# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from  multiprocessing import Process

from couch_queue import *
from get_and_fwd import *
from responder import *
from config import *


def main():
    Process(target=forwarder_device, args=(FRONTEND_IP, FRONTEND_PORT, BACKEND_IP, BACKEND_PORT)).start()
    Process(target=queue_couch, args=(COUCH_FRONT_IP, COUCH_FRONT_PORT, COUCH_BACK_IP, COUCH_BACK_PORT)).start()
    time.sleep(2)
    Process(target=couch_queuer, args=(BACKEND_IP, BACKEND_PORT, COUCH_FRONT_IP, COUCH_FRONT_PORT)).start()
    Process(target=lora_responder, args=(GW_DOWN_IP, GW_DOWN_PORT, BACKEND_IP, BACKEND_PORT)).start()
    Process(target=package_preprocessor, args=(GW_UP_IP, GW_UP_PORT, FRONTEND_IP, FRONTEND_PORT)).start()

if __name__ == '__main__':
	main()
