from modules.migration_module import get_text_columns,generate_utf8mb4_migration
from modules.services import get_all_user_tables
from modules.db_connection import get_db_connection
import streamlit as st

import streamlit as st

st.title("🔤 UTF8MB4 Migration")

# Get DB list
db_list = []
try:
    db_tables = get_all_user_tables()
    db_list = list(db_tables.keys())
except Exception as e:
    st.error(f"⚠️ DB connection failed: {e}")
    st.stop()

# Initialize session state
if 'analyzed_db' not in st.session_state:
    st.session_state.analyzed_db = None
    st.session_state.text_columns = []

# 1. Select and analyze
db_to_migrate = st.selectbox("Select database to convert", db_list)

if st.button("🔍 Analyze Text Columns"):
    cols = get_text_columns(db_to_migrate)
    st.session_state.analyzed_db = db_to_migrate
    st.session_state.text_columns = cols
    st.rerun()  # Refresh to show results

# 2. Show results and migrate button (outside any button block!)
if st.session_state.analyzed_db:
    db = st.session_state.analyzed_db
    cols = st.session_state.text_columns
    
    st.write(f"✅ Found {len(cols)} text columns in `{db}`:")
    for table, col, _ in cols:
        st.code(f"{table}.{col}")
    
    st.warning("⚠️ Make sure you have a backup before migrating!")
    
    # 👇 This button is always rendered → click will register
    if st.button("🚀 Migrate to utf8mb4"):
        conn = None
        try:
            conn = get_db_connection()
            for table, col, col_type in cols:
                steps = generate_utf8mb4_migration(db, table, col, col_type)
                with conn.cursor() as cur:
                    for stmt in steps:
                        cur.execute(stmt)
                st.success(f"✅ Converted {table}.{col}")
            conn.commit()
            st.balloons()
            st.success("🎉 Migration complete!")
        except Exception as e:
            if conn:
                conn.rollback()
            st.error(f"❌ Migration failed: {e}")
        finally:
            if conn:
                conn.close()