import streamlit as st
import requests
from pyvis.network import Network
import streamlit.components.v1 as components
import json
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
        res = requests.get(
            "http://127.0.0.1:8000/graph",
            params={"highlight": highlight}
        )

        data = res.json()

        net = Network(height="600px", width="100%", directed=True)

        # 🔹 Add nodes safely
        for node in data.get("nodes", []):
            net.add_node(
                str(node.get("id")),
                label=str(node.get("label")),
                color=node.get("color", "gray"),
                title=f"Node: {node.get('id')}"
            )

        # 🔹 Add edges safely
        for edge in data.get("edges", []):
            net.add_edge(
                str(edge.get("source")),
                str(edge.get("target"))
            )

        # ❌ REMOVE ALL set_options / options / physics
        # (this is what breaks your graph)

        net.save_graph("graph.html")

        with open("graph.html", "r", encoding="utf-8") as f:
            html = f.read()

        # 🔥 ADD POPUP SCRIPT HERE
        popup_script = """
<script>

function waitForNetwork() {
    if (typeof network !== "undefined") {

        network.on("click", function(params) {

            if (params.nodes.length > 0) {

                var nodeId = params.nodes[0];

                console.log("Clicked node:", nodeId);

                fetch("http://127.0.0.1:8000/node/" + nodeId)
                .then(res => res.json())
                .then(data => {

                    console.log("API Response:", data);

                    let content = "<b>Node Details</b><br><br>";

                    Object.keys(data).forEach(key => {
                        content += "<b>" + key + ":</b> " + data[key] + "<br>";
                    });

                    let popup = document.getElementById("popup");

                    if (!popup) {
                        console.log("Popup not found");
                        return;
                    }

                    popup.innerHTML = content;
                    popup.style.display = "block";
                })
                .catch(err => {
                    console.log("Fetch failed:", err);
                });
            }
        });

    } else {
        setTimeout(waitForNetwork, 500);
    }
}

waitForNetwork();

</script>

<div id="popup" style="
position:fixed;
top:80px;
right:20px;
background:#ffffff;
padding:15px;
border-radius:12px;
box-shadow:0 6px 20px rgba(0,0,0,0.3);
font-size:14px;
min-width:240px;
z-index:9999;
display:none;
">
Click a node
</div>
"""
        html = html.replace("</body>", popup_script + "</body>")
    

        components.html(html, height=650, scrolling=True)

    except Exception as e:
        st.error(f"Graph Error: {e}")

# ---------- LAYOUT ----------
col1, col2 = st.columns([2, 1])

# 🔹 LEFT: GRAPH
with col1:
    st.markdown("## 🔗 Process Graph")

    show_graph(st.session_state.highlight)

    # ---------- LEGEND ----------
    st.markdown("### 🎨 Graph Legend")
    st.markdown("""
    - 🔵 **Sales Order**  
    - 🟠 **Delivery**  
    - 🔴 **Billing**  
    - 🟢 **Highlighted Node**  
    """)

    st.info("💡 Hover over nodes. Use chat to highlight entities.")

# 🔹 RIGHT: CHAT
with col2:
    st.markdown("## 💬 AI Assistant")

    # Fixed chat container (no scroll issue)
    chat_container = st.container(height=500)

    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # Input always visible
    user_input = st.chat_input("Ask your question...")

    if user_input:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        try:
            res = requests.get(
                "http://127.0.0.1:8000/ask",
                params={"question": user_input}
            )

            data = res.json()

            if "error" in data:
                reply = data["error"]
            else:
                reply = data.get("answer", "No answer found.")

                # Update highlight
                if data.get("highlight"):
                    st.session_state.highlight = str(data["highlight"])

        except Exception as e:
            reply = f"Error: {e}"

        # Add assistant response
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