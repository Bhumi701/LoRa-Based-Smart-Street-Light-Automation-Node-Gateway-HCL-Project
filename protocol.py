import struct

UP = "<BHHBHBB"   # node_id, seq, lux, motion, current_mA, brightness, state
DOWN = "<BBB"     # node_id, cmd, value
CMDS = {"AUTO": 0, "ON": 1, "OFF": 2, "DIM": 3}
GATEWAY_ADDR = ("127.0.0.1", 5005)
NODE_PORT_BASE = 6000

def encode_up(node_id, seq, lux, motion, current, bright, state):
    return struct.pack(UP, node_id, seq, lux, int(motion), current, bright, state)

def decode_up(data):
    k = ("node_id", "seq", "lux", "motion", "current_mA", "brightness", "state")
    return dict(zip(k, struct.unpack(UP, data)))

def encode_down(node_id, cmd, value=0):
    return struct.pack(DOWN, node_id, CMDS[cmd], value)

def decode_down(data):
    nid, cmd, val = struct.unpack(DOWN, data)
    return nid, {v: k for k, v in CMDS.items()}[cmd], val