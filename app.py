import streamlit as st
import sqlite3
import requests
import pandas as pd
from datetime import datetime, timedelta
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

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="LinkMetrics Pro - URL Shortener & Analytics", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional branding
APP_NAME = "LinkMetrics Pro"
APP_DOMAIN = "linkmetrics.pro"  # This is your brand domain
APP_URL = "https://smartlink-tracker.streamlit.app"  # Your actual Streamlit URL

# Custom CSS for professional UI
st.markdown("""
<style>
    /* Professional color scheme */
    :root {
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --secondary: #7c3aed;
        --success: #059669;
        --warning: #d97706;
        --danger: #dc2626;
        --dark: #1f2937;
        --light: #f3f4f6;
    }
    
    /* Main header */
    .professional-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        padding: 2.5rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
    }
    
    /* Domain badge */
    .domain-badge {
        background: rgba(255,255,255,0.2);
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        display: inline-block;
        font-size: 1.1rem;
        margin-top: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* Card styling */
    .professional-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    .professional-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    /* URL display */
    .url-container {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
    }
    .short-url {
        color: var(--primary);
        font-size: 1.25rem;
        font-weight: 600;
        word-break: break-all;
    }
    .original-url {
        color: #64748b;
        font-size: 0.875rem;
        word-break: break-all;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary);
        line-height: 1.2;
    }
    .metric-label {
        color: #64748b;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    /* Click card for live feed */
    .click-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border: 1px solid #e2e8f0;
        border-left: 4px solid var(--primary);
        animation: slideIn 0.3s ease;
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
    
    /* Button styling */
    .stButton > button {
        background: var(--primary) !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 2rem !important;
        font-weight: 500 !important;
        border-radius: 0.375rem !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: var(--primary-dark) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: white;
        padding: 0.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
    }
    
    /* Info boxes */
    .info-box {
        background: #eff6ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid var(--primary);
        color: #1e40af;
    }
    
    /* Success message */
    .success-box {
        background: #ecfdf5;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #a7f3d0;
        color: #065f46;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Database setup
@st.cache_resource
def init_db():
    if os.getenv('STREAMLIT_SERVER_ADDRESS'):
        db_path = os.path.join(tempfile.gettempdir(), 'linkmetrics.db')
        os.makedirs(tempfile.gettempdir(), exist_ok=True)
    else:
        db_path = 'linkmetrics.db'
    
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

# Enhanced IP geolocation with multiple fallbacks
def get_accurate_geo_info(ip_address=None):
    """Get accurate geolocation data with multiple API fallbacks"""
    
    if not ip_address or ip_address == '127.0.0.1' or ip_address == '::1':
        # Use a public IP for testing (in production, this would be the real IP)
        ip_address = '8.8.8.8'  # Google DNS for testing
    
    geo_data = {
        'country': 'Unknown',
        'city': 'Unknown',
        'region': 'Unknown',
        'latitude': 0.0,
        'longitude': 0.0,
        'isp': 'Unknown',
        'ip': ip_address
    }
    
    # Try ip-api.com (fast, free, no API key needed)
    try:
        response = requests.get(f'http://ip-api.com/json/{ip_address}?fields=status,country,city,regionName,lat,lon,isp,query', timeout=3)
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
                    'ip': data.get('query', ip_address)
                })
                return geo_data
    except Exception as e:
        print(f"ip-api.com failed: {e}")
    
    # Try ipapi.co (free tier)
    try:
        response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=3)
        if response.status_code == 200:
            data = response.json()
            geo_data.update({
                'country': data.get('country_name', 'Unknown'),
                'city': data.get('city', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'latitude': data.get('latitude', 0.0),
                'longitude': data.get('longitude', 0.0),
                'isp': data.get('org', 'Unknown'),
                'ip': ip_address
            })
            return geo_data
    except Exception as e:
        print(f"ipapi.co failed: {e}")
    
    return geo_data

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
                    expires_at = (datetime.now() + timedelta(days=days)).isoformat()
                
                # Insert into database
                try:
                    link_id = hashlib.md5(f"{short_code}{datetime.now()}".encode()).hexdigest()[:12]
                    c.execute("""
                        INSERT INTO links (id, original_url, short_code, created_date, expires_at, 
                                         utm_source, utm_medium, utm_campaign, clicks)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                    """, (link_id, url, short_code, datetime.now().isoformat(), expires_at,
                          utm_source, utm_medium, utm_campaign))
                    conn.commit()
                    
                    short_url = f"{APP_URL}/?go={short_code}"
                    
                    # Success message
                    st.markdown(f"""
                    <div class="success-box">
                        <h3 style="margin:0 0 1rem 0;">✅ Link Created Successfully!</h3>
                        <div class="url-container">
                            <div class="short-url">🔗 {short_url}</div>
                            <div class="original-url">📎 {url[:100]}{'...' if len(url) > 100 else ''}</div>
                        </div>
                        <p style="margin:0.5rem 0 0 0;">
                            <strong>Short Code:</strong> {short_code}<br>
                            <strong>Created:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}<br>
                            <strong>Expires:</strong> {expires_in if expires_in != 'Never' else 'Never'}
                        </p>
                    </div>
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
            # Link info card
            st.markdown(f"""
            <div class="professional-card">
                <h4 style="margin:0 0 1rem 0;">Link Information</h4>
                <p><strong>Short Code:</strong> {short_code}</p>
                <p><strong>Original URL:</strong> <a href="{link[1]}" target="_blank">{link[1][:100]}</a></p>
                <p><strong>Created:</strong> {link[4]}</p>
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
            now = datetime.now()
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
                
                # Detailed data
                st.markdown("##### Recent Clicks")
                display_df = df[['timestamp', 'country', 'city', 'device_type', 'browser', 'os']].head(50)
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
            
            # Format time
            try:
                click_time = datetime.fromisoformat(timestamp)
                time_ago = (datetime.now() - click_time).total_seconds()
                if time_ago < 60:
                    time_str = f"{int(time_ago)} seconds ago"
                elif time_ago < 3600:
                    time_str = f"{int(time_ago/60)} minutes ago"
                else:
                    time_str = click_time.strftime("%H:%M:%S")
            except:
                time_str = timestamp
            
            st.markdown(f"""
            <div class="click-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span><strong>🔗 {code}</strong></span>
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
            
            # Get visitor IP
            # Try to get real IP from headers
            ip_address = None
            headers_to_check = [
                'X-Forwarded-For',
                'X-Real-IP',
                'CF-Connecting-IP',
                'True-Client-IP'
            ]
            
            for header in headers_to_check:
                if header in st.query_params:
                    ip_candidate = st.query_params[header].split(',')[0].strip()
                    if ip_candidate and ip_candidate != '127.0.0.1':
                        ip_address = ip_candidate
                        print(f"Found IP from header {header}: {ip_address}")
                        break
            
            if not ip_address:
                # Use a default for testing (in production, this would be handled differently)
                ip_address = '8.8.8.8'
                print(f"Using default IP: {ip_address}")
            
            # Get accurate geolocation
            geo_data = get_accurate_geo_info(ip_address)
            print(f"Geo data: {geo_data}")
            
            # Parse user agent
            user_agent_string = st.query_params.get('user_agent', 'Unknown')
            ua_info = parse_user_agent_accurate(user_agent_string)
            print(f"UA info: {ua_info}")
            
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
                    datetime.now().isoformat(),
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