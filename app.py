import streamlit as st
import asyncio
import websockets
import json
import uuid
import html as html_lib

st.set_page_config(
    page_title="Agentic Swarm",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary:   #080a12;
    --bg-secondary: #0d1017;
    --bg-card:      #111520;
    --bg-hover:     #161b2e;
    --border:       #1a1f35;
    --border-glow:  rgba(108,142,255,0.15);
    --text-primary: #e8edf8;
    --text-muted:   #5a6480;
    --accent:       #6c8eff;
}

* { font-family: 'Inter', sans-serif; box-sizing: border-box; }

[data-testid="stAppViewContainer"] {
    background: linear-gradient(175deg, var(--bg-primary) 0%, #0a0e1a 50%, #070914 100%);
}
[data-testid="stSidebar"] {
    background: var(--bg-secondary);
    border-right: 1px solid var(--border);
}
#MainMenu, footer, header { visibility: hidden; }

/* scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1e2545; border-radius: 8px; }

/* header */
.swarm-hdr {
    text-align: center;
    padding: 18px 0 4px;
}
.swarm-hdr h1 {
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(135deg, #6c8eff 0%, #a78bfa 50%, #f472b6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0; letter-spacing: -0.02em;
}
.swarm-hdr p { color: var(--text-muted); font-size: 0.85rem; margin-top: 4px; }

/* chat window */
.chat-window {
    height: 55vh;
    overflow-y: auto;
    padding: 20px 14px;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 14px;
    display: flex;
    flex-direction: column;
    gap: 2px;
    scroll-behavior: smooth;
    box-shadow: inset 0 2px 20px rgba(0,0,0,0.3);
}

/* empty state */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #2a3050;
    font-size: 1rem;
    gap: 8px;
}
.empty-state .big-emoji { font-size: 3rem; opacity: 0.4; }

/* message row */
.msg-row {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    animation: fadeSlide 0.35s cubic-bezier(0.16,1,0.3,1);
    padding: 10px 12px;
    border-radius: 10px;
    transition: background 0.2s;
}
.msg-row:hover { background: var(--bg-hover); }
@keyframes fadeSlide {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* avatar */
.avatar {
    width: 38px; height: 38px; min-width: 38px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.95rem; color: #fff; flex-shrink: 0;
}

/* bubble */
.msg-bubble { flex: 1; min-width: 0; }
.msg-header { display: flex; align-items: center; gap: 8px; margin-bottom: 3px; }
.agent-name { font-weight: 700; font-size: 0.84rem; }
.msg-tag {
    font-size: 0.65rem; padding: 1px 6px; border-radius: 4px;
    font-family: 'JetBrains Mono', monospace; font-weight: 500;
}
.tag-question   { background: rgba(108,142,255,0.15); color: #6c8eff; }
.tag-correction { background: rgba(251,191,36,0.15); color: #fbbf24; }
.tag-user       { background: rgba(244,114,182,0.15); color: #f472b6; }
.msg-content {
    font-size: 0.88rem; color: var(--text-primary);
    line-height: 1.6; word-wrap: break-word;
}

/* user message special */
.msg-row-user      { background: rgba(244,114,182,0.04); border-left: 3px solid rgba(244,114,182,0.3); }
.msg-row-correction { background: rgba(251,191,36,0.04); border-left: 3px solid rgba(251,191,36,0.3); }

/* status bar */
.status-bar {
    padding: 8px 14px;
    background: linear-gradient(90deg, rgba(108,142,255,0.06), rgba(167,139,250,0.06));
    border: 1px solid var(--border-glow);
    border-radius: 8px;
    color: #8b9ec7;
    font-size: 0.78rem;
    font-family: 'JetBrains Mono', monospace;
    display: flex; align-items: center; gap: 8px;
}

.live-dot {
    display: inline-block; width: 8px; height: 8px;
    border-radius: 50%; background: #22c55e;
    box-shadow: 0 0 8px rgba(34,197,94,0.5);
    animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.35; transform: scale(0.7); }
}

/* stats pills */
.stats-row { display: flex; gap: 10px; flex-wrap: wrap; }
.stat-pill {
    display: flex; align-items: center; gap: 6px;
    padding: 5px 12px; background: var(--bg-card);
    border: 1px solid var(--border); border-radius: 8px;
    font-size: 0.75rem; color: var(--text-muted);
}
.stat-value {
    font-weight: 700; font-size: 0.85rem; color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════
COLOR_MAP = {
    "Strategist": "#6c8eff", "Architect": "#a78bfa", "Engineer": "#34d399",
    "Critic": "#fbbf24", "ProductOwner": "#f87171", "Business": "#60a5fa",
    "Moderator": "#94a3b8", "User": "#f472b6",
}
EMOJI_MAP = {
    "Strategist": "🎯", "Architect": "🏗️", "Engineer": "⚙️",
    "Critic": "🔍", "ProductOwner": "📋", "Business": "💰",
    "Moderator": "🤖", "User": "👤",
}


def build_msg_html(agent, content, msg_idx, streaming=False,
                   is_user=False, is_correction=False):
    color = COLOR_MAP.get(agent, "#94a3b8")
    emoji = EMOJI_MAP.get(agent, "?")
    cursor = '<span style="animation:pulse .8s infinite;color:#6c8eff;">▌</span>' if streaming else ""
    safe = html_lib.escape(content).replace("\n", "<br>")
    tag = ""
    if is_correction:
        tag = '<span class="msg-tag tag-correction">CORRECTION</span>'
    elif is_user:
        tag = '<span class="msg-tag tag-user">YOU</span>'
    elif "?" in content:
        tag = '<span class="msg-tag tag-question">QUESTION</span>'
    row_cls = "msg-row"
    if is_user and is_correction:
        row_cls += " msg-row-correction"
    elif is_user:
        row_cls += " msg-row-user"
    return f"""
    <div class="{row_cls}">
        <div class="avatar" style="background:linear-gradient(135deg,{color},{color}dd);">{emoji}</div>
        <div class="msg-bubble">
            <div class="msg-header">
                <span class="agent-name" style="color:{color}">{agent}</span>
                {tag}
                <span style="flex:1"></span>
                <span style="font-size:.65rem;color:#3a4060;font-family:'JetBrains Mono',monospace;">#{msg_idx}</span>
            </div>
            <div class="msg-content">{safe}{cursor}</div>
        </div>
    </div>"""


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
for k, v in {
    "debate_active": False, "stop_requested": False, "session_id": None,
    "chat_history": [], "status_text": "Idle", "total_msgs": 0,
    "user_msgs_to_send": [], "full_conversation": "", "show_export": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR  (export + legend only)
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 📋 Conversation Export")
    if st.button("📄 Show Full Conversation", use_container_width=True,
                 disabled=len(st.session_state.chat_history) == 0):
        st.session_state.show_export = not st.session_state.show_export

    if st.session_state.show_export and st.session_state.chat_history:
        export = "\n\n".join(
            [f"[{m['agent']}]: {m['content']}" for m in st.session_state.chat_history]
        )
        st.text_area("Select all + copy", value=export, height=250, key="export_area")
        st.download_button(
            "💾 Download .txt", data=export,
            file_name=f"debate_{st.session_state.session_id or 'export'}.txt",
            mime="text/plain", use_container_width=True,
        )

    st.divider()
    st.markdown("### 🎨 Agents")
    for name, color in COLOR_MAP.items():
        if name not in ("Moderator", "User"):
            emoji = EMOJI_MAP.get(name, "?")
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;margin:3px 0;">'
                f'<div style="width:10px;height:10px;border-radius:3px;background:{color};"></div>'
                f'<span style="color:{color};font-size:.8rem;font-weight:600;">{emoji} {name}</span>'
                f'</div>', unsafe_allow_html=True,
            )

# ═══════════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="swarm-hdr">
    <h1>🧠 Agentic Swarm</h1>
    <p>Agents debate continuously • Ask questions & respond to each other • You can intervene anytime</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CONTROL BAR  — always in main area
# ═══════════════════════════════════════════════════════════════════════════════
is_active = st.session_state.debate_active

if not is_active:
    # ── Topic input + Start button ──
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        prompt = st.text_area(
            "💬 Debate Topic / Project Idea",
            placeholder="e.g. Build a self-hosted AI SaaS platform for Discord communities...",
            height=90, key="prompt_input",
        )
    with col_btn:
        st.markdown("")  # spacer
        st.markdown("")
        if st.button("🚀 Start Debate", use_container_width=True, type="primary"):
            if prompt.strip():
                st.session_state.debate_active = True
                st.session_state.stop_requested = False
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.chat_history = []
                st.session_state.total_msgs = 0
                st.session_state.status_text = "Connecting..."
                st.session_state.full_conversation = ""
                st.session_state.show_export = False
                st.rerun()
            else:
                st.warning("⚠️ Please enter a topic first.")
else:
    # Show stop + stats row
    prompt = st.session_state.get("prompt_input", "")
    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        if st.button("🛑 Stop Debate", use_container_width=True, type="secondary"):
            st.session_state.stop_requested = True
    with c2:
        st.markdown(f"""
        <div class="stats-row">
            <div class="stat-pill">💬 <span class="stat-value">{st.session_state.total_msgs}</span> messages</div>
            <div class="stat-pill">👥 <span class="stat-value">6</span> agents active</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        pass  # reserved space

# ═══════════════════════════════════════════════════════════════════════════════
# STATUS BAR
# ═══════════════════════════════════════════════════════════════════════════════
status_ph = st.empty()
if is_active:
    status_ph.markdown(
        f'<div class="status-bar"><span class="live-dot"></span>{st.session_state.status_text}</div>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# CHAT WINDOW
# ═══════════════════════════════════════════════════════════════════════════════
scroll_anchor = st.empty()


def render_chat(history, live_agent="", live_content=""):
    rows = ""
    for i, m in enumerate(history):
        rows += build_msg_html(
            m["agent"], m["content"], i + 1,
            is_user=m.get("is_user", False),
            is_correction=m.get("is_correction", False),
        )
    if live_agent:
        rows += build_msg_html(
            live_agent, live_content, len(history) + 1,
            streaming=True, is_user=(live_agent == "User"),
        )
    if not rows:
        rows = """
        <div class="empty-state">
            <span class="big-emoji">💬</span>
            <span>Enter a topic above and click <b>Start Debate</b> to begin</span>
        </div>"""
    scroll_anchor.markdown(
        f'<div class="chat-window">{rows}</div>', unsafe_allow_html=True,
    )


render_chat(st.session_state.chat_history)

# ═══════════════════════════════════════════════════════════════════════════════
# USER INPUT BAR  (visible only during debate)
# ═══════════════════════════════════════════════════════════════════════════════
if is_active:
    st.markdown("")
    ic1, ic2, ic3 = st.columns([5, 1, 1])
    with ic1:
        user_input = st.text_input(
            "msg", placeholder="Type a question or correction to inject into the debate...",
            key="user_chat_input", label_visibility="collapsed",
        )
    with ic2:
        send_msg = st.button("💬 Send", use_container_width=True)
    with ic3:
        send_correction = st.button("🔧 Correct", use_container_width=True)

    if (send_msg or send_correction) and user_input and user_input.strip():
        is_corr = bool(send_correction)
        st.session_state.user_msgs_to_send.append({
            "content": user_input.strip(), "is_correction": is_corr,
        })
        st.session_state.chat_history.append({
            "agent": "User", "content": user_input.strip(),
            "is_user": True, "is_correction": is_corr,
        })
        st.session_state.total_msgs += 1

# ═══════════════════════════════════════════════════════════════════════════════
# WEBSOCKET LOOP
# ═══════════════════════════════════════════════════════════════════════════════
if is_active:

    async def run():
        sid = st.session_state.session_id
        uri = f"ws://localhost:8000/ws/debate/{sid}"

        try:
            async with websockets.connect(uri) as ws:
                await ws.send(json.dumps({"prompt": prompt}))

                live_agent = ""
                live_content = ""

                while True:
                    # stop signal
                    if st.session_state.stop_requested:
                        try:
                            await ws.send(json.dumps({"type": "stop"}))
                        except Exception:
                            pass
                        st.session_state.stop_requested = False

                    # send user messages
                    while st.session_state.user_msgs_to_send:
                        payload = st.session_state.user_msgs_to_send.pop(0)
                        msg_type = "correction" if payload["is_correction"] else "user_message"
                        try:
                            await ws.send(json.dumps({"type": msg_type, "content": payload["content"]}))
                        except Exception:
                            pass

                    # receive
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=0.5)
                    except asyncio.TimeoutError:
                        render_chat(st.session_state.chat_history, live_agent, live_content)
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        break

                    data = json.loads(raw)

                    if data["type"] == "agent_chunk":
                        agent = data["agent"]
                        chunk = data["content"]
                        if agent == "User":
                            continue
                        if live_agent and live_agent != agent:
                            st.session_state.chat_history.append({
                                "agent": live_agent, "content": live_content,
                                "is_user": False, "is_correction": False,
                            })
                            st.session_state.total_msgs += 1
                            live_content = ""
                        live_agent = agent
                        live_content += chunk
                        render_chat(st.session_state.chat_history, live_agent, live_content)

                    elif data["type"] == "status":
                        st.session_state.status_text = data["message"]
                        status_ph.markdown(
                            f'<div class="status-bar"><span class="live-dot"></span>{data["message"]}</div>',
                            unsafe_allow_html=True,
                        )

                    elif data["type"] == "complete":
                        if live_agent and live_content:
                            st.session_state.chat_history.append({
                                "agent": live_agent, "content": live_content,
                                "is_user": False, "is_correction": False,
                            })
                            st.session_state.total_msgs += 1
                        st.session_state.full_conversation = data.get("full_conversation", "")
                        render_chat(st.session_state.chat_history)
                        status_ph.markdown(
                            f'<div class="status-bar">✅ Debate ended — {data.get("rounds", 0)} messages.</div>',
                            unsafe_allow_html=True,
                        )
                        break

                    elif data["type"] == "error":
                        st.error(f"Server error: {data['message']}")
                        break

                st.session_state.debate_active = False
                st.session_state.stop_requested = False

        except ConnectionRefusedError:
            st.error("❌ Cannot reach backend. Run **start.bat** (or `python main.py`) first!")
            st.session_state.debate_active = False

    asyncio.run(run())
    st.rerun()
