"""Live CT-scan chocolate bar quiz.
Players:  https://<your-app>/            (join on their phones)
Host:     https://<your-app>/?host=1     (project this; password = HOST_PASSWORD, default "ctscan")
"""
import io, os, threading, uuid
import streamlit as st

st.set_page_config(page_title="Name That Bar", page_icon="🍫", layout="centered")

# ---- EDIT ME: one entry per scan. Options are shown in this order. ----
QUESTIONS = [
    {"img": "images/aero.gif", "answer": "Aero",
     "options": ["Aero", "Kit Kat", "Crunchie", "Mr. Big"]},
    {"img": "images/coffee-crisp.gif", "answer": "Coffee Crisp",
     "options": ["Twix", "Coffee Crisp", "Caramilk", "Wunderbar"]},
    {"img": "images/kinder.gif", "answer": "Kinder Bueno",
     "options": ["Mars", "Kinder Bueno", "Toblerone", "Snickers"]},
]
HOST_PASSWORD = st.secrets.get("HOST_PASSWORD", os.environ.get("HOST_PASSWORD", "ctscan"))

@st.cache_resource
def game():
    # One shared object for every browser session on this server.
    return {"phase": "lobby", "q": 0, "players": {}, "lock": threading.Lock()}
G = game()

def score(p):
    return sum(1 for i, a in p["answers"].items() if a == QUESTIONS[i]["answer"])

def leaderboard():
    return sorted(G["players"].values(), key=lambda p: (-score(p), p["name"].lower()))

def show_scan():
    st.image(QUESTIONS[G["q"]]["img"], use_container_width=True)

def board(n=8):
    for r, p in enumerate(leaderboard()[:n], 1):
        st.write(f"**{r}.** {p['name']} — {score(p)}/{len(QUESTIONS)}")

# ------------------------------------------------------------------ HOST
def host_view():
    if not st.session_state.get("host_ok"):
        pw = st.text_input("Host password", type="password")
        if pw:
            if pw == HOST_PASSWORD:
                st.session_state.host_ok = True; st.rerun()
            else:
                st.error("Nope.")
        return
    n = len(QUESTIONS)
    with st.sidebar:
        st.header("Host controls")
        try:
            h = st.context.headers.get("Host", "")
            guess = ("http://" if h.startswith(("localhost", "127.")) else "https://") + h if h else ""
        except Exception:
            guess = ""
        url = st.text_input("Quiz URL (for QR code)", value=guess)
        if HOST_PASSWORD == "ctscan":
            st.warning("Using the default host password. Set HOST_PASSWORD in secrets.")
        if st.button("Reset game (kicks everyone)"):
            with G["lock"]:
                G.update(phase="lobby", q=0); G["players"].clear()
            st.rerun()
    c1, c2 = st.columns(2)
    ph = G["phase"]
    if ph == "lobby" and c1.button("▶ Start", type="primary", use_container_width=True):
        G.update(phase="q", q=0); st.rerun()
    if ph == "q" and c1.button("Reveal answer", type="primary", use_container_width=True):
        G["phase"] = "reveal"; st.rerun()
    if ph == "reveal":
        last = G["q"] == n - 1
        if c1.button("Final results" if last else "Next scan ▶", type="primary", use_container_width=True):
            if last: G["phase"] = "end"
            else: G.update(phase="q", q=G["q"] + 1)
            st.rerun()

    @st.fragment(run_every=2)
    def screen():
        ph, qi = G["phase"], G["q"]
        players = list(G["players"].values())
        if ph == "lobby":
            st.title("Name that bar 🍫")
            st.subheader("These chocolate bars were CT scanned. Can you tell which is which?")
            if url:
                try:
                    import qrcode
                    buf = io.BytesIO(); qrcode.make(url).save(buf, format="PNG")
                    st.image(buf.getvalue(), width=260)
                except Exception:
                    pass
                st.code(url, language=None)
            st.metric("Players joined", len(players))
        elif ph in ("q", "reveal"):
            st.markdown(f"#### Scan {qi + 1} of {len(QUESTIONS)}")
            show_scan()
            q = QUESTIONS[qi]
            counts = {o: sum(1 for p in players if p["answers"].get(qi) == o) for o in q["options"]}
            if ph == "q":
                st.metric("Answers in", f"{sum(counts.values())} / {len(players)}")
                st.write(" · ".join(f"**{o}**" for o in q["options"]))
            else:
                st.success(f"It's **{q['answer']}**")
                st.bar_chart(counts)
                board(5)
        else:
            st.title("Final results 🏆")
            board(10)
    screen()

# ---------------------------------------------------------------- PLAYER
def player_view():
    pid = st.query_params.get("pid")
    if not pid or pid not in G["players"]:
        st.title("Name that bar 🍫")
        st.write("Chocolate bars, scanned in a CT machine. Guess which is which.")
        name = st.text_input("Your name", max_chars=20)
        if st.button("Join", type="primary", disabled=not name.strip()):
            pid = uuid.uuid4().hex[:8]
            with G["lock"]:
                G["players"][pid] = {"name": name.strip(), "answers": {}}
            st.query_params["pid"] = pid
            st.rerun()
        return
    me = G["players"][pid]

    @st.fragment(run_every=2)
    def live():
        ph, qi = G["phase"], G["q"]
        st.caption(f"{me['name']} · {score(me)} pts")
        if ph == "lobby":
            st.info("You're in! Waiting for the host to start…")
        elif ph in ("q", "reveal"):
            q = QUESTIONS[qi]
            st.markdown(f"#### Scan {qi + 1} of {len(QUESTIONS)}")
            show_scan()
            mine = me["answers"].get(qi)
            if ph == "q" and mine is None:
                st.write("Which bar is this?")
                for o in q["options"]:
                    if st.button(o, key=f"{qi}-{o}", use_container_width=True):
                        me["answers"][qi] = o
                        st.rerun(scope="fragment")
            elif ph == "q":
                st.info(f"Locked in: **{mine}**. Waiting for the reveal…")
            else:
                if mine == q["answer"]: st.success(f"Yes! It was **{q['answer']}**")
                elif mine: st.error(f"You said {mine}. It was **{q['answer']}**")
                else: st.warning(f"No answer. It was **{q['answer']}**")
        else:
            rank = [p["name"] for p in leaderboard()].index(me["name"]) + 1
            st.title("That's a wrap!")
            st.metric("Your score", f"{score(me)} / {len(QUESTIONS)}", f"rank {rank} of {len(G['players'])}")
            board(5)
    live()

if st.query_params.get("host"):
    host_view()
else:
    player_view()
