"""
==========================================================================================
MASTER REQUIREMENT REGISTRY (MRR) - Build v1.64 - TOTAL RECONCILIATION
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
[V-LOG-04] Routine Filtering: Selecting a Routine bolds 'Suggested' exercises with ⭐.
[V-LOG-05] Increments: Logger must account for specific exercise weight increments.
[V-LOG-06] Datetime: Log date/time defaults to 'now' but is fully user-editable.
[V-LOG-07] [V-LOCK-DEF]: No creating Exercises/Routines while a workout is active.
[V-LOG-08] Log Schema: WorkoutLogs (id, timestamp, exercise, sets_json, is_sample, routines_json).
[V-LOG-09] Set Removal: Ability to remove a specific set during active logging.
[V-LOG-11] Full History Edit: History tab must allow editing of timestamp and exercise name.
[V-LOG-12] Grid History Edit: History tab must provide structured numeric inputs for every set (Lbs/Reps/RIR/Fail).
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
nav = {"🏠 Home": "Home", "🏋️ Workout": "Workout", "💾 Backup": "Backup", "⚙️ Settings": "Settings", "🛠️ Developer": "Developer"}
for label, target in nav.items():
    if st.sidebar.button(label):
        st.session_state.page = target; save_draft("current_page", target); st.rerun()

# --- 4. PAGE: HOME ---
if st.session_state.page == "Home":
    st.title("Systems Action Center")
    if st.button("⚡ Quick Log", use_container_width=True):
        save_draft("workout_active", "True"); st.session_state.page = "Workout"; save_draft("current_page", "Workout"); st.rerun()

# --- 5. PAGE: WORKOUT ---
elif st.session_state.page == "Workout":
    active = load_draft("workout_active", "False") == "True"
    tabs = st.tabs(["Log Workout", "Workout Definitions", "Workout History"])
    
    with tabs[0]: # LOGGING
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
                if ca.button("➕ Add Set"): sets.append(sets[-1].copy()); save_draft("active_sets", json.dumps(sets)); st.rerun()
                if cb.button("➖ Remove Set") and len(sets) > 1: sets.pop(); save_draft("active_sets", json.dumps(sets)); st.rerun()
                
                if st.button("✅ Commit", type="primary"):
                    ts = datetime.combine(log_date, log_time).isoformat()
                    conn.execute("INSERT INTO WorkoutLogs (id, timestamp, exercise, sets_json, is_sample, routines_json) VALUES (?,?,?,?,?,?)",
                                 (str(uuid.uuid4()), ts, cur_ex, json.dumps(sets), 0, json.dumps(sel_rts)))
                    conn.commit(); save_draft("active_log_ex", "---"); st.rerun()
            if st.button("End Session"): save_draft("workout_active", "False"); save_draft("log_routines", "[]"); st.rerun()
        else:
            if st.button("Start New Workout"): save_draft("workout_active", "True"); st.rerun()

    with tabs[1]: # DEFINITIONS
        if active: st.error("Definitions Locked.")
        else:
            mode = st.radio("Manage:", ["Muscles", "Exercises", "Routines"], horizontal=True)
            with st.expander(f"Add New {mode}"):
                with st.form(f"add_{mode}"):
                    name = st.text_input("Name")
                    if mode == "Exercises":
                        ms = sorted([r[0] for r in conn.execute("SELECT name FROM Muscles").fetchall()])
                        m_sel = st.multiselect("Muscles", ms)
                        wi = st.number_input("Inc", value=2.5)
                    if st.form_submit_button("Save"):
                        if mode == "Muscles": conn.execute("INSERT OR IGNORE INTO Muscles (id, name) VALUES (?,?)", (str(uuid.uuid4()), name))
                        elif mode == "Exercises": conn.execute("INSERT OR IGNORE INTO Exercises (id, name, muscle_ids_json, weight_increment) VALUES (?,?,?,?)", (str(uuid.uuid4()), name, json.dumps(m_sel), wi))
                        elif mode == "Routines": conn.execute("INSERT OR IGNORE INTO Routines (id, name, exercise_ids_json) VALUES (?,?,?)", (str(uuid.uuid4()), name, "[]"))
                        conn.commit(); st.rerun()

            st.subheader(f"Existing {mode}")
            # V-SYS-11 Atomic Scope Query
            if mode == "Muscles":
                for mid, mname in conn.execute("SELECT id, name FROM Muscles").fetchall():
                    c1, c2, c3 = st.columns([3,1,1])
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
                        rx = st.multiselect("Ex", ex_all, json.loads(rex or "[]"), key=f"xr_{rid}")
                        c1, c2 = st.columns(2)
                        if c1.button("Update", key=f"ur_{rid}"):
                            conn.execute("UPDATE Routines SET name=?, exercise_ids_json=? WHERE id=?", (rn, json.dumps(rx), rid)); conn.commit(); st.rerun()
                        if c2.button("Del", key=f"dr_{rid}"):
                            conn.execute("DELETE FROM Routines WHERE id=?", (rid,)); conn.commit(); st.rerun()

    with tabs[2]: # HISTORY
        h_logs = pd.read_sql_query("SELECT * FROM WorkoutLogs ORDER BY timestamp DESC", conn)
        for _, row in h_logs.iterrows():
            with st.expander(f"{row['timestamp']} - {row['exercise']}"):
                nts = st.text_input("Time", row['timestamp'], key=f"ht_{row['id']}")
                nex = st.text_input("Ex", row['exercise'], key=f"hx_{row['id']}")
                h_rts = sorted([r[0] for r in conn.execute("SELECT name FROM Routines").fetchall()])
                nrts = st.multiselect("Rts", h_rts, json.loads(row['routines_json'] or "[]"), key=f"hr_{row['id']}")
                sets_h = json.loads(row['sets_json'])
                up_sets = []
                for si, s in enumerate(sets_h):
                    c1, c2, c3, c4 = st.columns(4)
                    uw = c1.number_input("Lbs", float(s[0]), key=f"hw_{row['id']}_{si}")
                    ur = c2.number_input("Reps", int(s[1]), key=f"hr_{row['id']}_{si}")
                    uri = c3.number_input("RIR", int(s[2]), key=f"hi_{row['id']}_{si}")
                    uf = c4.number_input("Fail", float(s[3]), key=f"hf_{row['id']}_{si}")
                    up_sets.append([uw, ur, uri, uf])
                c1, c2 = st.columns(2)
                if c1.button("Save", key=f"sv_{row['id']}"):
                    conn.execute("UPDATE WorkoutLogs SET timestamp=?, exercise=?, sets_json=?, routines_json=? WHERE id=?", (nts, nex, json.dumps(up_sets), json.dumps(nrts), row['id'])); conn.commit(); st.rerun()
                if c2.button("Del", key=f"dh_{row['id']}"):
                    conn.execute("DELETE FROM WorkoutLogs WHERE id=?", (row['id'],)); conn.commit(); st.rerun()

# --- 7. DEVELOPER ---
elif st.session_state.page == "Developer":
    st.title("🛠️ Developer")
    if st.button("🌱 Seed"):
        mus = ["Chest", "Back", "Quads", "Hamstrings", "Shoulders", "Biceps", "Triceps", "Abs"]
        for m in mus: conn.execute("INSERT OR IGNORE INTO Muscles (id, name) VALUES (?,?)", (str(uuid.uuid4()), m))
        exs = [("Bench Press", ["Chest"], 5.0), ("Squat", ["Quads"], 5.0), ("Deadlift", ["Back"], 10.0), ("OHP", ["Shoulders"], 2.5), ("Curls", ["Biceps"], 1.25), ("Extensions", ["Triceps"], 2.5), ("Row", ["Back"], 5.0), ("Leg Press", ["Quads"], 10.0), ("Lateral Raise", ["Shoulders"], 1.25), ("Plank", ["Abs"], 0.0)]
        for n, m, i in exs: conn.execute("INSERT OR IGNORE INTO Exercises (id, name, muscle_ids_json, weight_increment) VALUES (?,?,?,?)", (str(uuid.uuid4()), n, json.dumps(m), i))
        rts = [("Push Day", ["Bench Press", "OHP"]), ("Pull Day", ["Deadlift", "Row"]), ("Legs", ["Squat", "Leg Press"]), ("Full Body", ["Squat", "Bench Press"]), ("Arms", ["Curls", "Extensions"])]
        for rn, re in rts: conn.execute("INSERT OR IGNORE INTO Routines (id, name, exercise_ids_json) VALUES (?,?,?)", (str(uuid.uuid4()), rn, json.dumps(re)))
        conn.commit(); st.success("Seeded.")
    if st.button("🧪 Generate 20 Variety Samples"):
        exs = [r[0] for r in conn.execute("SELECT name FROM Exercises").fetchall()]
        if not exs: exs = ["Bench Press", "Squat", "Deadlift"]
        for _ in range(20):
            ce = random.choice(exs)
            sd = json.dumps([[random.randint(45,225), random.randint(5,12), random.randint(0,4), round(random.uniform(0,1),1)] for _ in range(3)])
            conn.execute("INSERT INTO WorkoutLogs (id, timestamp, exercise, sets_json, is_sample, routines_json) VALUES (?,?,?,?,?,?)", (str(uuid.uuid4()), datetime.now().isoformat(), ce, sd, 1, "[]"))
        conn.commit(); st.success("Samples added.")
    if st.button("⚠️ FULL WIPE", type="primary"):
        for t in ["Muscles", "Exercises", "Routines", "WorkoutLogs", "DraftState"]: conn.execute(f"DELETE FROM {t}")
        conn.commit(); st.rerun()

elif st.session_state.page == "Backup":
    st.title("💾 Backup")
    if st.button("Export"): shutil.copy2(DB_NAME, os.path.join(BACKUP_DIR, f"manual_{datetime.now().strftime('%H%M%S')}.db"))