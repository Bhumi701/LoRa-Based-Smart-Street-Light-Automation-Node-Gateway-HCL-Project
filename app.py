import streamlit as st, pandas as pd
import db

db.init()
st.set_page_config(page_title="Smart Street Light", layout="wide")
st.title("💡 LoRa Smart Street Light Dashboard")

@st.fragment(run_every=3)
def live():
    with db.conn() as c:
        df = pd.read_sql("SELECT * FROM readings ORDER BY ts DESC LIMIT 400", c)
    if df.empty:
        st.info("Data nahi aaya. Gateway aur node_sim chalao.")
        return
    latest = df.sort_values("ts").groupby("node_id").last().reset_index()
    latest["status"] = latest.apply(
        lambda r: "⚠️ FAULT" if r.fault else ("🟡 ON" if r.brightness else "⚫ OFF"), axis=1)

    a, b, c3 = st.columns(3)
    a.metric("Total Nodes", len(latest))
    b.metric("Lights ON", int((latest.brightness > 0).sum()))
    c3.metric("Faults", int(latest.fault.sum()))

    st.dataframe(latest[["node_id", "status", "lux", "motion", "brightness",
                         "current_mA", "seq"]], use_container_width=True, hide_index=True)

    node = st.selectbox("Chart ke liye node", latest.node_id, key="chart_node")
    h = df[df.node_id == node].sort_values("ts").copy()
    h["time"] = pd.to_datetime(h["ts"], unit="s", utc=True).dt.tz_convert("Asia/Kolkata")
    h = h.set_index("time")
    st.line_chart(h[["lux", "brightness", "current_mA"]])

live()

st.subheader("Control")
c1, c2, c3 = st.columns(3)
node = c1.selectbox("Node", [1, 2, 3, 4])
cmd = c2.selectbox("Command", ["AUTO", "ON", "OFF", "DIM"])
val = c3.slider("Dim %", 0, 100, 50) if cmd == "DIM" else 0
if st.button("Send"):
    db.add_command(node, cmd, val)
    st.success(f"{cmd} → Node {node}")