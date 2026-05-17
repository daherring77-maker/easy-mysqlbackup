# In your main app or a dedicated restore page

import streamlit as st
from pathlib import Path
from datetime import datetime
from modules.services import restore_table

DUMP_ROOT = Path(r'D:\MySQL_backups')

# Initialize session state
if 'restore_selections' not in st.session_state:
    st.session_state.restore_selections = {}  # { (db, table): bool }

st.title("🔄 Restore Database Tables")

# 1. Select dump session
sessions = sorted(
    [p for p in DUMP_ROOT.iterdir() if p.is_dir() and p.name.startswith("Dump")],
    reverse=True
)

if not sessions:
    st.warning("No backup folders found.")
else:
    session_name = st.selectbox(
        "Select backup session",
        [s.name for s in sessions]
    )
    session_dir = DUMP_ROOT / session_name

    # 2. Age warning
    mtime = session_dir.stat().st_mtime
    age = datetime.now() - datetime.fromtimestamp(mtime)
    if age.days > 7:
        st.warning(f"⚠️ Backup is {age.days} days old")

    # 3. Parse tables
    sql_files = list(session_dir.glob("*.sql"))
    table_info = []  # list of (db, table, file_path)
    for f in sql_files:
        parts = f.stem.split('_', 1)
        if len(parts) == 2:
            db, table = parts
            table_info.append((db, table, f))

    if not table_info:
        st.error("No valid table files found.")
    else:
        # 4. Group by database and show checkboxes
        dbs = sorted(set(db for db, _, _ in table_info))
        for db in dbs:
            st.subheader(f"📁 {db}")
            db_tables = [(t, f) for d, t, f in table_info if d == db]
            
            for table, file_path in db_tables:
                key = f"{db}_{table}"
                # Use session_state to preserve selection
                current = st.session_state.restore_selections.get(key, False)
                selected = st.checkbox(f"{table}", value=current, key=f"cb_{key}")
                st.session_state.restore_selections[key] = selected

        # 5. Restore button
        if st.button("🚀 Restore Selected Tables"):
            success_count = 0
            for db, table, file_path in table_info:
                key = f"{db}_{table}"
                if st.session_state.restore_selections.get(key, False):
                    try:
                        restore_table(db, table, file_path, st.secrets.database)
                        st.success(f"✅ Restored {db}.{table}")
                        success_count += 1
                    except Exception as e:
                        st.error(f"❌ Failed {db}.{table}: {str(e)}")
            
            if success_count > 0:
                st.balloons()


