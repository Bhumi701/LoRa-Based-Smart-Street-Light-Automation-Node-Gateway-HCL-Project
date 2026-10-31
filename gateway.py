import socket
import protocol as P, db

db.init()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(P.GATEWAY_ADDR)
s.settimeout(1)
print("Gateway listening...")

while True:
    try:
        d = P.decode_up(s.recvfrom(64)[0])
        fault = 1 if d["brightness"] > 0 and d["current_mA"] < 50 else 0  # light ON par current ~0
        db.save_reading(d, fault)
    except socket.timeout:
        pass
    for c in db.pop_commands():  # dashboard ke commands node ko bhejo
        s.sendto(P.encode_down(c["node_id"], c["cmd"], c["value"]),
                 ("127.0.0.1", P.NODE_PORT_BASE + c["node_id"]))
        print("Sent", dict(c))