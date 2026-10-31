import socket, time, math, random, threading
import protocol as P

N_NODES, INTERVAL, THRESH = 4, 3, 300
FAULTY_NODE = 3   # is node ka bulb "kharab" hai

def run_node(nid):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("127.0.0.1", P.NODE_PORT_BASE + nid))
    s.settimeout(INTERVAL)
    mode, manual, seq, motion_until = "AUTO", 0, 0, 0
    while True:
        lux = int(500 + 500 * math.sin(time.time() / 20))   # ~6 min ka din-raat cycle
        motion = random.random() < 0.15
        if motion:
            motion_until = time.time() + 10
        if mode == "AUTO":
            bright = 0 if lux >= THRESH else (100 if time.time() < motion_until else 30)
        else:
            bright = manual
        current = 0 if nid == FAULTY_NODE else max(0, bright * 8 + random.randint(-10, 10))
        seq += 1
        s.sendto(P.encode_up(nid, seq, lux, motion, current, bright, 1 if bright else 0),
                 P.GATEWAY_ADDR)
        try:  # downlink command ka wait (sleep ki tarah kaam karta hai)
            _, cmd, val = P.decode_down(s.recvfrom(16)[0])
            if cmd == "AUTO": mode = "AUTO"
            elif cmd == "ON": mode, manual = "MANUAL", 100
            elif cmd == "OFF": mode, manual = "MANUAL", 0
            elif cmd == "DIM": mode, manual = "MANUAL", val
        except socket.timeout:
            pass

if __name__ == "__main__":
    for i in range(1, N_NODES + 1):
        threading.Thread(target=run_node, args=(i,), daemon=True).start()
    print(f"{N_NODES} nodes running...")
    while True:
        time.sleep(1)