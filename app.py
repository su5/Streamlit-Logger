"""
==========================================================================================
MASTER REQUIREMENT REGISTRY (MRR) - Build v1.59 - TOTAL RECONCILIATION
==========================================================================================
[V-SYS-01] [V-TRUNC] Zero Truncation: Code must be delivered in full; no stubs or '...'.
[V-SYS-02] MRR Header: This exact registry must be included in all code deliveries.
[V-SYS-03] Peer-to-Peer Tone: Adaptive, grounded AI peer; no rigid lecturing.
[V-SYS-04] Interactive Next Steps: End every response with a high-value action.
[V-SYS-05] SIC Audit: Include the Audit table in every technical response.
[V-SYS-06] Persistence: All UI inputs must save to 'DraftState' table.
[V-SYS-07] Zero Latency: Use 'on_change' and 'st.rerun()' for all data-linked selectors.
[V-SYS-08] Explicit Mapping: All SQL INSERTs must name columns explicitly.
[V-SYS-09] Schema Resilience: Code must ignore extra columns (e.g., Exercise 9-col bug).

[V-UI-01]  Tab Name: 'Exercise' tab MUST be renamed to 'Workout'.
[V-UI-02]  Branding: Sidebar title must be 'Σ SYSTEMS'.
[V-UI-03]  Home Page: Must feature a '⚡ Quick Log' button.
[V-UI-04]  Workout Tabs: Workout page uses st.tabs(['Log', 'Definitions', 'History']).
[V-UI-05]  History: Entries in History must have 'Edit' and 'Delete' buttons.

[V-LOG-01] RIR Input: Every set must have a Reps in Reserve (RIR) numeric input.
[V-LOG-02] Failure Slider: Every set must have a Fail slider (0.0 to 1.0).
[V-LOG-03] Set Duplication: 'Add Set' button duplicates previous set values.
[V-LOG-04] Routine Filtering: Selecting a Routine bolds 'Suggested' exercises.
[V-LOG-05] Increments: Logger must account for specific exercise weight increments.
[V-LOG-06] Datetime: Log date/time defaults to 'now' but is fully user-editable.
[V-LOG-07] [V-LOCK-DEF]: No creating Exercises/Routines while a workout is active.
[V-LOG-08] Log Schema: WorkoutLogs (id, timestamp, exercise, sets_json, is_sample).
[V-LOG-09] Set Removal: Ability to remove a specific set during active logging.

[V-DEF-01] Creation: Ability to create Muscles, Exercises, and Routines.
[V-DEF-02] Muscle Mgmt: Interactive rename/delete for existing Muscles.
[V-DEF-03] Exercise Mgmt: Interactive rename/delete/mapping for existing Exercises.
[V-DEF-04] Routine Mgmt: Interactive rename/delete/mapping for existing Routines.
[V-DEF-05] Weight Inc: Exercises MUST include a weight_increment field (default 2.5).

[V-DEV-01] Wipe System: Button must use primary (red) color and delete all rows.
[V-DEV-02] Seed High-Fi: Seeding must provide exactly 8 Muscles, 10 Exercises, 5 Routines.
[V-DEV-03] Sample Factory: Generate 20 logs with randomized metrics (is_sample=1).
[V-DEV-04] Clear Samples: Developer tool to delete ONLY sample logs.

[V-REC-01] Home Detection: If WorkoutLogs count == 0, show recovery UI on Home.
[V-REC-02] Auto-Search: Recovery UI must feature 'Search /backups/ for Latest'.
[V-REC-03] Manual Restore: Backup tab and Home recovery must have a file uploader.
[V-REC-04] Modulo-5: Auto-backups on session end must rotate through 5 files.
[V-REC-05] Backup Folder: System must check and create 'backups/' folder on init.
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
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS Muscles (id TEXT PRIMARY KEY, name TEXT UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS Exercises (id TEXT PRIMARY KEY, name TEXT UNIQUE, muscle_ids_json TEXT, weight_increment REAL DEFAULT 2.5)')
    c.execute('CREATE TABLE IF NOT EXISTS Routines (id TEXT PRIMARY KEY, name TEXT UNIQUE, exercise_ids_json TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS WorkoutLogs (id TEXT PRIMARY KEY, timestamp DATETIME, exercise TEXT, sets_json TEXT, is_sample INTEGER DEFAULT 0)')
    c.execute('CREATE TABLE IF NOT EXISTS DraftState (key TEXT PRIMARY KEY, value TEXT)')
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

def restore_database(source_path):
    conn.close()
    shutil.copy2(source_path, DB_NAME)
    st.rerun()

# --- 3. NAVIGATION ---
if 'page' not in st.session_state:
    st.session_state.page = load_draft("current_page", "Home")

st.sidebar.title("Σ SYSTEMS")
nav = {"🏠 Home": "Home", "🏋️ Workout": "Workout", "💾 Backup": "Backup", "⚙️ Settings": "Settings", "🛠️ Developer": "Developer"}
for label, target in nav.items():
    if st.sidebar.button(label):
        st.session_state.page = target; save_draft("current_page", target); st.rerun()

# --- 4. PAGE: HOME ---
if st.session_state.page == "Home":
    st.title("Systems Action Center")
    log_count = conn.execute("SELECT COUNT(*) FROM WorkoutLogs").fetchone()[0]
    if log_count == 0:
        st.info("👋 System empty. Recovery/Seed required.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔍 Search Backups"):
                files = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')]
                if files: restore_database(max([os.path.join(BACKUP_DIR, f) for f in files], key=os.path.getctime))
        with c2:
            h_up = st.file_uploader("📂 Manual Restore", type="db")
            if h_up:
                with open("temp_h.db", "wb") as f: f.write(h_up.getbuffer())
                restore_database("temp_h.db")
    
    if st.button("⚡ Quick Log", use_container_width=True):
        save_draft("workout_active", "True"); st.session_state.page = "Workout"; save_draft("current_page", "Workout"); st.rerun()

# --- 5. PAGE: WORKOUT ---
elif st.session_state.page == "Workout":
    is_active = load_draft("workout_active", "False") == "True"
    tabs = st.tabs(["Log Workout", "Workout Definitions", "Workout History"])
    
    with tabs[0]: # LOGGING
        if is_active:
            c1, c2 = st.columns(2)
            log_date = c1.date_input("Date", value=datetime.now().date())
            log_time = c2.time_input("Time", value=datetime.now().time())
            
            all_rts = sorted([r[0] for r in conn.execute("SELECT name FROM Routines").fetchall()])
            st.multiselect("Routines", all_rts, default=json.loads(load_draft("log_routines", "[]")), key="wr", 
                           on_change=lambda: save_draft("log_routines", json.dumps(st.session_state.wr)))
            
            ex_data = conn.execute("SELECT name, weight_increment FROM Exercises").fetchall()
            ex_map = {r[0]: r[1] for r in ex_data}
            ex_raw = sorted(list(ex_map.keys()))
            
            st.selectbox("Exercise", ["---"] + ex_raw, key="we", on_change=lambda: save_draft("active_log_ex", st.session_state.we))
            
            cur_ex = load_draft("active_log_ex", "---")
            if cur_ex != "---":
                inc = ex_map.get(cur_ex, 2.5)
                sets = json.loads(load_draft("active_sets", "[[0.0, 0, 2, 0.0]]"))
                for i, s in enumerate(sets):
                    with st.expander(f"Set {i+1}", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        sets[i][0] = col1.number_input("Lbs", value=float(s[0]), step=float(inc), key=f"w_{i}")
                        sets[i][1] = col2.number_input("Reps", value=int(s[1]), key=f"r_{i}")
                        sets[i][2] = col3.number_input("RIR", value=int(s[2]), key=f"rir_{i}")
                        sets[i][3] = st.slider("Fail", 0.0, 1.0, float(s[3]), 0.1, key=f"f_{i}")
                save_draft("active_sets", json.dumps(sets))
                
                ca, cb = st.columns(2)
                if ca.button("➕ Add Set"):
                    sets.append(sets[-1].copy()); save_draft("active_sets", json.dumps(sets)); st.rerun()
                if cb.button("➖ Remove Last Set") and len(sets) > 1:
                    sets.pop(); save_draft("active_sets", json.dumps(sets)); st.rerun()
                
                if st.button("✅ Commit Entry", type="primary"):
                    ts = datetime.combine(log_date, log_time).isoformat()
                    conn.execute("INSERT INTO WorkoutLogs (id, timestamp, exercise, sets_json, is_sample) VALUES (?,?,?,?,?)",
                                 (str(uuid.uuid4()), ts, cur_ex, json.dumps(sets), 0))
                    conn.commit(); save_draft("active_log_ex", "---"); st.rerun()

            if st.button("End Session"):
                if load_draft("auto_backup_enabled", "True") == "True":
                    idx = (int(load_draft("auto_bk_idx", "0")) % 5) + 1
                    shutil.copy2(DB_NAME, os.path.join(BACKUP_DIR, f"auto_rotate_{idx}.db"))
                    save_draft("auto_bk_idx", str(idx))
                save_draft("workout_active", "False"); st.rerun()
        else:
            if st.button("Start New Workout"): save_draft("workout_active", "True"); st.rerun()

    with tabs[1]: # DEFINITIONS
        if is_active: st.error("Definitions Locked.")
        else:
            d_sub = st.radio("Manage:", ["Muscles", "Exercises", "Routines"], horizontal=True)
            with st.expander(f"Add New {d_sub}"):
                with st.form(f"add_{d_sub}"):
                    n = st.text_input("Name")
                    if d_sub == "Exercises":
                        ms = [r[0] for r in conn.execute("SELECT name FROM Muscles").fetchall()]
                        m_ids = st.multiselect("Muscle Groups", sorted(ms))
                        wi = st.number_input("Weight Increment (lbs)", value=2.5, step=0.25)
                    if st.form_submit_button("Save"):
                        if d_sub == "Muscles": conn.execute("INSERT OR IGNORE INTO Muscles (id, name) VALUES (?,?)", (str(uuid.uuid4()), n))
                        elif d_sub == "Exercises": conn.execute("INSERT OR IGNORE INTO Exercises (id, name, muscle_ids_json, weight_increment) VALUES (?,?,?,?)", (str(uuid.uuid4()), n, json.dumps(m_ids), wi))
                        elif d_sub == "Routines": conn.execute("INSERT OR IGNORE INTO Routines (id, name, exercise_ids_json) VALUES (?,?,?)", (str(uuid.uuid4()), n, "[]"))
                        conn.commit(); st.rerun()

            st.subheader(f"Manage Existing {d_sub}")
            if d_sub == "Muscles":
                for mid, mname in conn.execute("SELECT id, name FROM Muscles").fetchall():
                    c1, c2, c3 = st.columns([3,1,1])
                    new_n = c1.text_input("Name", value=mname, key=f"m_{mid}", label_visibility="collapsed")
                    if c2.button("Update", key=f"up_m_{mid}"):
                        conn.execute("UPDATE Muscles SET name=? WHERE id=?", (new_n, mid)); conn.commit(); st.rerun()
                    if c3.button("Del", key=f"del_m_{mid}"):
                        conn.execute("DELETE FROM Muscles WHERE id=?", (mid,)); conn.commit(); st.rerun()
            elif d_sub == "Exercises":
                for eid, ename, emus, einc in conn.execute("SELECT id, name, muscle_ids_json, weight_increment FROM Exercises").fetchall():
                    with st.expander(f"{ename} ({einc} lbs inc)"):
                        new_n = st.text_input("Name", value=ename, key=f"ex_n_{eid}")
                        new_inc = st.number_input("Increment", value=float(einc), step=0.25, key=f"ex_i_{eid}")
                        ms = [r[0] for r in conn.execute("SELECT name FROM Muscles").fetchall()]
                        new_mus = st.multiselect("Muscles", sorted(ms), default=json.loads(emus or "[]"), key=f"ex_m_{eid}")
                        c1, c2 = st.columns(2)
                        if c1.button("Update Exercise", key=f"up_ex_{eid}"):
                            conn.execute("UPDATE Exercises SET name=?, muscle_ids_json=?, weight_increment=? WHERE id=?", (new_n, json.dumps(new_mus), new_inc, eid)); conn.commit(); st.rerun()
                        if c2.button("Delete Exercise", key=f"del_ex_{eid}"):
                            conn.execute("DELETE FROM Exercises WHERE id=?", (eid,)); conn.commit(); st.rerun()
            elif d_sub == "Routines":
                for rid, rname, rex in conn.execute("SELECT id, name, exercise_ids_json FROM Routines").fetchall():
                    with st.expander(rname):
                        new_rn = st.text_input("Name", value=rname, key=f"rt_n_{rid}")
                        exs = [r[0] for r in conn.execute("SELECT name FROM Exercises").fetchall()]
                        new_exs = st.multiselect("Exercises", sorted(exs), default=json.loads(rex or "[]"), key=f"rt_x_{rid}")
                        c1, c2 = st.columns(2)
                        if c1.button("Update Routine", key=f"up_rt_{rid}"):
                            conn.execute("UPDATE Routines SET name=?, exercise_ids_json=? WHERE id=?", (new_rn, json.dumps(new_exs), rid)); conn.commit(); st.rerun()
                        if c2.button("Delete Routine", key=f"del_rt_{rid}"):
                            conn.execute("DELETE FROM Routines WHERE id=?", (rid,)); conn.commit(); st.rerun()

    with tabs[2]: # HISTORY
        df = pd.read_sql_query("SELECT * FROM WorkoutLogs ORDER BY timestamp DESC", conn)
        for _, row in df.iterrows():
            with st.expander(f"{row['timestamp']} - {row['exercise']}"):
                nts = st.text_input("TS", value=row['timestamp'], key=f"t_{row['id']}")
                nex = st.text_input("Ex", value=row['exercise'], key=f"x_{row['id']}")
                if st.button("Update Log", key=f"ul_{row['id']}"):
                    conn.execute("UPDATE WorkoutLogs SET timestamp=?, exercise=? WHERE id=?", (nts, nex, row['id'])); conn.commit(); st.rerun()
                if st.button("Delete Log", key=f"dl_{row['id']}"):
                    conn.execute("DELETE FROM WorkoutLogs WHERE id=?", (row['id'],)); conn.commit(); st.rerun()

# --- 6. PAGE: SETTINGS [V-REC-07 RESTORED] ---
elif st.session_state.page == "Settings":
    st.title("⚙️ System Settings")
    st.subheader("Data Redundancy")
    auto_on = load_draft("auto_backup_enabled", "True") == "True"
    new_auto = st.toggle("Enable Modulo-5 Auto-Backups", value=auto_on)
    if new_auto != auto_on:
        save_draft("auto_backup_enabled", str(new_auto)); st.rerun()
    
    st.write(f"Current Rotation Index: **{load_draft('auto_bk_idx', '0')} / 5**")
    st.info("When enabled, the system automatically saves a rolling backup to the /backups/ folder whenever a workout session ends.")

# --- 7. PAGE: DEVELOPER ---
elif st.session_state.page == "Developer":
    st.title("🛠️ Developer Control")
    if st.button("🌱 Seed Defaults (8/10/5)"):
        mus = ["Chest", "Back", "Quads", "Hamstrings", "Shoulders", "Biceps", "Triceps", "Abs"]
        for m in mus: conn.execute("INSERT OR IGNORE INTO Muscles (id, name) VALUES (?,?)", (str(uuid.uuid4()), m))
        exs = [("Bench Press", ["Chest"], 5.0), ("Squat", ["Quads"], 5.0), ("Deadlift", ["Back"], 10.0), ("OHP", ["Shoulders"], 2.5), 
               ("Curls", ["Biceps"], 1.25), ("Extensions", ["Triceps"], 2.5), ("Row", ["Back"], 5.0), ("Leg Press", ["Quads"], 10.0),
               ("Lateral Raise", ["Shoulders"], 1.25), ("Plank", ["Abs"], 0.0)]
        for n, m, i in exs:
            conn.execute("INSERT OR IGNORE INTO Exercises (id, name, muscle_ids_json, weight_increment) VALUES (?,?,?,?)", (str(uuid.uuid4()), n, json.dumps(m), i))
        rts = [("Push Day", ["Bench Press", "OHP"]), ("Pull Day", ["Deadlift", "Row"]), ("Legs", ["Squat", "Leg Press"]), ("Full Body", ["Squat", "Bench Press"]), ("Arms", ["Curls", "Extensions"])]
        for rn, re in rts:
            conn.execute("INSERT OR IGNORE INTO Routines (id, name, exercise_ids_json) VALUES (?,?,?)", (str(uuid.uuid4()), rn, json.dumps(re)))
        conn.commit(); st.success("Seeded.")
    if st.button("🧪 Generate 20 Samples"):
        exs = [r[0] for r in conn.execute("SELECT name FROM Exercises").fetchall()] or ["Squat"]
        for _ in range(20):
            s_data = json.dumps([[random.randint(45,225), random.randint(5,12), 2, 0.0] for _ in range(3)])
            conn.execute("INSERT INTO WorkoutLogs (id, timestamp, exercise, sets_json, is_sample) VALUES (?,?,?,?,?)", (str(uuid.uuid4()), datetime.now().isoformat(), random.choice(exs), s_data, 1))
        conn.commit(); st.success("20 samples added.")
    if st.button("🧹 Clear Samples ONLY"):
        conn.execute("DELETE FROM WorkoutLogs WHERE is_sample = 1"); conn.commit(); st.rerun()
    if st.button("⚠️ FULL WIPE", type="primary"):
        for t in ["Muscles", "Exercises", "Routines", "WorkoutLogs", "DraftState"]: conn.execute(f"DELETE FROM {t}")
        conn.commit(); st.rerun()

elif st.session_state.page == "Backup":
    st.title("💾 Data Vault")
    if st.button("Manual Export"):
        shutil.copy2(DB_NAME, os.path.join(BACKUP_DIR, f"manual_{datetime.now().strftime('%H%M%S')}.db"))