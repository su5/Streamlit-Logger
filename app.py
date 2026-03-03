"""
==========================================================================================
MASTER REQUIREMENT REGISTRY (MRR) - Build v1.65 - UI REDESIGN (BOLD/ATHLETIC)
==========================================================================================
[V-SYS-01] [V-TRUNC] Zero Truncation: Code must be delivered in full; no stubs or '...'.
[V-SYS-02] MRR Header: This exact registry must be included in all code deliveries.
[V-SYS-03] Peer-to-Peer Tone: Adaptive, grounded AI peer; no rigid lecturing.
[V-SYS-04] Interactive Next Steps: End every response with a high-value action.
[V-SYS-05] SIC Audit: Include the Audit table in every technical response.
[V-SYS-06] Persistence: All UI inputs must save to 'DraftState' table.
[V-SYS-07] Zero Latency: Use 'on_change' and 'st.rerun()' for all data-linked selectors.
[V-SYS-08] Explicit Mapping: All SQL INSERTs must name columns explicitly.
[V-SYS-10] UI Deduplication: Manage UI must force query refreshes to prevent ghost duplicates.
[V-SYS-11] Atomic Refresh: Queries must be executed inside the UI loop to ensure fresh state.

[V-UI-01]  Tab Name: 'Exercise' tab MUST be renamed to 'Workout'.
[V-UI-02]  Branding: Sidebar title must be 'Σ SYSTEMS'.
[V-UI-03]  Home Page: Must feature a '⚡ Quick Log' button.
[V-UI-04]  Workout Tabs: Workout page uses st.tabs(['Log', 'Definitions', 'History']).
[V-UI-05]  History: Entries in History must have 'Edit' and 'Delete' buttons.

[V-LOG-01] RIR Input: Every set must have a Reps in Reserve (RIR) numeric input.
[V-LOG-02] Failure Slider: Every set must have a Fail slider (0.0 to 1.0).
[V-LOG-03] Set Duplication: 'Add Set' button duplicates previous set values.
[V-LOG-04] Routine Filtering: Selecting a Routine bolds 'Suggested' exercises with star.
[V-LOG-05] Increments: Logger must account for specific exercise weight increments.
[V-LOG-06] Datetime: Log date/time defaults to 'now' but is fully user-editable.
[V-LOG-07] [V-LOCK-DEF]: No creating Exercises/Routines while a workout is active.
[V-LOG-08] Log Schema: WorkoutLogs (id, timestamp, exercise, sets_json, is_sample, routines_json).
[V-LOG-09] Set Removal: Ability to remove a specific set during active logging.
[V-LOG-11] Full History Edit: History tab must allow editing of timestamp and exercise name.
[V-LOG-12] Grid History Edit: History tab must provide structured numeric inputs for every set.
[V-LOG-13] Routine Persistence: Selected routines must be saved in WorkoutLogs.routines_json.

[V-DEF-01] Creation: Ability to create Muscles, Exercises, and Routines.
[V-DEF-02] Muscle Mgmt: Interactive rename/delete for existing Muscles.
[V-DEF-03] Exercise Mgmt: Interactive rename/delete/mapping for existing Exercises.
[V-DEF-04] Routine Mgmt: Interactive rename/delete/mapping for existing Routines.
[V-DEF-05] Weight Inc: Exercises MUST include a weight_increment field (default 2.5).

[V-DEV-01] Wipe System: Button must use primary (red) color and delete all rows.
[V-DEV-02] Seed High-Fi: Seeding must provide exactly 8 Muscles, 10 Exercises, 5 Routines.
[V-DEV-03] Sample Factory: Generate 20 logs with randomized metrics (is_sample=1).
[V-DEV-04] Clear Samples: Developer tool to delete ONLY sample logs.
[V-DEV-07] Variety Factory: Sample generator must pull from the full available exercise list.

[V-REC-01] Home Detection: If WorkoutLogs count == 0, show recovery UI on Home.
[V-REC-04] Modulo-5: Auto-backups on session end must rotate through 5 files.

[V-THEME-01] Bold/Athletic CSS: Dark base (#0d0d0d), electric lime accent (#C8FF00),
             Barlow Condensed headers, DM Mono data labels, sharp high-contrast UI.
==========================================================================================
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, time
import uuid
import json
import random
import os
import shutil

# --- PAGE CONFIG (must be first Streamlit call) ---
st.set_page_config(
    page_title="Σ SYSTEMS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME INJECTION ---
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800;900&family=DM+Mono:wght@400;500&display=swap');

/* ── BASE ───────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
}

.stApp {
    background-color: #0d0d0d;
    color: #f0f0f0;
}

/* ── SIDEBAR ────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #111111 !important;
    border-right: 2px solid #C8FF00;
}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #f0f0f0 !important;
}

[data-testid="stSidebar"] h1 {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 2.4rem !important;
    font-weight: 900 !important;
    letter-spacing: 0.12em !important;
    color: #C8FF00 !important;
    text-transform: uppercase;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #C8FF00;
    margin-bottom: 1.2rem;
}

[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #f0f0f0 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 0 !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase;
    width: 100%;
    text-align: left !important;
    padding: 0.5rem 1rem !important;
    margin-bottom: 4px !important;
    transition: all 0.15s ease !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: #C8FF00 !important;
    color: #0d0d0d !important;
    border-color: #C8FF00 !important;
}

/* ── HEADINGS ───────────────────────────────────────────── */
h1, h2, h3, h4 {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 900 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase;
    color: #ffffff !important;
}

h1 { font-size: 3rem !important; border-bottom: 3px solid #C8FF00; padding-bottom: 0.3rem; }
h2 { font-size: 2rem !important; color: #C8FF00 !important; }
h3 { font-size: 1.5rem !important; }

/* ── BUTTONS ────────────────────────────────────────────── */
.stButton > button {
    background-color: #1a1a1a !important;
    color: #f0f0f0 !important;
    border: 1.5px solid #333 !important;
    border-radius: 0px !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase;
    padding: 0.4rem 1.2rem !important;
    transition: all 0.12s ease !important;
}

.stButton > button:hover {
    background-color: #C8FF00 !important;
    color: #0d0d0d !important;
    border-color: #C8FF00 !important;
    transform: translateY(-1px);
}

/* Primary (type="primary") buttons */
.stButton > button[kind="primary"],
.stButton > button[data-testid*="primary"] {
    background-color: #C8FF00 !important;
    color: #0d0d0d !important;
    border-color: #C8FF00 !important;
    font-size: 1.1rem !important;
}

.stButton > button[kind="primary"]:hover {
    background-color: #ffffff !important;
    border-color: #ffffff !important;
}

/* ── INPUTS ─────────────────────────────────────────────── */
input[type="text"],
input[type="number"],
textarea,
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background-color: #1a1a1a !important;
    color: #f0f0f0 !important;
    border: 1.5px solid #333 !important;
    border-radius: 0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.9rem !important;
}

input[type="text"]:focus,
input[type="number"]:focus,
textarea:focus {
    border-color: #C8FF00 !important;
    box-shadow: 0 0 0 2px rgba(200,255,0,0.15) !important;
}

/* ── LABELS ─────────────────────────────────────────────── */
label, .stTextInput label, .stNumberInput label,
.stSelectbox label, .stMultiSelect label,
.stSlider label, .stDateInput label, .stTimeInput label {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #888 !important;
}

/* ── SELECTBOX / MULTISELECT ────────────────────────────── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background-color: #1a1a1a !important;
    border: 1.5px solid #333 !important;
    border-radius: 0 !important;
    color: #f0f0f0 !important;
}

/* ── TABS ───────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background-color: #111 !important;
    border-bottom: 2px solid #222 !important;
    gap: 0 !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #666 !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-radius: 0 !important;
    padding: 0.6rem 1.5rem !important;
    border-bottom: 3px solid transparent !important;
}

.stTabs [aria-selected="true"] {
    color: #C8FF00 !important;
    border-bottom: 3px solid #C8FF00 !important;
    background-color: #161616 !important;
}

/* ── EXPANDER ───────────────────────────────────────────── */
[data-testid="stExpander"] {
    background-color: #141414 !important;
    border: 1px solid #222 !important;
    border-radius: 0 !important;
    margin-bottom: 6px !important;
}

[data-testid="stExpander"]:hover {
    border-color: #444 !important;
}

[data-testid="stExpander"] summary {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #ddd !important;
    padding: 0.6rem 1rem !important;
}

/* ── SLIDER ─────────────────────────────────────────────── */
[data-testid="stSlider"] [data-testid="stThumbValue"] {
    color: #C8FF00 !important;
}

.stSlider [role="slider"] {
    background-color: #C8FF00 !important;
}

/* Slider track fill */
[data-testid="stSlider"] [data-testid="stTickBar"] {
    background: #C8FF00 !important;
}

/* ── FORM ───────────────────────────────────────────────── */
[data-testid="stForm"] {
    background-color: #141414 !important;
    border: 1px solid #222 !important;
    border-radius: 0 !important;
    padding: 1rem !important;
}

/* ── RADIO ──────────────────────────────────────────────── */
.stRadio label {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #aaa !important;
}

/* ── SUCCESS / ERROR / INFO ─────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 0 !important;
    border-left: 4px solid #C8FF00 !important;
    background: #141414 !important;
}

/* ── DATAFRAME ──────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* ── SCROLLBAR ──────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #111; }
::-webkit-scrollbar-thumb { background: #333; }
::-webkit-scrollbar-thumb:hover { background: #C8FF00; }

/* ── METRIC ─────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #141414;
    border: 1px solid #222;
    padding: 1rem;
}

[data-testid="stMetricLabel"] {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #666 !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 2.4rem !important;
    font-weight: 900 !important;
    color: #C8FF00 !important;
}

/* ── DIVIDER ────────────────────────────────────────────── */
hr {
    border-color: #222 !important;
}

/* ── MULTISELECT TAGS ───────────────────────────────────── */
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background-color: #C8FF00 !important;
    color: #0d0d0d !important;
    border-radius: 0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
}

/* ── DATE / TIME INPUT ──────────────────────────────────── */
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input {
    background-color: #1a1a1a !important;
    color: #f0f0f0 !important;
    border: 1.5px solid #333 !important;
    border-radius: 0 !important;
    font-family: 'DM Mono', monospace !important;
}

/* ── QUICK LOG HERO BUTTON ──────────────────────────────── */
div[data-testid="column"] .stButton > button,
.block-container .stButton > button {
    /* inherits base styles */
}

/* Make the Quick Log button extra punchy */
.element-container:has(button[kind="secondary"]) + .element-container,
.stButton > button[use_container_width="true"] {
    width: 100% !important;
}
</style>
"""

st.markdown(THEME_CSS, unsafe_allow_html=True)

# --- 1. INITIALIZATION ---
DB_NAME = 'systems_health.db'
BACKUP_DIR = 'backups'
if not os.path.exists(BACKUP_DIR): os.makedirs(BACKUP_DIR)

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS Muscles (id TEXT PRIMARY KEY, name TEXT UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS Exercises (id TEXT PRIMARY KEY, name TEXT UNIQUE, muscle_ids_json TEXT, weight_increment REAL DEFAULT 2.5)')
    c.execute('CREATE TABLE IF NOT EXISTS Routines (id TEXT PRIMARY KEY, name TEXT UNIQUE, exercise_ids_json TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS WorkoutLogs (id TEXT PRIMARY KEY, timestamp DATETIME, exercise TEXT, sets_json TEXT, is_sample INTEGER DEFAULT 0, routines_json TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS DraftState (key TEXT PRIMARY KEY, value TEXT)')

    # Migration
    cursor = c.execute("PRAGMA table_info(WorkoutLogs)")
    cols = [info[1] for info in cursor.fetchall()]
    if "routines_json" not in cols: c.execute("ALTER TABLE WorkoutLogs ADD COLUMN routines_json TEXT")
    conn.commit()
    return conn

conn = init_db()

# --- 2. PERSISTENCE ---
def save_draft(k, v):
    conn.execute("INSERT OR REPLACE INTO DraftState (key, value) VALUES (?, ?)", (k, str(v)))
    conn.commit()

def load_draft(k, d):
    res = conn.execute("SELECT value FROM DraftState WHERE key = ?", (k,)).fetchone()
    return res[0] if res else d

# --- 3. NAVIGATION ---
if 'page' not in st.session_state: st.session_state.page = load_draft("current_page", "Home")

st.sidebar.title("Σ SYSTEMS")
nav = {"⚡ Home": "Home", "🏋️ Workout": "Workout", "💾 Backup": "Backup", "⚙️ Settings": "Settings", "🛠️ Developer": "Developer"}
for label, target in nav.items():
    if st.sidebar.button(label):
        st.session_state.page = target; save_draft("current_page", target); st.rerun()

# --- 4. PAGE: HOME ---
if st.session_state.page == "Home":
    st.title("Action Center")

    log_count = conn.execute("SELECT COUNT(*) FROM WorkoutLogs WHERE is_sample = 0").fetchone()[0]
    total_sets = conn.execute("SELECT sets_json FROM WorkoutLogs WHERE is_sample = 0").fetchall()
    set_count = sum(len(json.loads(r[0])) for r in total_sets if r[0])
    last_log = conn.execute("SELECT timestamp, exercise FROM WorkoutLogs WHERE is_sample = 0 ORDER BY timestamp DESC LIMIT 1").fetchone()

    col1, col2, col3 = st.columns(3)
    col1.metric("Sessions", log_count)
    col2.metric("Total Sets", set_count)
    col3.metric("Last Exercise", last_log[1] if last_log else "—")

    st.markdown("---")

    if st.button("⚡ QUICK LOG", use_container_width=True, type="primary"):
        save_draft("workout_active", "True")
        st.session_state.page = "Workout"
        save_draft("current_page", "Workout")
        st.rerun()

    if log_count == 0:
        st.markdown("""
        <div style="border:1px dashed #333; padding:2rem; text-align:center; margin-top:2rem;">
            <p style="font-family:'Barlow Condensed',sans-serif; font-size:1.2rem; font-weight:700;
               letter-spacing:0.1em; text-transform:uppercase; color:#555;">
               No sessions logged yet. Hit Quick Log to start.
            </p>
        </div>
        """, unsafe_allow_html=True)

# --- 5. PAGE: WORKOUT ---
elif st.session_state.page == "Workout":
    st.title("Workout")
    active = load_draft("workout_active", "False") == "True"
    tabs = st.tabs(["Log Workout", "Workout Definitions", "Workout History"])

    with tabs[0]:  # LOGGING
        if active:
            c1, c2 = st.columns(2)
            log_date = c1.date_input("Date", value=datetime.now().date())
            log_time = c2.time_input("Time", value=datetime.now().time())

            all_rts = sorted([r[0] for r in conn.execute("SELECT name FROM Routines").fetchall()])
            sel_rts = st.multiselect("Routines", all_rts, default=json.loads(load_draft("log_routines", "[]")), key="wr",
                           on_change=lambda: save_draft("log_routines", json.dumps(st.session_state.wr)))

            suggested = []
            for r_name in sel_rts:
                res = conn.execute("SELECT exercise_ids_json FROM Routines WHERE name = ?", (r_name,)).fetchone()
                if res: suggested.extend(json.loads(res[0]))

            ex_data = conn.execute("SELECT name, weight_increment FROM Exercises").fetchall()
            ex_map = {r[0]: r[1] for r in ex_data}
            ex_raw = sorted(list(ex_map.keys()))
            fmt_ex = [f"⭐ {ex}" if ex in suggested else ex for ex in ex_raw]

            sel_fmt = st.selectbox("Exercise", ["---"] + fmt_ex, key="we_fmt")
            cur_ex = sel_fmt.replace("⭐ ", "") if sel_fmt != "---" else "---"
            if cur_ex != load_draft("active_log_ex", "---"): save_draft("active_log_ex", cur_ex); st.rerun()

            if cur_ex != "---":
                sets = json.loads(load_draft("active_sets", "[[0.0, 0, 2, 0.0]]"))
                for i, s in enumerate(sets):
                    with st.expander(f"Set {i+1}", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        sets[i][0] = col1.number_input("Lbs", value=float(s[0]), step=float(ex_map.get(cur_ex, 2.5)), key=f"w_{i}")
                        sets[i][1] = col2.number_input("Reps", value=int(s[1]), key=f"r_{i}")
                        sets[i][2] = col3.number_input("RIR", value=int(s[2]), key=f"rir_{i}")
                        sets[i][3] = st.slider("Fail", 0.0, 1.0, float(s[3]), 0.1, key=f"f_{i}")
                save_draft("active_sets", json.dumps(sets))

                ca, cb = st.columns(2)
                if ca.button("➕ Add Set"):
                    sets.append(sets[-1].copy()); save_draft("active_sets", json.dumps(sets)); st.rerun()
                if cb.button("➖ Remove Set") and len(sets) > 1:
                    sets.pop(); save_draft("active_sets", json.dumps(sets)); st.rerun()

                if st.button("✅ Commit Set", type="primary"):
                    ts = datetime.combine(log_date, log_time).isoformat()
                    conn.execute("INSERT INTO WorkoutLogs (id, timestamp, exercise, sets_json, is_sample, routines_json) VALUES (?,?,?,?,?,?)",
                                 (str(uuid.uuid4()), ts, cur_ex, json.dumps(sets), 0, json.dumps(sel_rts)))
                    conn.commit(); save_draft("active_log_ex", "---"); st.rerun()

            st.markdown("---")
            if st.button("End Session"):
                save_draft("workout_active", "False"); save_draft("log_routines", "[]"); st.rerun()
        else:
            st.markdown("""
            <div style="text-align:center; padding:3rem 0;">
                <p style="font-family:'Barlow Condensed',sans-serif; font-size:1.1rem;
                   font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:#444;">
                   No active session
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("▶ Start New Workout", type="primary", use_container_width=True):
                save_draft("workout_active", "True"); st.rerun()

    with tabs[1]:  # DEFINITIONS
        if active:
            st.error("⛔ Definitions locked while a session is active.")
        else:
            mode = st.radio("Manage:", ["Muscles", "Exercises", "Routines"], horizontal=True)
            with st.expander(f"＋ Add New {mode.upper()}"):
                with st.form(f"add_{mode}"):
                    name = st.text_input("Name")
                    if mode == "Exercises":
                        ms = sorted([r[0] for r in conn.execute("SELECT name FROM Muscles").fetchall()])
                        m_sel = st.multiselect("Muscles", ms)
                        wi = st.number_input("Weight Increment", value=2.5)
                    if st.form_submit_button("Save"):
                        if mode == "Muscles":
                            conn.execute("INSERT OR IGNORE INTO Muscles (id, name) VALUES (?,?)", (str(uuid.uuid4()), name))
                        elif mode == "Exercises":
                            conn.execute("INSERT OR IGNORE INTO Exercises (id, name, muscle_ids_json, weight_increment) VALUES (?,?,?,?)", (str(uuid.uuid4()), name, json.dumps(m_sel), wi))
                        elif mode == "Routines":
                            conn.execute("INSERT OR IGNORE INTO Routines (id, name, exercise_ids_json) VALUES (?,?,?)", (str(uuid.uuid4()), name, "[]"))
                        conn.commit(); st.rerun()

            st.subheader(f"Existing {mode}")
            if mode == "Muscles":
                for mid, mname in conn.execute("SELECT id, name FROM Muscles").fetchall():
                    c1, c2, c3 = st.columns([3, 1, 1])
                    new_n = c1.text_input("N", mname, key=f"edit_m_{mid}", label_visibility="collapsed")
                    if c2.button("Update", key=f"up_m_{mid}"):
                        conn.execute("UPDATE Muscles SET name=? WHERE id=?", (new_n, mid)); conn.commit(); st.rerun()
                    if c3.button("Del", key=f"dl_m_{mid}"):
                        conn.execute("DELETE FROM Muscles WHERE id=?", (mid,)); conn.commit(); st.rerun()
            elif mode == "Exercises":
                for eid, ename, emus, einc in conn.execute("SELECT id, name, muscle_ids_json, weight_increment FROM Exercises").fetchall():
                    with st.expander(f"{ename}"):
                        nn = st.text_input("Name", ename, key=f"nx_{eid}")
                        ni = st.number_input("Inc", float(einc), key=f"ix_{eid}")
                        ms_all = sorted([r[0] for r in conn.execute("SELECT name FROM Muscles").fetchall()])
                        nm = st.multiselect("Muscles", ms_all, json.loads(emus or "[]"), key=f"mx_{eid}")
                        c1, c2 = st.columns(2)
                        if c1.button("Update", key=f"ux_{eid}"):
                            conn.execute("UPDATE Exercises SET name=?, muscle_ids_json=?, weight_increment=? WHERE id=?", (nn, json.dumps(nm), ni, eid)); conn.commit(); st.rerun()
                        if c2.button("Del", key=f"dx_{eid}"):
                            conn.execute("DELETE FROM Exercises WHERE id=?", (eid,)); conn.commit(); st.rerun()
            elif mode == "Routines":
                for rid, rname, rex in conn.execute("SELECT id, name, exercise_ids_json FROM Routines").fetchall():
                    with st.expander(f"{rname}"):
                        rn = st.text_input("Name", rname, key=f"nr_{rid}")
                        ex_all = sorted([r[0] for r in conn.execute("SELECT name FROM Exercises").fetchall()])
                        rx = st.multiselect("Exercises", ex_all, json.loads(rex or "[]"), key=f"xr_{rid}")
                        c1, c2 = st.columns(2)
                        if c1.button("Update", key=f"ur_{rid}"):
                            conn.execute("UPDATE Routines SET name=?, exercise_ids_json=? WHERE id=?", (rn, json.dumps(rx), rid)); conn.commit(); st.rerun()
                        if c2.button("Del", key=f"dr_{rid}"):
                            conn.execute("DELETE FROM Routines WHERE id=?", (rid,)); conn.commit(); st.rerun()

    with tabs[2]:  # HISTORY
        h_logs = pd.read_sql_query("SELECT * FROM WorkoutLogs ORDER BY timestamp DESC", conn)
        if h_logs.empty:
            st.markdown("""
            <p style="font-family:'Barlow Condensed',sans-serif; font-size:1rem; font-weight:700;
               letter-spacing:0.1em; text-transform:uppercase; color:#444; text-align:center; padding:2rem;">
               No history yet.
            </p>
            """, unsafe_allow_html=True)
        for _, row in h_logs.iterrows():
            with st.expander(f"{row['timestamp']} — {row['exercise']}"):
                nts = st.text_input("Timestamp", row['timestamp'], key=f"ht_{row['id']}")
                nex = st.text_input("Exercise", row['exercise'], key=f"hx_{row['id']}")
                h_rts = sorted([r[0] for r in conn.execute("SELECT name FROM Routines").fetchall()])
                nrts = st.multiselect("Routines", h_rts, json.loads(row['routines_json'] or "[]"), key=f"hr_{row['id']}")
                sets_h = json.loads(row['sets_json'])
                up_sets = []
                for si, s in enumerate(sets_h):
                    c1, c2, c3, c4 = st.columns(4)
                    uw = c1.number_input("Lbs", float(s[0]), key=f"hw_{row['id']}_{si}")
                    ur = c2.number_input("Reps", int(s[1]), key=f"hr2_{row['id']}_{si}")
                    uri = c3.number_input("RIR", int(s[2]), key=f"hi_{row['id']}_{si}")
                    uf = c4.number_input("Fail", float(s[3]), key=f"hf_{row['id']}_{si}")
                    up_sets.append([uw, ur, uri, uf])
                c1, c2 = st.columns(2)
                if c1.button("Save", key=f"sv_{row['id']}"):
                    conn.execute("UPDATE WorkoutLogs SET timestamp=?, exercise=?, sets_json=?, routines_json=? WHERE id=?",
                                 (nts, nex, json.dumps(up_sets), json.dumps(nrts), row['id']))
                    conn.commit(); st.rerun()
                if c2.button("Delete", key=f"dh_{row['id']}"):
                    conn.execute("DELETE FROM WorkoutLogs WHERE id=?", (row['id'],))
                    conn.commit(); st.rerun()

# --- 6. PAGE: DEVELOPER ---
elif st.session_state.page == "Developer":
    st.title("Developer Tools")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌱 Seed Data", use_container_width=True):
            mus = ["Chest", "Back", "Quads", "Hamstrings", "Shoulders", "Biceps", "Triceps", "Abs"]
            for m in mus:
                conn.execute("INSERT OR IGNORE INTO Muscles (id, name) VALUES (?,?)", (str(uuid.uuid4()), m))
            exs = [
                ("Bench Press", ["Chest"], 5.0), ("Squat", ["Quads"], 5.0),
                ("Deadlift", ["Back"], 10.0), ("OHP", ["Shoulders"], 2.5),
                ("Curls", ["Biceps"], 1.25), ("Extensions", ["Triceps"], 2.5),
                ("Row", ["Back"], 5.0), ("Leg Press", ["Quads"], 10.0),
                ("Lateral Raise", ["Shoulders"], 1.25), ("Plank", ["Abs"], 0.0)
            ]
            for n, m, i in exs:
                conn.execute("INSERT OR IGNORE INTO Exercises (id, name, muscle_ids_json, weight_increment) VALUES (?,?,?,?)",
                             (str(uuid.uuid4()), n, json.dumps(m), i))
            rts = [
                ("Push Day", ["Bench Press", "OHP"]),
                ("Pull Day", ["Deadlift", "Row"]),
                ("Legs", ["Squat", "Leg Press"]),
                ("Full Body", ["Squat", "Bench Press"]),
                ("Arms", ["Curls", "Extensions"])
            ]
            for rn, re in rts:
                conn.execute("INSERT OR IGNORE INTO Routines (id, name, exercise_ids_json) VALUES (?,?,?)",
                             (str(uuid.uuid4()), rn, json.dumps(re)))
            conn.commit(); st.success("Seeded: 8 muscles, 10 exercises, 5 routines.")

        if st.button("🧪 Generate 20 Samples", use_container_width=True):
            exs = [r[0] for r in conn.execute("SELECT name FROM Exercises").fetchall()]
            if not exs: exs = ["Bench Press", "Squat", "Deadlift"]
            for _ in range(20):
                ce = random.choice(exs)
                sd = json.dumps([[random.randint(45, 225), random.randint(5, 12),
                                   random.randint(0, 4), round(random.uniform(0, 1), 1)] for _ in range(3)])
                conn.execute("INSERT INTO WorkoutLogs (id, timestamp, exercise, sets_json, is_sample, routines_json) VALUES (?,?,?,?,?,?)",
                             (str(uuid.uuid4()), datetime.now().isoformat(), ce, sd, 1, "[]"))
            conn.commit(); st.success("20 sample logs added.")

    with col2:
        if st.button("🗑️ Clear Samples Only", use_container_width=True):
            conn.execute("DELETE FROM WorkoutLogs WHERE is_sample = 1")
            conn.commit(); st.success("Sample logs cleared.")

        if st.button("⚠️ FULL WIPE", type="primary", use_container_width=True):
            for t in ["Muscles", "Exercises", "Routines", "WorkoutLogs", "DraftState"]:
                conn.execute(f"DELETE FROM {t}")
            conn.commit(); st.rerun()

# --- 7. PAGE: BACKUP ---
elif st.session_state.page == "Backup":
    st.title("Backup")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Export Backup", use_container_width=True, type="primary"):
            filename = f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(DB_NAME, os.path.join(BACKUP_DIR, filename))
            st.success(f"Saved: {filename}")

    st.subheader("Existing Backups")
    if os.path.exists(BACKUP_DIR):
        files = sorted(os.listdir(BACKUP_DIR), reverse=True)
        if files:
            for f in files:
                st.markdown(f"<code style='color:#C8FF00'>{f}</code>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#444; font-family:DM Mono,monospace;'>No backups yet.</p>", unsafe_allow_html=True)

# --- 8. PAGE: SETTINGS ---
elif st.session_state.page == "Settings":
    st.title("Settings")
    st.markdown("""
    <p style="font-family:'DM Mono',monospace; color:#555; font-size:0.9rem;">
        No settings configured yet. Future options will appear here.
    </p>
    """, unsafe_allow_html=True)