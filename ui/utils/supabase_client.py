"""
Supabase client for the Rice Growth Monitoring Dashboard.
Reads sensor data, images, and alerts from the Supabase database.
"""

import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_supabase() -> Client:
    """Create and cache a Supabase client using Streamlit secrets."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


@st.cache_data(ttl=30)
def fetch_recent_readings(limit=50):
    """Fetch the most recent readings, ordered newest first."""
    supabase = get_supabase()
    response = (
        supabase.table("readings")
        .select("*")
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data


@st.cache_data(ttl=60)
def fetch_readings_range(start_date, end_date):
    """Fetch readings within a date range, ordered oldest first (for charts)."""
    supabase = get_supabase()
    response = (
        supabase.table("readings")
        .select("*")
        .gte("timestamp", start_date.isoformat())
        .lte("timestamp", end_date.isoformat())
        .order("timestamp", desc=False)
        .execute()
    )
    return response.data


@st.cache_data(ttl=30)
def fetch_images(limit=20):
    """Fetch recent readings that have images attached."""
    supabase = get_supabase()
    response = (
        supabase.table("readings")
        .select("timestamp, image_url, prediction_label, prediction_confidence")
        .not_.is_("image_url", "null")
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data
