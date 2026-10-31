import sqlite3, time

DB = "streetlight.db"

def conn():
    c = sqlite3.connect(DB, timeout=10)
    c.row_factory = sqlite3.Row
    return c

def init():
    with conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS readings(
            ts REAL, node_id INT, seq INT, lux INT, motion INT,
            current_mA INT, brightness INT, fault INT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS commands(
            id INTEGER PRIMARY KEY AUTOINCREMENT, node_id INT,
            cmd TEXT, value INT, sent INT DEFAULT 0)""")

def save_reading(d, fault):
    with conn() as c:
        c.execute("INSERT INTO readings VALUES(?,?,?,?,?,?,?,?)",
                  (time.time(), d["node_id"], d["seq"], d["lux"], d["motion"],
                   d["current_mA"], d["brightness"], fault))

def add_command(node_id, cmd, value=0):
    with conn() as c:
        c.execute("INSERT INTO commands(node_id,cmd,value) VALUES(?,?,?)",
                  (node_id, cmd, value))

def pop_commands():
    with conn() as c:
        rows = c.execute("SELECT * FROM commands WHERE sent=0").fetchall()
        c.execute("UPDATE commands SET sent=1 WHERE sent=0")
        return rows