import subprocess
import os
from datetime import datetime
from pathlib import Path
from modules.db_connection import get_db_connection
import streamlit as st

# Config
dump_root = Path(st.secrets["backup"]["dump_dir"])
dump_dir = st.secrets["backup"]["dump_dir"]
mysqldump_path = Path(st.secrets["backup"]["mysqldump_path"])
config_path = Path(st.secrets["backup"]["config_path"])
if not mysqldump_path.exists():
    st.error(f"mysqldump not found at: {mysqldump_path}")
    st.stop()
mysql_path = Path(st.secrets["backup"]["mysql_path"])
if not mysql_path.exists():
    st.error(f"mysql.exe not found at: {mysql_path}")
    st.stop()
os.makedirs(dump_dir, exist_ok=True)
mysql = st.secrets["database"]

def get_all_user_tables():
    conn = get_db_connection()
    """Returns {db: [table1, table2, ...]} for non-system DBs"""
    with conn.cursor() as cur:
        cur.execute("SHOW DATABASES")
        dbs = [row[0] for row in cur.fetchall()]
        user_dbs = [db for db in dbs if db not in ('mysql', 'information_schema', 'performance_schema', 'sys')]
        
        db_tables = {}
        for db in user_dbs:
            cur.execute(f"SHOW TABLES FROM `{db}`")
            tables = [row[0] for row in cur.fetchall()]
            if tables:
                db_tables[db] = tables
        return db_tables

def create_dump_session():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    dump_dir = dump_root / f"Dump{timestamp}"
    dump_dir.mkdir(parents=True, exist_ok=True)
    return dump_dir

def dump_table(db_name, table_name, dump_dir, mysql_secrets):
    
    output_file = dump_dir / f"{db_name}_{table_name}.sql"
    cmd = [
    mysqldump_path,
    f"--defaults-file=C:/Users/daher/.my.cnf",  # ← first option!
    "--single-transaction",
    "--routines",      # safe for table dumps (ignored if no routines)
    "--triggers",
    db_name,           
    table_name        
]
    with open(output_file, 'w', encoding='utf-8') as f:
        subprocess.run(cmd, stdout=f, check=True)
    return output_file

def list_dump_sessions():
    sessions = []
    for item in dump_root.iterdir():
        if item.is_dir() and item.name.startswith("Dump"):
            sessions.append(item)
    return sorted(sessions, reverse=True)  # newest first

def restore_table(db_name, table_name, sql_file, mysql_secrets):
    # Ensure DB exists
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
            conn.commit()

    # Execute SQL file
    cmd = [
        mysql_path,
        f"--defaults-file=C:/Users/daher/.my.cnf",  # ← first option!
        db_name
    ]
    with open(sql_file, 'r', encoding='utf-8') as f:
        subprocess.run(cmd, stdin=f, check=True)

