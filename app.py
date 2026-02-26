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

# ============================================================================
# CLEAN PROFESSIONAL THEME - Subtle & Elegant
# ============================================================================

st.markdown("""
<style>
    /* ===== CLEAN PROFESSIONAL COLOR PALETTE ===== */
    :root {
        --primary: #2c3e50;
        --primary-light: #34495e;
        --primary-dark: #1e2b37;
        --accent: #3498db;
        --accent-light: #5dade2;
        --success: #27ae60;
        --warning: #f39c12;
        --danger: #e74c3c;
        
        --bg-main: #ffffff;
        --bg-light: #f8f9fa;
        --bg-card: #ffffff;
        
        --text-dark: #2c3e50;
        --text-medium: #4a5568;
        --text-light: #718096;
        --text-muted: #a0aec0;
        --text-white: #ffffff;
        
        --border-light: #e2e8f0;
        --border-medium: #cbd5e0;
        
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1);
        
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
    }

    /* ===== GLOBAL STYLES ===== */
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }

    .stApp {
        background: var(--bg-light);
    }

    /* ===== TYPOGRAPHY ===== */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-dark) !important;
        font-weight: 500 !important;
        letter-spacing: -0.01em !important;
    }

    p, li, span, div {
        color: var(--text-medium) !important;
        line-height: 1.6 !important;
    }

    /* ===== HEADER ===== */
    .professional-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        padding: 2.5rem 2rem;
        border-radius: var(--radius-lg);
        margin-bottom: 2rem;
        color: var(--text-white);
        box-shadow: var(--shadow-md);
    }

    .professional-header h1 {
        color: var(--text-white) !important;
        font-size: 2.5rem !important;
        font-weight: 500 !important;
        margin: 0 !important;
    }

    .professional-header p {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 1.1rem !important;
        margin: 0.5rem 0 0 0 !important;
    }

    .domain-badge {
        background: rgba(255, 255, 255, 0.1);
        padding: 0.6rem 1.5rem;
        border-radius: 100px;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: var(--text-white) !important;
        font-size: 1rem;
    }

    .domain-badge strong {
        color: var(--text-white) !important;
        font-weight: 500;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        font-family: monospace;
    }

    /* ===== CARDS ===== */
    .professional-card {
        background: var(--bg-card);
        padding: 1.5rem;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
        margin: 1rem 0;
        border: 1px solid var(--border-light);
        transition: all 0.2s ease;
    }

    .professional-card:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--border-medium);
    }

    .professional-card h4 {
        color: var(--text-dark) !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin: 0 0 1rem 0 !important;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-light);
    }

    .professional-card p {
        color: var(--text-medium) !important;
        margin: 0.75rem 0 !important;
    }

    .professional-card strong {
        color: var(--text-dark) !important;
        font-weight: 600;
    }

    .professional-card a {
        color: var(--accent);
        text-decoration: none;
    }

    .professional-card a:hover {
        text-decoration: underline;
    }

    /* ===== URL DISPLAY ===== */
    .url-container {
        background: var(--bg-light);
        padding: 1.5rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--border-light);
        margin: 1rem 0;
    }

    .short-url {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 0.75rem;
    }

    .short-url a {
        background: var(--accent);
        color: white !important;
        text-decoration: none;
        padding: 0.6rem 1.2rem;
        border-radius: var(--radius-sm);
        font-size: 1.1rem;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        transition: background 0.2s ease;
    }

    .short-url a:hover {
        background: var(--primary);
    }

    .copy-btn {
        background: white;
        border: 1px solid var(--border-medium);
        color: var(--text-medium) !important;
        padding: 0.6rem 1.2rem;
        border-radius: var(--radius-sm);
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }

    .copy-btn:hover {
        background: var(--bg-light);
        border-color: var(--accent);
        color: var(--accent) !important;
    }

    .original-url {
        color: var(--text-light) !important;
        font-size: 0.9rem;
        word-break: break-all;
        padding: 0.75rem;
        background: white;
        border-radius: var(--radius-sm);
        border: 1px dashed var(--border-light);
        margin-top: 0.75rem;
    }

    /* ===== METRIC CARDS ===== */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }

    .metric-card {
        background: var(--bg-card);
        padding: 1.5rem;
        border-radius: var(--radius-md);
        text-align: center;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-sm);
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 500;
        color: var(--primary) !important;
        line-height: 1.2;
        margin-bottom: 0.25rem;
    }

    .metric-label {
        color: var(--text-light) !important;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    /* ===== CLICK CARDS ===== */
    .click-card {
        background: var(--bg-card);
        padding: 1.2rem;
        border-radius: var(--radius-sm);
        margin: 0.75rem 0;
        border: 1px solid var(--border-light);
        border-left: 3px solid var(--accent);
        transition: all 0.2s ease;
    }

    .click-card:hover {
        background: var(--bg-light);
    }

    .click-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }

    .click-card-code {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-dark) !important;
    }

    .click-card-code a {
        color: var(--accent);
        text-decoration: none;
    }

    .click-card-time {
        color: var(--text-light) !important;
        font-size: 0.8rem;
        background: var(--bg-light);
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
    }

    .click-card-details {
        display: flex;
        gap: 1.5rem;
        flex-wrap: wrap;
    }

    .click-card-details span {
        color: var(--text-medium) !important;
        font-size: 0.9rem;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
    }

    /* ===== SUCCESS BOX ===== */
    .success-box {
        background: #f0f9ff;
        padding: 2rem;
        border-radius: var(--radius-md);
        border: 1px solid #bae6fd;
        margin: 1.5rem 0;
    }

    .success-box h3 {
        color: #0369a1 !important;
        font-size: 1.5rem !important;
        margin: 0 0 1rem 0 !important;
        font-weight: 500 !important;
    }

    .success-box p {
        color: #0369a1 !important;
    }

    .success-box strong {
        color: #0369a1 !important;
    }

    .success-box code {
        background: #e0f2fe;
        color: #0369a1 !important;
        padding: 0.2rem 0.5rem;
        border-radius: var(--radius-sm);
    }

    /* ===== INFO BOX ===== */
    .info-box {
        background: var(--bg-light);
        padding: 1rem 1.5rem;
        border-radius: var(--radius-sm);
        border-left: 3px solid var(--accent);
        color: var(--text-medium) !important;
        margin: 1rem 0;
    }

    /* ===== FORM ELEMENTS ===== */
    .stTextInput > div > div > input {
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1) !important;
    }

    .stSelectbox > div > div > div {
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-sm) !important;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        background: var(--accent) !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        font-weight: 500 !important;
        border-radius: var(--radius-sm) !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }

    .stButton > button:hover {
        background: var(--primary) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: transparent;
        padding: 0;
        border-bottom: 1px solid var(--border-light);
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 0;
        font-weight: 500;
        color: var(--text-light) !important;
    }

    .stTabs [aria-selected="true"] {
        color: var(--accent) !important;
        border-bottom: 2px solid var(--accent) !important;
    }

    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: var(--bg-light) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.6rem 1rem !important;
        font-weight: 500 !important;
        color: var(--text-medium) !important;
    }

    .streamlit-expanderContent {
        border: 1px solid var(--border-light) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important;
        padding: 1.5rem !important;
        background: white;
    }

    /* ===== DATAFRAMES ===== */
    .stDataFrame {
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-sm) !important;
        overflow: hidden !important;
    }

    .stDataFrame th {
        background: var(--bg-light) !important;
        color: var(--text-dark) !important;
        font-weight: 500 !important;
        padding: 0.75rem !important;
        font-size: 0.9rem !important;
    }

    .stDataFrame td {
        color: var(--text-medium) !important;
        padding: 0.6rem 0.75rem !important;
        font-size: 0.9rem !important;
    }

    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton > button {
        background: white !important;
        color: var(--accent) !important;
        border: 1px solid var(--accent) !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 500 !important;
        border-radius: var(--radius-sm) !important;
        transition: all 0.2s ease !important;
    }

    .stDownloadButton > button:hover {
        background: var(--accent) !important;
        color: white !important;
    }

    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        padding: 2rem 2rem 1rem;
        color: var(--text-light) !important;
        font-size: 0.85rem;
        border-top: 1px solid var(--border-light);
        margin-top: 3rem;
    }

    .footer span {
        color: var(--text-light) !important;
    }

    /* ===== RADIO BUTTONS ===== */
    .stRadio > div {
        background: white;
        padding: 0.5rem;
        border-radius: var(--radius-sm);
        border: 1px solid var(--border-light);
    }

    .stRadio label {
        color: var(--text-medium) !important;
    }

    /* ===== METRICS ===== */
    [data-testid="stMetricValue"] {
        color: var(--text-dark) !important;
        font-weight: 500 !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-light) !important;
        font-size: 0.85rem !important;
    }

    /* ===== PLOTLY CHARTS ===== */
    .js-plotly-plot {
        border-radius: var(--radius-sm);
        background: white;
        padding: 0.75rem;
        border: 1px solid var(--border-light);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# PROFESSIONAL HEADER - Clean & Simple
# ============================================================================
APP_URL = "https://smartlink-tracker.streamlit.app"  # Your actual Streamlit URL

st.markdown(f"""
<div class="professional-header">
    <h1>🔗 URL Shortener & Analytics</h1>
    <p>Shorten, track, and analyze your links</p>
    <div class="domain-badge">
        <span>Your links:</span>
        <strong>yourbrand.com/<span style="font-weight:300;">[code]</span></strong>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# DATABASE SETUP WITH COMPREHENSIVE MIGRATION
# ============================================================================

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
    
    # Links table - with all columns
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
    
    # Clicks table - with all columns
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

# Initialize database with comprehensive migration
try:
    conn = init_db()
    c = conn.cursor()
    
    # ============================================================
    # COMPREHENSIVE DATABASE MIGRATION
    # ============================================================
    def migrate_database():
        """Add all missing columns to both tables"""
        try:
            # ===== MIGRATE CLICKS TABLE =====
            c.execute("PRAGMA table_info(clicks)")
            clicks_columns = [column[1] for column in c.fetchall()]
            
            # Columns to add to clicks table
            clicks_columns_to_add = {
                'short_code': 'TEXT',
                'region': 'TEXT',
                'latitude': 'REAL',
                'longitude': 'REAL',
                'isp': 'TEXT',
                'browser_version': 'TEXT',
                'os_version': 'TEXT',
                'session_id': 'TEXT',
                'is_unique': 'BOOLEAN DEFAULT 1'
            }
            
            for column_name, column_type in clicks_columns_to_add.items():
                if column_name not in clicks_columns:
                    try:
                        c.execute(f"ALTER TABLE clicks ADD COLUMN {column_name} {column_type}")
                        conn.commit()
                    except Exception as e:
                        pass
            
            # ===== MIGRATE LINKS TABLE =====
            c.execute("PRAGMA table_info(links)")
            links_columns = [column[1] for column in c.fetchall()]
            
            # Columns to add to links table
            links_columns_to_add = {
                'short_code': 'TEXT UNIQUE',
                'title': 'TEXT',
                'expires_at': 'TEXT',
                'utm_source': 'TEXT',
                'utm_medium': 'TEXT',
                'utm_campaign': 'TEXT',
                'user_id': 'TEXT'
            }
            
            for column_name, column_type in links_columns_to_add.items():
                if column_name not in links_columns:
                    try:
                        if column_name == 'short_code':
                            c.execute("ALTER TABLE links ADD COLUMN short_code TEXT")
                            conn.commit()
                            # Update short_code from id for existing records
                            c.execute("UPDATE links SET short_code = id WHERE short_code IS NULL")
                            conn.commit()
                        else:
                            c.execute(f"ALTER TABLE links ADD COLUMN {column_name} {column_type}")
                            conn.commit()
                    except Exception as e:
                        pass
            
            # ===== DATA SYNC =====
            # Sync short_code from links to clicks
            try:
                c.execute("""
                    UPDATE clicks 
                    SET short_code = (
                        SELECT short_code FROM links 
                        WHERE links.id = clicks.link_id
                    )
                    WHERE short_code IS NULL AND link_id IN (SELECT id FROM links)
                """)
                conn.commit()
            except Exception as e:
                pass
            
        except Exception as e:
            pass
    
    # Run migration
    migrate_database()
    
    # Test database
    c.execute("SELECT 1")
    
except Exception as e:
    st.error(f"Database initialization error: {str(e)}")
    st.stop()

# ============================================================================
# ACCURATE IP AND GEOLOCATION FUNCTIONS
# ============================================================================

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
                return ip_value
    
    # If no headers found, try to get from request context
    try:
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
            return external_ip
    except:
        pass
    
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
        return geo_data
    
    # PRIMARY API: ip-api.com (fast, free, no API key needed)
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
                return geo_data
    except Exception as e:
        pass
    
    # SECONDARY API: ipapi.co
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
                return geo_data
    except Exception as e:
        pass
    
    return geo_data

# ============================================================================
# ACCURATE TIME FUNCTIONS
# ============================================================================

def get_local_time():
    """
    Get current time in local timezone with proper timezone handling
    """
    try:
        local_tz = get_localzone()
        local_time = datetime.now(local_tz)
        return local_time.isoformat()
    except Exception as e:
        return datetime.now(timezone.utc).isoformat()

def format_timestamp(iso_timestamp):
    """
    Convert ISO timestamp to local time for display with proper formatting
    """
    try:
        if not iso_timestamp:
            return "Unknown"
        
        if iso_timestamp.endswith('Z'):
            iso_timestamp = iso_timestamp.replace('Z', '+00:00')
        
        dt = datetime.fromisoformat(iso_timestamp)
        
        try:
            local_tz = get_localzone()
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            local_dt = dt.astimezone(local_tz)
            return local_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
        except Exception as e:
            return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
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

# ============================================================================
# TABS
# ============================================================================
tab1, tab2, tab3 = st.tabs(["🔗 Create Short Link", "📊 Analytics Dashboard", "🔄 Live Click Feed"])

# ============================================================================
# TAB 1: Create Short Link
# ============================================================================
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### ✨ Create New Short Link")
        
        with st.form("create_link"):
            # Main URL input
            url = st.text_input(
                "Enter your long URL",
                placeholder="https://example.com/very/long/path?with=parameters",
                help="Paste the URL you want to shorten"
            )
            
            # Advanced options
            with st.expander("⚙️ Advanced Options", expanded=False):
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
                
                st.markdown("##### 📊 UTM Campaign Parameters")
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
                        <h3>Link Created Successfully!</h3>
                        <div class="url-container">
                            <div class="short-url">
                                <a href="{short_url}" target="_blank">{short_url}</a>
                                <button class="copy-btn" onclick="navigator.clipboard.writeText('{short_url}')">Copy Link</button>
                            </div>
                            <div class="original-url">{url}</div>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 2rem; margin-top: 2rem;">
                            <div>
                                <p><strong>Short Code:</strong> <code>{short_code}</code></p>
                                <p><strong>Created:</strong> {display_time}</p>
                                <p><strong>Expires:</strong> {expires_in if expires_in != 'Never' else 'Never'}</p>
                            </div>
                            <div style="text-align: right;">
                                <p><strong>Total Clicks:</strong> 0</p>
                                <p><strong>Status:</strong> <span style="color: #10b981;">Active</span></p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.balloons()
                    
                except sqlite3.IntegrityError:
                    st.error("This short code is already taken. Please try another one.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    
    with col2:
        st.markdown("### 📈 Quick Stats")
        
        # Get stats with safe queries
        try:
            c.execute("SELECT COUNT(*) FROM links")
            total_links = c.fetchone()[0]
        except:
            total_links = 0
        
        try:
            c.execute("SELECT COUNT(*) FROM clicks")
            total_clicks = c.fetchone()[0]
        except:
            total_clicks = 0
        
        try:
            c.execute("SELECT COUNT(DISTINCT short_code) FROM clicks")
            active_links = c.fetchone()[0]
        except:
            # Fallback if short_code doesn't exist
            try:
                c.execute("SELECT COUNT(DISTINCT link_id) FROM clicks")
                active_links = c.fetchone()[0]
            except:
                active_links = 0
        
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

# ============================================================================
# TAB 2: Analytics Dashboard
# ============================================================================
with tab2:
    st.markdown("### 📊 Analytics Dashboard")
    
    # Get all links with safe query
    try:
        c.execute("SELECT short_code, original_url, created_date, clicks FROM links ORDER BY created_date DESC")
        all_links = c.fetchall()
    except:
        # Fallback if short_code doesn't exist
        try:
            c.execute("SELECT id, original_url, created_date, clicks FROM links ORDER BY created_date DESC")
            all_links = [(row[0], row[1], row[2], row[3]) for row in c.fetchall()]
        except:
            all_links = []
    
    if all_links:
        # Link selector
        link_options = {}
        for link in all_links:
            display_name = f"🔗 {link[0]} ({link[3]} clicks)"
            link_options[display_name] = link[0]
        
        selected = st.selectbox("Select a short link to analyze", options=list(link_options.keys()))
        short_code = link_options[selected]
        
        # Get link details with safe query
        try:
            c.execute("SELECT * FROM links WHERE short_code=?", (short_code,))
            link = c.fetchone()
        except:
            # Fallback using id
            c.execute("SELECT * FROM links WHERE id=?", (short_code,))
            link = c.fetchone()
        
        if link:
            # Format creation time for display
            created_display = format_timestamp(link[5]) if len(link) > 5 and link[5] else "Unknown"
            
            # Link info card
            st.markdown(f"""
            <div class="professional-card">
                <h4>Link Information</h4>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                    <div>
                        <p><strong>Short Code:</strong> {short_code}</p>
                        <p><strong>Short URL:</strong> <a href="{APP_URL}/?go={short_code}" target="_blank">Open</a></p>
                    </div>
                    <div>
                        <p><strong>Created:</strong> {created_display}</p>
                        <p><strong>Total Clicks:</strong> {link[4] if len(link) > 4 else 0}</p>
                    </div>
                </div>
                <p><strong>Original URL:</strong> <a href="{link[1]}" target="_blank">{link[1][:100]}{'...' if len(link[1]) > 100 else ''}</a></p>
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
            
            # Get clicks for this link with safe query
            try:
                if start_date:
                    c.execute("""
                        SELECT * FROM clicks 
                        WHERE short_code=? AND timestamp >= ? 
                        ORDER BY timestamp DESC
                    """, (short_code, start_date))
                else:
                    c.execute("SELECT * FROM clicks WHERE short_code=? ORDER BY timestamp DESC", (short_code,))
            except:
                # Fallback using link_id
                try:
                    # Get link_id first
                    c.execute("SELECT id FROM links WHERE short_code=?", (short_code,))
                    link_id_result = c.fetchone()
                    if link_id_result:
                        link_id = link_id_result[0]
                        if start_date:
                            c.execute("""
                                SELECT * FROM clicks 
                                WHERE link_id=? AND timestamp >= ? 
                                ORDER BY timestamp DESC
                            """, (link_id, start_date))
                        else:
                            c.execute("SELECT * FROM clicks WHERE link_id=? ORDER BY timestamp DESC", (link_id,))
                    else:
                        clicks_data = []
                except:
                    clicks_data = []
            
            clicks_data = c.fetchall() if 'clicks_data' not in locals() else clicks_data
            
            if clicks_data:
                # Determine columns from the data
                num_columns = len(clicks_data[0]) if clicks_data else 0
                
                # Create DataFrame with appropriate columns
                if num_columns >= 15:
                    df = pd.DataFrame(clicks_data, columns=[
                        'id', 'link_id', 'short_code', 'timestamp', 'ip_address', 'country', 
                        'city', 'region', 'latitude', 'longitude', 'isp', 'device_type', 
                        'browser', 'browser_version', 'os', 'os_version', 'referrer', 
                        'user_agent', 'session_id', 'is_unique'
                    ][:num_columns])
                else:
                    # Fallback with fewer columns
                    df = pd.DataFrame(clicks_data, columns=[
                        'id', 'link_id', 'short_code', 'timestamp', 'ip_address', 'country', 
                        'city', 'device_type', 'browser', 'os'
                    ][:num_columns])
                
                # Format timestamps for display
                if 'timestamp' in df.columns:
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
                    if 'country' in df.columns:
                        unique_countries = df['country'].nunique()
                    else:
                        unique_countries = 0
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{unique_countries}</div>
                        <div class="metric-label">Countries</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    if 'session_id' in df.columns:
                        unique_visitors = df['session_id'].nunique()
                    else:
                        unique_visitors = len(df)
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{unique_visitors}</div>
                        <div class="metric-label">Unique Visitors</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    if 'device_type' in df.columns:
                        mobile_pct = (df['device_type'] == 'Mobile').mean() * 100
                    else:
                        mobile_pct = 0
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{mobile_pct:.1f}%</div>
                        <div class="metric-label">Mobile</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 📈 Clicks Over Time")
                    if 'timestamp' in df.columns:
                        df['date'] = pd.to_datetime(df['timestamp']).dt.date
                        timeline = df.groupby('date').size().reset_index(name='count')
                        fig = px.line(timeline, x='date', y='count', markers=True)
                        fig.update_layout(
                            height=350,
                            margin=dict(l=20, r=20, t=30, b=20),
                            hovermode='x unified',
                            plot_bgcolor='white',
                            paper_bgcolor='white'
                        )
                        fig.update_traces(line_color='#0a2c4e', marker_color='#0a2c4e')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No timeline data available")
                
                with col2:
                    st.markdown("##### 🌍 Top Countries")
                    if 'country' in df.columns:
                        countries = df['country'].value_counts().head(10)
                        if not countries.empty:
                            fig = px.bar(x=countries.values, y=countries.index, orientation='h')
                            fig.update_layout(
                                height=350,
                                margin=dict(l=20, r=20, t=30, b=20),
                                showlegend=False,
                                plot_bgcolor='white',
                                paper_bgcolor='white'
                            )
                            fig.update_traces(marker_color='#0a2c4e')
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No country data available")
                    else:
                        st.info("No country data available")
                
                # Device breakdown
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### 📱 Device Types")
                    if 'device_type' in df.columns:
                        devices = df['device_type'].value_counts()
                        if not devices.empty:
                            fig = px.pie(values=devices.values, names=devices.index, hole=0.4)
                            fig.update_layout(
                                height=350,
                                margin=dict(l=20, r=20, t=30, b=20),
                                plot_bgcolor='white',
                                paper_bgcolor='white'
                            )
                            fig.update_traces(marker=dict(colors=['#0a2c4e', '#1e4a7a', '#2d7a4b']))
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No device data available")
                    else:
                        st.info("No device data available")
                
                with col2:
                    st.markdown("##### 🌐 Top Browsers")
                    if 'browser' in df.columns:
                        browsers = df['browser'].value_counts().head(5)
                        if not browsers.empty:
                            fig = px.bar(x=browsers.values, y=browsers.index, orientation='h')
                            fig.update_layout(
                                height=350,
                                margin=dict(l=20, r=20, t=30, b=20),
                                showlegend=False,
                                plot_bgcolor='white',
                                paper_bgcolor='white'
                            )
                            fig.update_traces(marker_color='#2d7a4b')
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No browser data available")
                    else:
                        st.info("No browser data available")
                
                # Map if coordinates available
                if 'latitude' in df.columns and 'longitude' in df.columns:
                    map_df = df[df['latitude'].notna() & (df['latitude'] != 0)]
                    if not map_df.empty:
                        st.markdown("##### 🗺️ Click Locations Map")
                        st.map(map_df[['latitude', 'longitude']])
                
                # Detailed data
                st.markdown("##### 📋 Recent Clicks")
                display_cols = ['display_time' if 'display_time' in df.columns else 'timestamp']
                if 'country' in df.columns:
                    display_cols.append('country')
                if 'city' in df.columns:
                    display_cols.append('city')
                if 'device_type' in df.columns:
                    display_cols.append('device_type')
                if 'browser' in df.columns:
                    display_cols.append('browser')
                if 'os' in df.columns:
                    display_cols.append('os')
                
                display_df = df[display_cols].head(50) if display_cols else df.head(50)
                if 'display_time' in display_df.columns:
                    display_df = display_df.rename(columns={'display_time': 'Time'})
                st.dataframe(display_df, use_container_width=True)
                
                # Export
                csv = df.to_csv(index=False)
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

# ============================================================================
# TAB 3: Live Click Feed
# ============================================================================
with tab3:
    st.markdown("### 🔴 Live Click Feed")
    st.markdown("*Real-time clicks across all your links*")
    
    # Get recent clicks with safe query
    try:
        c.execute("""
            SELECT c.timestamp, c.short_code, c.country, c.city, c.device_type, c.browser, c.os
            FROM clicks c
            ORDER BY c.timestamp DESC LIMIT 50
        """)
        recent = c.fetchall()
    except:
        # Fallback without short_code
        try:
            c.execute("""
                SELECT c.timestamp, c.link_id, c.country, c.city, c.device_type, c.browser, c.os
                FROM clicks c
                ORDER BY c.timestamp DESC LIMIT 50
            """)
            recent = [(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in c.fetchall()]
        except:
            recent = []
    
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
                    time_str = f"{int(time_diff.total_seconds())}s ago"
                elif time_diff.total_seconds() < 3600:
                    time_str = f"{int(time_diff.total_seconds()/60)}m ago"
                elif time_diff.total_seconds() < 86400:
                    time_str = f"{int(time_diff.total_seconds()/3600)}h ago"
                else:
                    time_str = f"{int(time_diff.total_seconds()/86400)}d ago"
            except:
                time_str = "recently"
            
            st.markdown(f"""
            <div class="click-card">
                <div class="click-card-header">
                    <span class="click-card-code">🔗 <a href="{APP_URL}/?go={code}" target="_blank">{code}</a></span>
                    <span class="click-card-time">{time_str}</span>
                </div>
                <div class="click-card-details">
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
short_code = None

if 'go' in st.query_params:
    short_code = st.query_params['go']
elif 'id' in st.query_params:
    short_code = st.query_params['id']

if short_code:
    try:
        # Try to get by short_code first
        c.execute("SELECT original_url FROM links WHERE short_code=?", (short_code,))
        result = c.fetchone()
        
        # If not found, try by id (for backward compatibility)
        if not result:
            c.execute("SELECT original_url FROM links WHERE id=?", (short_code,))
            result = c.fetchone()
        
        if result:
            original_url = result[0]
            
            # Get accurate geolocation
            geo_data = get_accurate_geo_info()
            
            # Parse user agent
            user_agent_string = st.query_params.get('user_agent', 'Unknown')
            ua_info = parse_user_agent_accurate(user_agent_string)
            
            # Get local time
            click_time = get_local_time()
            
            # Get link_id
            c.execute("SELECT id FROM links WHERE short_code=? OR id=?", (short_code, short_code))
            link_id_result = c.fetchone()
            link_id = link_id_result[0] if link_id_result else short_code
            
            # Generate session ID
            session_id = hashlib.md5(
                f"{geo_data['ip']}{short_code}{datetime.now().strftime('%Y-%m-%d')}".encode()
            ).hexdigest()
            
            # Record click with safe insert
            try:
                c.execute("""
                    INSERT INTO clicks (
                        link_id, short_code, timestamp, ip_address, country, city, 
                        device_type, browser, os, referrer, user_agent, session_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    link_id, short_code, click_time, geo_data['ip'],
                    geo_data['country'], geo_data['city'],
                    ua_info['device_type'], ua_info['browser'],
                    ua_info['os'], st.query_params.get('referrer', 'Direct'),
                    user_agent_string, session_id
                ))
                
                c.execute("UPDATE links SET clicks = clicks + 1 WHERE id=?", (link_id,))
                conn.commit()
            except Exception as e:
                pass
            
            # Redirect page
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Redirecting...</title>
                <meta http-equiv="refresh" content="2;url={original_url}">
                <style>
                    body {{
                        margin: 0;
                        padding: 0;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: linear-gradient(135deg, #0a2c4e 0%, #1e4a7a 100%);
                        color: white;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }}
                    .container {{ text-align: center; padding: 2rem; max-width: 500px; }}
                    .card {{
                        background: rgba(255,255,255,0.1);
                        backdrop-filter: blur(10px);
                        padding: 2rem;
                        border-radius: 20px;
                        margin: 2rem 0;
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
                    @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 style="font-size: 3rem;">🔗</h1>
                    <h2>URL Shortener</h2>
                    <div class="card">
                        <p style="margin:0;"><strong>{geo_data['country']}</strong> • <strong>{geo_data['city']}</strong></p>
                        <p style="margin:0.5rem 0 0 0;">{ua_info['device_type']} • {ua_info['browser']}</p>
                    </div>
                    <div class="loader"></div>
                    <p>Redirecting you to your destination...</p>
                </div>
            </body>
            </html>
            """
            
            st.markdown(html_content, unsafe_allow_html=True)
            st.stop()
            
        else:
            st.error("Link not found")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        if 'original_url' in locals() and original_url:
            st.markdown(f'<meta http-equiv="refresh" content="2;url={original_url}">', unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("""
<div class="footer">
    <span>© 2024 URL Shortener Platform</span>
    <span class="footer-dot">•</span>
    <span>Professional Link Analytics</span>
    <span class="footer-dot">•</span>
    <span>Secure & Reliable</span>
</div>
""", unsafe_allow_html=True)