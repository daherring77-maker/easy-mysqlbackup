from modules.services import create_dump_session, get_all_user_tables, dump_table
import streamlit as st
    
st.title("🔧 MySQL Backup Manager")

db_tables = {}
db_list = []

try:
    db_tables = get_all_user_tables()
    db_list = list(db_tables.keys())
except Exception as e:
    st.error(f"⚠️ Could not connect to MySQL or fetch tables: {e}")
    st.info("Check your secrets.toml and MySQL server status.")
    st.stop()

# ✅ ONE multiselect — outside the loop!
selected_dbs = st.multiselect(
    "Databases to back up",
    options=db_list,
    default=db_list  # or [] for none by default
)

# Only proceed if user clicked a button
if st.button("Start Backup"):
    if not selected_dbs:
        st.warning("Please select at least one database.")
    else:
        # Create a new dump session (timestamped folder)
        dump_dir = create_dump_session()
        st.info(f"Backing up to: `{dump_dir}`")

        # Loop only over selected databases
        for db in selected_dbs:
            tables = db_tables[db]
            st.write(f"Backing up **{db}** ({len(tables)} tables)...")
            for table in tables:
                try:
                    dump_table(db, table, dump_dir, st.secrets.database)
                    st.success(f"✅ {db}.{table}")
                except Exception as e:
                    st.error(f"❌ Failed {db}.{table}: {str(e)}")
        
        st.balloons()
        st.success("Backup completed!")