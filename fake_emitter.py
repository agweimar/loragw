import zmq
import json

from config import *

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
