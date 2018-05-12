# loragw
LoRa packet handling in python using pyzmq

receives packages from [LoRa Packet Forwarder](https://github.com/Lora-net/packet_forwarder)
and distributes them to various workers

# todo
documentation
=======
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

