# db_connection.py
import streamlit as st
import mysql.connector  # or your database library
import time

# Global variables for caching
_cached_connection = None
_cached_connection_time = 0
CONNECTION_CACHE_TIMEOUT = 350  # seconds

def get_db_connection():
    """Get a database connection with caching."""
    global _cached_connection, _cached_connection_time
    
    current_time = time.time()
    
    # Check if we have a cached connection that's still valid
    if (_cached_connection is not None and 
        current_time - _cached_connection_time < CONNECTION_CACHE_TIMEOUT):
        try:
            # Test if connection is still alive (optional but recommended)
            _cached_connection.execute("SELECT 1")
            return _cached_connection
        except:
            # Connection is dead, fall through to create new one
            pass
    
    # Create new connection
    _cached_connection = create_new_connection()  # your existing connection logic
    _cached_connection_time = current_time
    return _cached_connection

def create_new_connection():
    """Your existing connection creation logic."""
    # Replace this with your actual connection code
    conn = mysql.connector.connect(**st.secrets["database"])
    return conn

def close_connection():
    """Explicitly close the cached connection."""
    global _cached_connection, _cached_connection_time
    if _cached_connection:
        _cached_connection.close()
    _cached_connection = None
    _cached_connection_time = 0