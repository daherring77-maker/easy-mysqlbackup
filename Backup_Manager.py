import streamlit as st

# ----------------------------
# Main App
# ----------------------------

pages = {
        "Database Administration": [
           st.Page("pages/backup.py", title="Backup Databases", icon="🔧"),
           st.Page("pages/restore.py", title="Restore Databases", icon="🔧"), 
                   
    ]
}
pg = st.navigation(pages)
pg.run()