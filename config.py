# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

GW_UP_IP = "127.0.0.1"
GW_UP_PORT = 5555

GW_DOWN_IP = "127.0.0.1"
GW_DOWN_PORT = 5556

FRONTEND_IP = "127.0.0.1"
FRONTEND_PORT = 6665

BACKEND_IP = "127.0.0.1"
BACKEND_PORT = 6667

COUCH_FRONT_IP = "127.0.0.1"
COUCH_FRONT_PORT = 7776

COUCH_BACK_IP = "134.2.210.135"
COUCH_BACK_PORT = 7778

COUCHDB_HOST = 'http://smucl.ipc.uni-tuebingen.de:5984'
COUCHDB_USERNAME = ""
COUCHDB_PASSWORD = ""

with open("cred.login", 'r') as pwfile:
    login, pw = pwfile.readline().strip('\n').split(':')
    COUCHDB_USERNAME = login
    COUCHDB_PASSWORD = pw

