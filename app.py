import streamlit as st
import sqlite3
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import base64
import os
import plotly.express as px
import plotly.graph_objects as go
from user_agents import parse
import time
import tempfile
import re
import json
import random
import string
import hashlib
import urllib.parse
import pytz
from tzlocal import get_localzone
import socket

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="URL Shortener & Analytics Platform", 
    page_icon="🔗", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Generic branding - No specific product name
APP_NAME = "URL Shortener"
APP_DOMAIN = "yourbrand.com"  # Change this to your actual domain
APP_URL = "https://smartlink-tracker.streamlit.app"  # Your actual Streamlit URL

# ============================================================================
# ENHANCED UI - Professional Design with Better Contrast
# ============================================================================
st.markdown("""
<style>
    /* ===== Modern Color Palette ===== */
    :root {
        --primary: #2563eb;
        --primary-light: #3b82f6;
        --primary-dark: #1d4ed8;
        --secondary: #7c3aed;
        --secondary-light: #8b5cf6;
        --success: #059669;
        --warning: #d97706;
        --danger: #dc2626;
        --info: #2563eb;
        
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-300: #d1d5db;
        --gray-400: #9ca3af;
        --gray-500: #6b7280;
        --gray-600: #4b5563;
        --gray-700: #374151;
        --gray-800: #1f2937;
        --gray-900: #111827;
        
        --bg-gradient: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        --card-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.02);
        --hover-shadow: 0 20px 30px -10px rgba(37, 99, 235, 0.2);
    }

    /* ===== Global Typography ===== */
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--gray-800) !important;
        font-weight: 600 !important;
        letter-spacing: -0.025em !important;
    }

    p, li, span {
        color: var(--gray-600) !important;
        line-height: 1.6 !important;
    }

    /* ===== Professional Header ===== */
    .professional-header {
        background: var(--bg-gradient);
        padding: 2.5rem 2rem;
        border-radius: 1.5rem;
        margin-bottom: 2rem;
        color: white;
        box-shadow: var(--card-shadow);
        position: relative;
        overflow: hidden;
    }

    .professional-header::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        background: radial-gradient(circle at top right, rgba(255,255,255,0.2) 0%, transparent 60%);
        pointer-events: none;
    }

    .professional-header h1 {
        color: white !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .professional-header p {
        color: rgba(255, 255, 255, 0.95) !important;
        font-size: 1.1rem !important;
        margin: 0.5rem 0 0 0 !important;
        font-weight: 400 !important;
    }

    /* ===== Domain Badge ===== */
    .domain-badge {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        padding: 0.75rem 1.5rem;
        border-radius: 100px;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white !important;
        font-size: 1rem;
        font-weight: 500;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .domain-badge strong {
        color: white !important;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        margin-left: 0.25rem;
    }

    /* ===== Cards ===== */
    .professional-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border: 1px solid var(--gray-200);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .professional-card:hover {
        box-shadow: var(--hover-shadow);
        transform: translateY(-2px);
        border-color: var(--primary-light);
    }

    .professional-card h4 {
        color: var(--gray-800) !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin: 0 0 1rem 0 !important;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--gray-100);
    }

    .professional-card p {
        color: var(--gray-600) !important;
        margin: 0.75rem 0 !important;
    }

    .professional-card strong {
        color: var(--gray-800) !important;
        font-weight: 600;
    }

    .professional-card a {
        color: var(--primary);
        text-decoration: none;
        font-weight: 500;
    }

    .professional-card a:hover {
        color: var(--primary-dark);
        text-decoration: underline;
    }

    /* ===== URL Display ===== */
    .url-container {
        background: var(--gray-50);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid var(--gray-200);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }

    .url-container:hover {
        border-color: var(--primary-light);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
    }

    .short-url {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 0.75rem;
    }

    .short-url a {
        background: white;
        color: var(--primary) !important;
        text-decoration: none;
        padding: 0.75rem 1.25rem;
        border-radius: 0.75rem;
        font-size: 1.2rem;
        font-weight: 600;
        border: 2px solid var(--primary-light);
        transition: all 0.3s ease;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }

    .short-url a:hover {
        background: var(--primary);
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(37, 99, 235, 0.3);
        border-color: var(--primary);
    }

    .short-url a::before {
        content: '🔗';
        font-size: 1.2rem;
    }

    .copy-btn {
        background: white;
        border: 2px solid var(--primary-light);
        color: var(--primary);
        padding: 0.75rem 1.5rem;
        border-radius: 0.75rem;
        cursor: pointer;
        font-size: 0.95rem;
        font-weight: 600;
        transition: all 0.3s ease;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }

    .copy-btn:hover {
        background: var(--primary);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(37, 99, 235, 0.3);
    }

    .original-url {
        color: var(--gray-500) !important;
        font-size: 0.9rem;
        word-break: break-all;
        padding: 0.75rem;
        background: white;
        border-radius: 0.5rem;
        border: 1px dashed var(--gray-300);
    }

    /* ===== Metric Cards ===== */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }

    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        text-align: center;
        border: 1px solid var(--gray-200);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--hover-shadow);
        border-color: var(--primary-light);
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--primary) !important;
        line-height: 1.2;
        margin-bottom: 0.25rem;
    }

    .metric-label {
        color: var(--gray-500) !important;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }

    /* ===== Click Cards (Live Feed) ===== */
    .click-card {
        background: white;
        padding: 1.25rem;
        border-radius: 0.75rem;
        margin: 0.75rem 0;
        border: 1px solid var(--gray-200);
        border-left: 4px solid var(--primary);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        transition: all 0.3s ease;
        animation: slideIn 0.3s ease-out;
    }

    .click-card:hover {
        box-shadow: var(--card-shadow);
        transform: translateX(4px);
        border-left-width: 6px;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-10px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    .click-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }

    .click-card-code {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--gray-800) !important;
    }

    .click-card-code a {
        color: var(--primary);
        text-decoration: none;
    }

    .click-card-time {
        color: var(--gray-400) !important;
        font-size: 0.85rem;
        font-weight: 500;
    }

    .click-card-details {
        display: flex;
        gap: 1.5rem;
        flex-wrap: wrap;
        color: var(--gray-600);
        font-size: 0.95rem;
    }

    .click-card-details span {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
    }

    /* ===== Success Box ===== */
    .success-box {
        background: #f0fdf4;
        padding: 2rem;
        border-radius: 1rem;
        border: 1px solid #bbf7d0;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(5, 150, 105, 0.1);
    }

    .success-box h3 {
        color: var(--success) !important;
        font-size: 1.5rem !important;
        margin: 0 0 1rem 0 !important;
    }

    .success-box strong {
        color: var(--gray-700) !important;
    }

    .success-box code {
        background: #dcfce7;
        color: var(--success) !important;
        padding: 0.25rem 0.5rem;
        border-radius: 0.375rem;
        font-weight: 500;
    }

    /* ===== Info Box ===== */
    .info-box {
        background: #eff6ff;
        padding: 1rem 1.5rem;
        border-radius: 0.75rem;
        border-left: 4px solid var(--primary);
        color: var(--gray-700) !important;
        margin: 1rem 0;
    }

    /* ===== Form Elements ===== */
    .stTextInput > div > div > input {
        border: 2px solid var(--gray-200) !important;
        border-radius: 0.75rem !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1) !important;
    }

    .stSelectbox > div > div > div {
        border: 2px solid var(--gray-200) !important;
        border-radius: 0.75rem !important;
    }

    /* ===== Buttons ===== */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border-radius: 0.75rem !important;
        transition: all 0.3s ease !important;
        text-transform: none !important;
        letter-spacing: normal !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 12px -2px rgba(37, 99, 235, 0.3) !important;
    }

    /* ===== Tabs ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--gray-50);
        padding: 0.5rem;
        border-radius: 1rem;
        border: 1px solid var(--gray-200);
        margin-bottom: 2rem;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: var(--gray-500) !important;
        border-radius: 0.75rem;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: white !important;
        color: var(--primary) !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    /* ===== Expander ===== */
    .streamlit-expanderHeader {
        background: var(--gray-50) !important;
        border: 1px solid var(--gray-200) !important;
        border-radius: 0.75rem !important;
        padding: 0.75rem 1rem !important;
        font-weight: 500 !important;
        color: var(--gray-700) !important;
    }

    .streamlit-expanderContent {
        border: 1px solid var(--gray-200) !important;
        border-top: none !important;
        border-radius: 0 0 0.75rem 0.75rem !important;
        padding: 1.5rem !important;
        background: white;
    }

    /* ===== DataFrames ===== */
    .stDataFrame {
        border: 1px solid var(--gray-200) !important;
        border-radius: 0.75rem !important;
        overflow: hidden !important;
    }

    .stDataFrame th {
        background: var(--gray-50) !important;
        color: var(--gray-700) !important;
        font-weight: 600 !important;
        padding: 0.75rem 1rem !important;
    }

    .stDataFrame td {
        color: var(--gray-600) !important;
        padding: 0.75rem 1rem !important;
    }

    /* ===== Alerts ===== */
    .stAlert {
        border-radius: 0.75rem !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
    }

    /* ===== Download Button ===== */
    .stDownloadButton > button {
        background: white !important;
        color: var(--primary) !important;
        border: 2px solid var(--primary) !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        border-radius: 0.75rem !important;
        transition: all 0.3s ease !important;
    }

    .stDownloadButton > button:hover {
        background: var(--primary) !important;
        color: white !important;
        transform: translateY(-2px) !important;
    }

    /* ===== Tooltips ===== */
    [data-testid="stTooltip"] {
        background: var(--gray-800) !important;
        color: white !important;
        border-radius: 0.5rem !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.85rem !important;
    }

    /* ===== Footer ===== */
    .footer {
        text-align: center;
        padding: 2rem;
        color: var(--gray-400);
        font-size: 0.85rem;
        border-top: 1px solid var(--gray-200);
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# PROFESSIONAL HEADER - Generic Version
# ============================================================================
st.markdown(f"""
<div class="professional-header">
    <h1>🔗 URL Shortener & Analytics</h1>
    <p>Shorten, track, and analyze every click with precision</p>
    <div class="domain-badge">
        <span>Your links:</span>
        <strong>{APP_DOMAIN}/<span style="font-weight:300;">[your-code]</span></strong>
    </div>
</div>
""", unsafe_allow_html=True)

# Add a subtle footer
st.markdown("""
<div class="footer">
    <span>© 2024 URL Shortener Platform · Professional Link Analytics · Secure · Reliable · Real-time</span>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# REST OF YOUR CODE CONTINUES HERE
# ============================================================================
# [Keep all your existing database functions, geolocation functions, 
#  time functions, and the rest of your app code here]

# Database setup
@st.cache_resource
def init_db():
    if os.getenv('STREAMLIT_SERVER_ADDRESS'):
        db_path = os.path.join(tempfile.gettempdir(), 'urls.db')
        os.makedirs(tempfile.gettempdir(), exist_ok=True)
    else:
        db_path = 'urls.db'
    
    conn = sqlite3.connect(db_path, timeout=30, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=30000")
    
    c = conn.cursor()
    
    # Links table
    c.execute('''CREATE TABLE IF NOT EXISTS links (
        id TEXT PRIMARY KEY,
        original_url TEXT NOT NULL,
        short_code TEXT UNIQUE NOT NULL,
        title TEXT,
        clicks INTEGER DEFAULT 0,
        created_date TEXT,
        expires_at TEXT,
        utm_source TEXT,
        utm_medium TEXT,
        utm_campaign TEXT,
        user_id TEXT
    )''')
    
    # Clicks table with comprehensive tracking
    c.execute('''CREATE TABLE IF NOT EXISTS clicks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link_id TEXT,
        short_code TEXT,
        timestamp TEXT,
        ip_address TEXT,
        country TEXT,
        city TEXT,
        region TEXT,
        latitude REAL,
        longitude REAL,
        isp TEXT,
        device_type TEXT,
        browser TEXT,
        browser_version TEXT,
        os TEXT,
        os_version TEXT,
        referrer TEXT,
        user_agent TEXT,
        session_id TEXT,
        is_unique BOOLEAN DEFAULT 1,
        FOREIGN KEY (link_id) REFERENCES links (id)
    )''')
    
    conn.commit()
    return conn

# Initialize database
try:
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT 1")
except Exception as e:
    st.error(f"Database initialization error: {str(e)}")
    st.stop()


def get_real_client_ip():
    """
    Get the real client IP address from various headers
    This is crucial for accurate geolocation
    """
    # List of headers to check in order of preference
    headers_to_check = [
        'X-Forwarded-For',
        'X-Real-IP',
        'CF-Connecting-IP',  # Cloudflare
        'True-Client-IP',
        'HTTP_X_FORWARDED_FOR',
        'HTTP_X_REAL_IP',
        'HTTP_CF_CONNECTING_IP',
        'REMOTE_ADDR'
    ]
    
    # Check each header in st.query_params
    for header in headers_to_check:
        if header in st.query_params:
            ip_value = st.query_params[header]
            # X-Forwarded-For can contain multiple IPs, take the first one
            if ',' in ip_value:
                ip_value = ip_value.split(',')[0].strip()
            # Validate it looks like an IP
            if ip_value and ip_value != '127.0.0.1' and ip_value != '::1':
                print(f"Found real IP from {header}: {ip_value}")
                return ip_value
    
    # If no headers found, try to get from request context
    try:
        # On Streamlit Cloud, try to get from environment
        host = os.environ.get('REMOTE_ADDR', '')
        if host and host != '127.0.0.1':
            return host
    except:
        pass
    
    # Last resort - make a request to a service that echoes the IP
    try:
        response = requests.get('https://api.ipify.org', timeout=3)
        if response.status_code == 200:
            external_ip = response.text.strip()
            print(f"Got external IP from ipify: {external_ip}")
            return external_ip
    except:
        pass
    
    # If all else fails, return a default (this will be overwritten by geolocation fallback)
    print("Could not determine real IP, using default")
    return None

def get_accurate_geo_info():
    """
    Get accurate geolocation data for the real client IP
    Uses multiple APIs with fallbacks
    """
    
    # First, get the real client IP
    client_ip = get_real_client_ip()
    
    geo_data = {
        'country': 'Unknown',
        'city': 'Unknown',
        'region': 'Unknown',
        'latitude': 0.0,
        'longitude': 0.0,
        'isp': 'Unknown',
        'ip': client_ip if client_ip else 'Unknown'
    }
    
    if not client_ip:
        print("No client IP available for geolocation")
        return geo_data
    
    print(f"Attempting geolocation for IP: {client_ip}")
    
    # PRIMARY API: ip-api.com (fast, free, no API key needed)
    # This is very accurate and includes city-level data
    try:
        response = requests.get(
            f'http://ip-api.com/json/{client_ip}?fields=status,country,city,regionName,lat,lon,isp,query',
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                geo_data.update({
                    'country': data.get('country', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'latitude': data.get('lat', 0.0),
                    'longitude': data.get('lon', 0.0),
                    'isp': data.get('isp', 'Unknown'),
                    'ip': data.get('query', client_ip)
                })
                print(f"ip-api.com success: {geo_data['country']}, {geo_data['city']}")
                return geo_data
    except Exception as e:
        print(f"ip-api.com failed: {e}")
    
    # SECONDARY API: ipapi.co (free tier, requires no API key for basic usage)
    try:
        response = requests.get(f'https://ipapi.co/{client_ip}/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('error') is None:
                geo_data.update({
                    'country': data.get('country_name', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'latitude': data.get('latitude', 0.0),
                    'longitude': data.get('longitude', 0.0),
                    'isp': data.get('org', 'Unknown'),
                    'ip': client_ip
                })
                print(f"ipapi.co success: {geo_data['country']}, {geo_data['city']}")
                return geo_data
    except Exception as e:
        print(f"ipapi.co failed: {e}")
    
    # TERTIARY API: ipinfo.io (free tier with token, but we'll try without)
    try:
        response = requests.get(f'https://ipinfo.io/{client_ip}/json', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('country'):
                geo_data.update({
                    'country': data.get('country', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'latitude': float(data.get('loc', '0,0').split(',')[0]) if data.get('loc') else 0.0,
                    'longitude': float(data.get('loc', '0,0').split(',')[1]) if data.get('loc') else 0.0,
                    'isp': data.get('org', 'Unknown'),
                    'ip': client_ip
                })
                print(f"ipinfo.io success: {geo_data['country']}, {geo_data['city']}")
                return geo_data
    except Exception as e:
        print(f"ipinfo.io failed: {e}")
    
    print(f"All geolocation APIs failed for IP: {client_ip}")
    return geo_data

# ============================================================================
# FIXED: Accurate Time Functions
# ============================================================================

def get_local_time():
    """
    Get current time in local timezone with proper timezone handling
    """
    try:
        # Get local timezone
        local_tz = get_localzone()
        # Get current time in local timezone
        local_time = datetime.now(local_tz)
        # Return ISO format with timezone info
        return local_time.isoformat()
    except Exception as e:
        print(f"Local timezone detection failed: {e}")
        # Fallback to UTC
        return datetime.now(timezone.utc).isoformat()

def format_timestamp(iso_timestamp):
    """
    Convert ISO timestamp to local time for display with proper formatting
    """
    try:
        if not iso_timestamp:
            return "Unknown"
        
        # Handle Z suffix (UTC)
        if iso_timestamp.endswith('Z'):
            iso_timestamp = iso_timestamp.replace('Z', '+00:00')
        
        # Parse the timestamp
        dt = datetime.fromisoformat(iso_timestamp)
        
        # Convert to local timezone
        try:
            local_tz = get_localzone()
            # If timestamp has no timezone, assume UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            # Convert to local timezone
            local_dt = dt.astimezone(local_tz)
            # Format with timezone abbreviation
            return local_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
        except Exception as e:
            print(f"Timezone conversion failed: {e}")
            # Fallback to simple formatting
            return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"Timestamp parsing failed: {e}")
        return iso_timestamp

# Parse user agent accurately
def parse_user_agent_accurate(user_agent_string):
    try:
        ua = parse(user_agent_string)
        return {
            'device_type': 'Mobile' if ua.is_mobile else 'Tablet' if ua.is_tablet else 'Desktop',
            'browser': ua.browser.family if ua.browser.family else 'Unknown',
            'browser_version': ua.browser.version_string if ua.browser.version_string else 'Unknown',
            'os': ua.os.family if ua.os.family else 'Unknown',
            'os_version': ua.os.version_string if ua.os.version_string else 'Unknown'
        }
    except:
        return {
            'device_type': 'Unknown',
            'browser': 'Unknown',
            'browser_version': 'Unknown',
            'os': 'Unknown',
            'os_version': 'Unknown'
        }

# Professional header
st.markdown(f"""
<div class="professional-header">
    <h1 style="font-size: 3rem; margin: 0;">📊 {APP_NAME}</h1>
    <p style="font-size: 1.25rem; margin: 0.5rem 0; opacity: 0.95;">Enterprise-Grade URL Shortening & Click Analytics</p>
    <div class="domain-badge">
        🔗 Your links: <strong>{APP_DOMAIN}/[code]</strong>
    </div>
</div>
""", unsafe_allow_html=True)

# Function to generate short code
def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Function to validate URL
def validate_url(url):
    if not url:
        return url
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

# Tabs
tab1, tab2, tab3 = st.tabs(["🔗 Create Short Link", "📊 Analytics", "🔄 Live Feed"])

# TAB 1: Create Short Link
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Create New Short Link")
        
        with st.form("create_link"):
            # Main URL input
            url = st.text_input(
                "Enter your long URL",
                placeholder="https://example.com/very/long/path?with=parameters",
                help="Paste the URL you want to shorten"
            )
            
            # Advanced options
            with st.expander("Advanced Options", expanded=False):
                col_a, col_b = st.columns(2)
                with col_a:
                    custom_code = st.text_input(
                        "Custom short code (optional)",
                        placeholder="my-campaign",
                        help="Choose a memorable short code"
                    )
                with col_b:
                    expires_in = st.selectbox(
                        "Link expiration",
                        ["Never", "7 days", "30 days", "90 days"],
                        index=0
                    )
                
                st.markdown("##### UTM Campaign Parameters")
                col_c, col_d, col_e = st.columns(3)
                with col_c:
                    utm_source = st.text_input("Source", placeholder="facebook")
                with col_d:
                    utm_medium = st.text_input("Medium", placeholder="social")
                with col_e:
                    utm_campaign = st.text_input("Campaign", placeholder="summer2024")
            
            submit = st.form_submit_button("Generate Short Link", use_container_width=True)
            
            if submit and url:
                # Validate and clean URL
                url = validate_url(url)
                
                # Add UTM parameters
                if utm_source or utm_medium or utm_campaign:
                    separator = '&' if '?' in url else '?'
                    utm_parts = []
                    if utm_source:
                        utm_parts.append(f"utm_source={utm_source}")
                    if utm_medium:
                        utm_parts.append(f"utm_medium={utm_medium}")
                    if utm_campaign:
                        utm_parts.append(f"utm_campaign={utm_campaign}")
                    if utm_parts:
                        url = f"{url}{separator}{'&'.join(utm_parts)}"
                
                # Generate or use custom code
                if custom_code:
                    short_code = re.sub(r'[^a-zA-Z0-9-]', '', custom_code).lower()
                else:
                    short_code = generate_short_code()
                    # Ensure uniqueness
                    max_attempts = 5
                    attempts = 0
                    while attempts < max_attempts:
                        c.execute("SELECT id FROM links WHERE short_code=?", (short_code,))
                        if not c.fetchone():
                            break
                        short_code = generate_short_code()
                        attempts += 1
                
                # Calculate expiration
                expires_at = None
                if expires_in != "Never":
                    days = int(expires_in.split()[0])
                    expires_at = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
                
                # Get local time for creation
                local_created_time = get_local_time()
                
                # Insert into database
                try:
                    link_id = hashlib.md5(f"{short_code}{datetime.now()}".encode()).hexdigest()[:12]
                    c.execute("""
                        INSERT INTO links (id, original_url, short_code, created_date, expires_at, 
                                         utm_source, utm_medium, utm_campaign, clicks)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                    """, (link_id, url, short_code, local_created_time, expires_at,
                          utm_source, utm_medium, utm_campaign))
                    conn.commit()
                    
                    short_url = f"{APP_URL}/?go={short_code}"
                    
                    # Format the creation time for display
                    display_time = format_timestamp(local_created_time)
                    
                    # Success message with clickable link
                    st.markdown(f"""
                    <div class="success-box">
                        <h3 style="margin:0 0 1rem 0;">✅ Link Created Successfully!</h3>
                        <div class="url-container">
                            <div class="short-url">
                                <a href="{short_url}" target="_blank">🔗 {short_url}</a>
                                <span class="copy-btn" onclick="navigator.clipboard.writeText('{short_url}')">Copy</span>
                            </div>
                            <div class="original-url">📎 Original: {url[:100]}{'...' if len(url) > 100 else ''}</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
                            <div>
                                <strong>Short Code:</strong> <code>{short_code}</code><br>
                                <strong>Created:</strong> {display_time}<br>
                                <strong>Expires:</strong> {expires_in if expires_in != 'Never' else 'Never'}
                            </div>
                            <div style="text-align: right;">
                                <strong>Total Clicks:</strong> 0<br>
                                <strong>Status:</strong> <span style="color: #059669;">Active</span>
                            </div>
                        </div>
                        <div style="margin-top: 1rem; text-align: center;">
                            <p style="color: #065f46;">✨ Click the link above to test it or copy it to share!</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add JavaScript for copy functionality
                    st.markdown("""
                    <script>
                    function copyToClipboard(text) {
                        navigator.clipboard.writeText(text).then(function() {
                            alert('Link copied to clipboard!');
                        }, function(err) {
                            console.error('Could not copy text: ', err);
                        });
                    }
                    </script>
                    """, unsafe_allow_html=True)
                    
                    st.balloons()
                    
                except sqlite3.IntegrityError:
                    st.error("This short code is already taken. Please try another one.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    
    with col2:
        st.markdown("### Quick Stats")
        
        # Get stats
        c.execute("SELECT COUNT(*) FROM links")
        total_links = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM clicks")
        total_clicks = c.fetchone()[0]
        
        c.execute("SELECT COUNT(DISTINCT short_code) FROM clicks")
        active_links = c.fetchone()[0]
        
        st.markdown(f"""
        <div class="stats-grid">
            <div class="metric-card">
                <div class="metric-value">{total_links}</div>
                <div class="metric-label">Total Links</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{total_clicks}</div>
                <div class="metric-label">Total Clicks</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{active_links}</div>
                <div class="metric-label">Active Links</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{((total_clicks/total_links)*100 if total_links > 0 else 0):.1f}%</div>
                <div class="metric-label">CTR</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# TAB 2: Analytics Dashboard
with tab2:
    st.markdown("### Analytics Dashboard")
    
    # Get all links
    c.execute("SELECT short_code, original_url, created_date, clicks FROM links ORDER BY created_date DESC")
    all_links = c.fetchall()
    
    if all_links:
        # Link selector
        link_options = {f"{link[0]} ({link[3]} clicks)": link[0] for link in all_links}
        selected = st.selectbox("Select a short link to analyze", options=list(link_options.keys()))
        short_code = link_options[selected]
        
        # Get link details
        c.execute("SELECT * FROM links WHERE short_code=?", (short_code,))
        link = c.fetchone()
        
        if link:
            # Format creation time for display
            created_display = format_timestamp(link[4]) if link[4] else "Unknown"
            
            # Link info card
            st.markdown(f"""
            <div class="professional-card">
                <h4 style="margin:0 0 1rem 0;">Link Information</h4>
                <p><strong>Short Code:</strong> {short_code}</p>
                <p><strong>Short URL:</strong> <a href="{APP_URL}/?go={short_code}" target="_blank">{APP_URL}/?go={short_code}</a></p>
                <p><strong>Original URL:</strong> <a href="{link[1]}" target="_blank">{link[1][:100]}</a></p>
                <p><strong>Created:</strong> {created_display}</p>
                <p><strong>Total Clicks:</strong> {link[3]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Time range filter
            time_range = st.radio(
                "Time Range",
                ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"],
                horizontal=True
            )
            
            # Calculate date filter
            now = datetime.now(timezone.utc)
            if time_range == "Last 24 Hours":
                start_date = (now - timedelta(days=1)).isoformat()
            elif time_range == "Last 7 Days":
                start_date = (now - timedelta(days=7)).isoformat()
            elif time_range == "Last 30 Days":
                start_date = (now - timedelta(days=30)).isoformat()
            else:
                start_date = None
            
            # Get clicks for this link
            if start_date:
                c.execute("""
                    SELECT * FROM clicks 
                    WHERE short_code=? AND timestamp >= ? 
                    ORDER BY timestamp DESC
                """, (short_code, start_date))
            else:
                c.execute("SELECT * FROM clicks WHERE short_code=? ORDER BY timestamp DESC", (short_code,))
            
            clicks_data = c.fetchall()
            
            if clicks_data:
                # Convert to DataFrame
                df = pd.DataFrame(clicks_data, columns=[
                    'id', 'link_id', 'short_code', 'timestamp', 'ip_address', 'country', 
                    'city', 'region', 'latitude', 'longitude', 'isp', 'device_type', 
                    'browser', 'browser_version', 'os', 'os_version', 'referrer', 
                    'user_agent', 'session_id', 'is_unique'
                ])
                
                # Format timestamps for display
                df['display_time'] = df['timestamp'].apply(format_timestamp)
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{len(df)}</div>
                        <div class="metric-label">Clicks</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    unique_countries = df['country'].nunique()
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{unique_countries}</div>
                        <div class="metric-label">Countries</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    unique_visitors = df['session_id'].nunique()
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{unique_visitors}</div>
                        <div class="metric-label">Unique Visitors</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    mobile_pct = (df['device_type'] == 'Mobile').mean() * 100
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{mobile_pct:.1f}%</div>
                        <div class="metric-label">Mobile</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### Clicks Over Time")
                    df['date'] = pd.to_datetime(df['timestamp']).dt.date
                    timeline = df.groupby('date').size().reset_index(name='count')
                    fig = px.line(timeline, x='date', y='count', markers=True)
                    fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("##### Top Countries")
                    countries = df['country'].value_counts().head(10)
                    fig = px.bar(x=countries.values, y=countries.index, orientation='h')
                    fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                
                # Device breakdown
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### Device Types")
                    devices = df['device_type'].value_counts()
                    fig = px.pie(values=devices.values, names=devices.index, hole=0.4)
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("##### Browsers")
                    browsers = df['browser'].value_counts().head(5)
                    fig = px.bar(x=browsers.values, y=browsers.index, orientation='h')
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Map if coordinates available
                if 'latitude' in df.columns and 'longitude' in df.columns:
                    map_df = df[df['latitude'].notna() & (df['latitude'] != 0)]
                    if not map_df.empty:
                        st.markdown("##### Click Locations Map")
                        st.map(map_df[['latitude', 'longitude']])
                
                # Detailed data with formatted timestamps
                st.markdown("##### Recent Clicks")
                display_df = df[['display_time', 'country', 'city', 'device_type', 'browser', 'os']].head(50)
                display_df = display_df.rename(columns={'display_time': 'Time'})
                st.dataframe(display_df, use_container_width=True)
                
                # Export
                export_df = df.copy()
                export_df['local_time'] = export_df['timestamp'].apply(format_timestamp)
                csv = export_df.to_csv(index=False)
                st.download_button(
                    "📥 Export Data to CSV",
                    csv,
                    f"{short_code}_analytics.csv",
                    "text/csv"
                )
                
            else:
                st.info("No clicks recorded for this link yet.")
    else:
        st.info("Create your first short link to see analytics!")

# TAB 3: Live Feed
with tab3:
    st.markdown("### Live Click Feed")
    st.markdown("*Real-time clicks across all your links*")
    
    # Get recent clicks
    c.execute("""
        SELECT c.timestamp, c.short_code, c.country, c.city, c.device_type, c.browser, c.os
        FROM clicks c
        ORDER BY c.timestamp DESC LIMIT 50
    """)
    recent = c.fetchall()
    
    if recent:
        for click in recent:
            timestamp, code, country, city, device, browser, os = click
            
            # Format time for display
            display_time = format_timestamp(timestamp)
            
            # Calculate time ago
            try:
                click_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                now = datetime.now()
                time_diff = now - click_time
                
                if time_diff.total_seconds() < 60:
                    time_str = f"{int(time_diff.total_seconds())} seconds ago"
                elif time_diff.total_seconds() < 3600:
                    time_str = f"{int(time_diff.total_seconds()/60)} minutes ago"
                elif time_diff.total_seconds() < 86400:
                    time_str = f"{int(time_diff.total_seconds()/3600)} hours ago"
                else:
                    time_str = f"{int(time_diff.total_seconds()/86400)} days ago"
            except:
                time_str = display_time
            
            st.markdown(f"""
            <div class="click-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span><strong>🔗 <a href="{APP_URL}/?go={code}" target="_blank" style="color: #2563eb;">{code}</a></strong></span>
                    <span style="color: #64748b; font-size: 0.875rem;">{time_str}</span>
                </div>
                <div style="display: flex; gap: 1.5rem; margin-top: 0.5rem; flex-wrap: wrap;">
                    <span>🌍 {country}{f' ({city})' if city else ''}</span>
                    <span>📱 {device}</span>
                    <span>🌐 {browser}</span>
                    <span>💻 {os}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.caption("🔄 Live updates on page refresh")
    else:
        st.info("No clicks recorded yet. Share your links to start tracking!")

# ============================================================================
# REDIRECT HANDLER - This runs when someone clicks a short link
# ============================================================================
# Check for short code in query parameters
short_code = None

# Check for 'go' parameter (our new format)
if 'go' in st.query_params:
    short_code = st.query_params['go']
    print(f"Redirect: Found go parameter: {short_code}")

# Check for 'id' parameter (old format for backward compatibility)
elif 'id' in st.query_params:
    short_code = st.query_params['id']
    print(f"Redirect: Found id parameter: {short_code}")

# If we have a short code, process the redirect
if short_code:
    print(f"Processing redirect for code: {short_code}")
    
    try:
        # Get the original URL from database
        c.execute("SELECT original_url, clicks FROM links WHERE short_code=?", (short_code,))
        result = c.fetchone()
        
        if result:
            original_url = result[0]
            print(f"Found URL: {original_url}")
            
            # ================================================================
            # FIXED: Get accurate geolocation using real client IP
            # ================================================================
            geo_data = get_accurate_geo_info()
            print(f"Final geo data: {geo_data}")
            
            # Parse user agent
            user_agent_string = st.query_params.get('user_agent', 'Unknown')
            ua_info = parse_user_agent_accurate(user_agent_string)
            print(f"UA info: {ua_info}")
            
            # Get local time for click timestamp
            click_time = get_local_time()
            
            # Generate session ID for unique visitor tracking
            session_id = hashlib.md5(
                f"{geo_data['ip']}{short_code}{datetime.now().strftime('%Y-%m-%d')}".encode()
            ).hexdigest()
            
            # Check if this is a unique click today
            c.execute("""
                SELECT id FROM clicks 
                WHERE short_code=? AND session_id=? AND DATE(timestamp)=DATE('now')
            """, (short_code, session_id))
            
            is_unique = 0 if c.fetchone() else 1
            print(f"Is unique: {is_unique}")
            
            # Get referrer
            referrer = st.query_params.get('referrer', 'Direct')
            
            # Get link_id
            c.execute("SELECT id FROM links WHERE short_code=?", (short_code,))
            link_id_result = c.fetchone()
            link_id = link_id_result[0] if link_id_result else hashlib.md5(short_code.encode()).hexdigest()[:12]
            
            # Record the click
            try:
                c.execute("""
                    INSERT INTO clicks (
                        link_id, short_code, timestamp, ip_address, country, city, region,
                        latitude, longitude, isp, device_type, browser, browser_version,
                        os, os_version, referrer, user_agent, session_id, is_unique
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    link_id,
                    short_code,
                    click_time,  # Use local time
                    geo_data['ip'],
                    geo_data['country'],
                    geo_data['city'],
                    geo_data['region'],
                    geo_data['latitude'],
                    geo_data['longitude'],
                    geo_data['isp'],
                    ua_info['device_type'],
                    ua_info['browser'],
                    ua_info['browser_version'],
                    ua_info['os'],
                    ua_info['os_version'],
                    referrer,
                    user_agent_string,
                    session_id,
                    1 if is_unique else 0
                ))
                
                # Update click count in links table
                c.execute("UPDATE links SET clicks = clicks + 1 WHERE short_code=?", (short_code,))
                conn.commit()
                print(f"Click recorded successfully for {short_code}")
                print(f"Location: {geo_data['country']}, {geo_data['city']}")
                
            except Exception as e:
                print(f"Error recording click: {e}")
                conn.rollback()
            
            # Create HTML redirect page with tracking info
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Redirecting to {original_url[:50]}...</title>
                <meta http-equiv="refresh" content="2;url={original_url}">
                <style>
                    body {{
                        margin: 0;
                        padding: 0;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
                        color: white;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }}
                    .container {{
                        text-align: center;
                        padding: 2rem;
                        max-width: 600px;
                    }}
                    .card {{
                        background: rgba(255, 255, 255, 0.1);
                        backdrop-filter: blur(10px);
                        padding: 2rem;
                        border-radius: 1rem;
                        margin: 2rem 0;
                        border: 1px solid rgba(255,255,255,0.2);
                    }}
                    .grid {{
                        display: grid;
                        grid-template-columns: repeat(2, 1fr);
                        gap: 1rem;
                        margin: 1.5rem 0;
                    }}
                    .item {{
                        background: rgba(255, 255, 255, 0.05);
                        padding: 1rem;
                        border-radius: 0.5rem;
                    }}
                    .loader {{
                        width: 50px;
                        height: 50px;
                        border: 5px solid rgba(255,255,255,0.3);
                        border-top: 5px solid white;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                        margin: 2rem auto;
                    }}
                    @keyframes spin {{
                        0% {{ transform: rotate(0deg); }}
                        100% {{ transform: rotate(360deg); }}
                    }}
                    h1 {{ font-size: 3rem; margin: 0; }}
                    .url {{ 
                        color: #a5f3fc; 
                        word-break: break-all;
                        font-size: 0.9rem;
                        margin-top: 0.5rem;
                    }}
                    a {{ color: white; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📊</h1>
                    <h2>LinkMetrics Pro</h2>
                    <div class="card">
                        <h3 style="margin-top:0;">📍 Your Location</h3>
                        <div class="grid">
                            <div class="item">
                                <div>🌍 Country</div>
                                <strong>{geo_data['country']}</strong>
                            </div>
                            <div class="item">
                                <div>🏙️ City</div>
                                <strong>{geo_data['city']}</strong>
                            </div>
                            <div class="item">
                                <div>📱 Device</div>
                                <strong>{ua_info['device_type']}</strong>
                            </div>
                            <div class="item">
                                <div>🌐 Browser</div>
                                <strong>{ua_info['browser']}</strong>
                            </div>
                        </div>
                        <p style="margin:0;"><small>ISP: {geo_data['isp']}</small></p>
                    </div>
                    <div class="loader"></div>
                    <p style="font-size: 1.2rem;">Tracking your click...</p>
                    <p>Redirecting to:</p>
                    <div class="url">{original_url[:100]}{'...' if len(original_url) > 100 else ''}</div>
                    <p><small>If you're not redirected in 2 seconds, <a href="{original_url}">click here</a></small></p>
                </div>
            </body>
            </html>
            """
            
            # Display the HTML
            st.markdown(html_content, unsafe_allow_html=True)
            
            # Stop further Streamlit execution
            st.stop()
            
        else:
            st.error(f"❌ Link not found. The short code '{short_code}' does not exist.")
            st.markdown(f"[Go to {APP_NAME}]({APP_URL})")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        if 'original_url' in locals() and original_url:
            st.markdown(f'<meta http-equiv="refresh" content="2;url={original_url}">', unsafe_allow_html=True)