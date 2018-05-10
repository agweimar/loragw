# Desctiption
LoRa packet handling in python using zeromq

It started as a project to learn zmq and still is...

# topology

```
                 +----------+
     +-----------> LoRa GW  |
     |           +----+-----+
     |                |
     |                |
+----+------+   +-----v-------+
| responder |   | get_and_fwd |
+----^------+   +-----+-------+
     |                |
     |                |
     |          +-----v-------+    +------------+
     +----------+  FORWARDER  +---->couch_queuer|
                +-------------+    +----+-------+
                                        |
                                        |
                                   +----v-------+
                                   |   QUEUE    |
                                   +----+-------+
                                        |
                                        |
                                        |
                                   +----v-------+    +----------+
                                   |couch_worker+----> Couch DB |
                                   +------------+    +----------+
```


# TODO

multipart messaging where it makes sense

polling sockets where needed

tidy up:
- nicer configuration handling
- logging
- queue monitor?

documentation

