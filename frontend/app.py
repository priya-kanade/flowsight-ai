import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
import sys

# 🔥 allow backend imports
sys.path.append(".")

from backend.main import ask
from backend.graph import build_graph

st.set_page_config(layout="wide")

# ---------- STYLES ----------
st.markdown("""
<style>
.main-header {
    font-size: 32px;
    font-weight: 700;
    color: #1f77b4;
}
.sub-header {
    font-size: 16px;
    color: gray;
    margin-bottom: 20px;
}
.footer {
    text-align: center;
    font-size: 12px;
    color: gray;
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<div class="main-header">FlowSight AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Graph-powered Order-to-Cash Intelligence</div>', unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "highlight" not in st.session_state:
    st.session_state.highlight = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- GRAPH FUNCTION ----------
def show_graph(highlight=None):
    try:
        # ✅ DIRECT FUNCTION CALL (NO API)
        data = build_graph(highlight)

        if not data["nodes"]:
            st.warning("No graph data found. Check database.")
            return

        net = Network(height="600px", width="100%", directed=True)

        # Add nodes
        for node in data.get("nodes", []):
            net.add_node(
                str(node.get("id")),
                label=str(node.get("label")),
                color=node.get("color", "gray")
            )

        # Add edges
        for edge in data.get("edges", []):
            net.add_edge(
                str(edge.get("source")),
                str(edge.get("target"))
            )

        # ✅ FIX: use write_html (important)
        net.write_html("graph.html")

        with open("graph.html", "r", encoding="utf-8") as f:
            html = f.read()

        components.html(html, height=650, scrolling=True)

    except Exception as e:
        st.error(f"Graph Error: {e}")

# ---------- LAYOUT ----------
col1, col2 = st.columns([2, 1])

# 🔹 LEFT: GRAPH
with col1:
    st.markdown("## 🔗 Process Graph")
    show_graph(st.session_state.highlight)

    st.markdown("### 🎨 Graph Legend")
    st.markdown("""
    - 🔵 **Sales Order**  
    - 🟠 **Delivery**  
    - 🔴 **Billing**  
    - 🟢 **Highlighted Node**  
    """)

    st.info("💡 Use chat to highlight entities.")

# 🔹 RIGHT: CHAT
with col2:
    st.markdown("## 💬 AI Assistant")

    chat_container = st.container(height=500)

    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    user_input = st.chat_input("Ask your question...")

    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        try:
            # ✅ DIRECT FUNCTION CALL (NO API)
            data = ask(user_input)

            if "error" in data:
                reply = data["error"]
            else:
                reply = data.get("answer", "No answer found.")

                if data.get("highlight"):
                    st.session_state.highlight = str(data["highlight"])

        except Exception as e:
            reply = f"Error: {e}"

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply
        })

        st.rerun()

# ---------- FOOTER ----------
st.markdown("""
<div class="footer">
Built using LLM + Graph + SQL | FlowSight AI
</div>
""", unsafe_allow_html=True)