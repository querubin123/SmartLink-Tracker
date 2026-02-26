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
import urllib.parse

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="SmartLink Tracker", 
    page_icon="🔗", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for enhanced UI - FIXED for better visibility
st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Card styling - FIXED for better text visibility */
    .custom-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
        transition: transform 0.3s ease;
        color: #2c3e50;
        border: 1px solid rgba(0,0,0,0.05);
    }
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
    }
    .custom-card h4 {
        color: #667eea;
        margin-top: 0;
    }
    .custom-card p {
        color: #2c3e50;
    }
    
    /* Metric cards - FIXED text visibility */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card h3 {
        font-size: 2rem;
        margin: 0;
        color: white;
        font-weight: bold;
    }
    .metric-card p {
        margin: 0;
        opacity: 0.9;
        color: white;
        font-size: 1rem;
    }
    
    /* Success message styling - FIXED */
    .success-message {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        animation: slideIn 0.5s ease;
        margin: 1rem 0;
    }
    .success-message h3 {
        color: white;
        margin-top: 0;
    }
    .success-message p {
        color: white;
    }
    .success-message code {
        background: rgba(255,255,255,0.2);
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        color: white;
    }
    
    /* Quick stats cards - FIXED */
    .quick-stats {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #2c3e50;
    }
    .quick-stats h4 {
        color: #667eea;
        margin: 0 0 0.5rem 0;
    }
    .quick-stats h2 {
        color: #2c3e50;
        margin: 0;
    }
    
    /* Info boxes - FIXED */
    .info-box {
        background: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
        color: #2c3e50;
    }
    .info-box p {
        color: #2c3e50;
        margin: 0;
    }
    
    /* Click feed cards - FIXED */
    .click-card {
        background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
        padding: 15px;
        border-radius: 10px;
        margin: 8px 0;
        border-left: 5px solid #667eea;
        animation: slideIn 0.3s ease;
        color: #2c3e50;
    }
    .click-card span {
        color: #2c3e50;
    }
    
    @keyframes slideIn {
        from {
            transform: translateY(-20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 0.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        border-radius: 0.5rem;
        padding: 0 2rem;
        font-weight: 600;
    }
    
    /* DataFrame styling */
    .dataframe-container {
        border-radius: 1rem;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        background: white;
        padding: 1rem;
    }
    
    /* Text color fixes for Streamlit default elements */
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #2c3e50;
    }
    
    /* Fix for selectbox text */
    .stSelectbox label {
        color: #2c3e50 !important;
    }
    
    /* Fix for radio buttons */
    .stRadio label {
        color: #2c3e50 !important;
    }
    
    /* Fix for metric delta colors */
    [data-testid="stMetricValue"] {
        color: #2c3e50 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #2c3e50 !important;
    }
    
    /* Fix for dataframe text */
    .stDataFrame {
        color: #2c3e50 !important;
    }
    
    /* Fix for expander text */
    .streamlit-expanderHeader {
        color: #2c3e50 !important;
    }
</style>
""", unsafe_allow_html=True)

# TOOL 1: SQLite Database - COMPLETE FIX for Streamlit Cloud
@st.cache_resource
def init_db():
    # Use /tmp directory on Streamlit Cloud, local directory otherwise
    if os.getenv('STREAMLIT_SERVER_ADDRESS'):  # Running on Streamlit Cloud
        db_path = os.path.join(tempfile.gettempdir(), 'urls.db')
        # Ensure the directory exists and is writable
        os.makedirs(tempfile.gettempdir(), exist_ok=True)
    else:  # Running locally
        db_path = 'urls.db'
    
    # Connect with proper permissions and settings for cloud
    conn = sqlite3.connect(db_path, timeout=30, check_same_thread=False)
    
    # Enable WAL mode for better concurrency on cloud
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=30000")
    
    c = conn.cursor()
    
    # Links table
    c.execute('''CREATE TABLE IF NOT EXISTS links 
                 (id TEXT PRIMARY KEY, original_url TEXT, clicks INTEGER DEFAULT 0, 
                  created_date TEXT, custom_id TEXT)''')
    
    # Clicks table with more detailed fields
    c.execute('''CREATE TABLE IF NOT EXISTS clicks 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  link_id TEXT, 
                  timestamp TEXT, 
                  country TEXT, 
                  city TEXT,
                  region TEXT,
                  latitude REAL,
                  longitude REAL,
                  isp TEXT,
                  device_type TEXT,
                  browser TEXT,
                  os TEXT,
                  ip TEXT, 
                  referrer TEXT,
                  user_agent TEXT,
                  session_id TEXT,
                  FOREIGN KEY (link_id) REFERENCES links (id))''')
    
    conn.commit()
    return conn

# Initialize connection with error handling
try:
    conn = init_db()
    
    # MIGRATION: Add missing columns if they don't exist
    def migrate_database():
        try:
            c = conn.cursor()
            
            # Check existing columns in clicks table
            c.execute("PRAGMA table_info(clicks)")
            existing_columns = [column[1] for column in c.fetchall()]
            
            # Columns to add if missing
            columns_to_add = {
                'region': 'TEXT',
                'latitude': 'REAL',
                'longitude': 'REAL',
                'isp': 'TEXT',
                'session_id': 'TEXT'
            }
            
            for column_name, column_type in columns_to_add.items():
                if column_name not in existing_columns:
                    try:
                        c.execute(f"ALTER TABLE clicks ADD COLUMN {column_name} {column_type}")
                        conn.commit()
                    except Exception as e:
                        print(f"Could not add column {column_name}: {e}")
            
        except Exception as e:
            print(f"Migration error: {e}")
    
    # Run migration
    migrate_database()
    
    # Test database is writable
    c = conn.cursor()
    c.execute("SELECT 1")
    
except Exception as e:
    st.error(f"Database initialization error: {str(e)}")
    st.stop()

# Enhanced IP geolocation function
def get_visitor_info():
    """Get detailed visitor information using multiple sources"""
    
    # Try to get real IP from various headers
    ip_address = '1.2.3.4'  # Default fallback
    headers_to_check = [
        'X-Forwarded-For',
        'X-Real-IP',
        'CF-Connecting-IP',  # Cloudflare
        'True-Client-IP',
        'HTTP_X_FORWARDED_FOR',
        'HTTP_X_REAL_IP',
        'HTTP_CF_CONNECTING_IP'
    ]
    
    # Check Streamlit's query params for headers
    for header in headers_to_check:
        if header in st.query_params:
            ip_address = st.query_params[header].split(',')[0].strip()
            break
    
    # If still default, try to get from session
    if ip_address == '1.2.3.4' and 'session_ip' in st.session_state:
        ip_address = st.session_state.session_ip
    
    # Try multiple geolocation APIs with fallback
    geo_data = {
        'country': 'Unknown',
        'city': 'Unknown',
        'region': 'Unknown',
        'latitude': 0,
        'longitude': 0,
        'isp': 'Unknown',
        'ip': ip_address
    }
    
    # Try ip-api.com first (fast and free)
    try:
        response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                geo_data.update({
                    'country': data.get('country', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'latitude': data.get('lat', 0),
                    'longitude': data.get('lon', 0),
                    'isp': data.get('isp', 'Unknown'),
                    'ip': data.get('query', ip_address)
                })
                return geo_data
    except:
        pass
    
    # Fallback to ipapi.co
    try:
        response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=3)
        if response.status_code == 200:
            data = response.json()
            geo_data.update({
                'country': data.get('country_name', 'Unknown'),
                'city': data.get('city', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'latitude': data.get('latitude', 0),
                'longitude': data.get('longitude', 0),
                'isp': data.get('org', 'Unknown'),
                'ip': ip_address
            })
            return geo_data
    except:
        pass
    
    return geo_data

# Enhanced header for the app
st.markdown("""
<div class="main-header">
    <h1>🔗 SmartLink Tracker</h1>
    <p style="font-size: 1.2rem; opacity: 0.95;">Advanced URL Shortener + Detailed Click Analytics</p>
    <p style="font-size: 1rem; opacity: 0.9;">Track every click with precision - Country, City, Device, Browser, and more!</p>
</div>
""", unsafe_allow_html=True)

# TOOL 2: Streamlit Tabs UI
tab1, tab2, tab3 = st.tabs(["🎯 Create Short Link", "📊 Analytics Dashboard", "📡 Live Click Feed"])

# CREATE LINK (TAB 1)
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### ✨ Create New Tracking Link")
        
        with st.form("shorten", clear_on_submit=False):
            # Main URL input
            original_url = st.text_input(
                "📎 Paste your long URL",
                placeholder="https://your-long-sales-page.com/path?param=value",
                help="Enter the URL you want to shorten and track"
            )
            
            # Advanced options in an expander
            with st.expander("⚙️ Advanced Options", expanded=False):
                col_a, col_b = st.columns(2)
                with col_a:
                    custom_id = st.text_input(
                        "🔖 Custom ID (optional)",
                        placeholder="e.g., summer-sale-2024",
                        help="Create a memorable custom short code"
                    )
                with col_b:
                    st.markdown(" ")
                    st.markdown(" ")
                    st.info("If left blank, a random ID will be generated")
                
                st.markdown("#### 📊 UTM Parameters (for campaign tracking)")
                col_c, col_d, col_e = st.columns(3)
                with col_c:
                    utm_source = st.text_input("UTM Source", placeholder="facebook")
                with col_d:
                    utm_medium = st.text_input("UTM Medium", placeholder="social")
                with col_e:
                    utm_campaign = st.text_input("UTM Campaign", placeholder="summer_sale")
            
            # Submit button
            submitted = st.form_submit_button(
                "🚀 Generate Short Link",
                use_container_width=True,
                type="primary"
            )
            
            if submitted:
                if original_url:
                    # Add UTM parameters if provided
                    if utm_source or utm_medium or utm_campaign:
                        separator = '&' if '?' in original_url else '?'
                        utm_params = []
                        if utm_source:
                            utm_params.append(f"utm_source={utm_source}")
                        if utm_medium:
                            utm_params.append(f"utm_medium={utm_medium}")
                        if utm_campaign:
                            utm_params.append(f"utm_campaign={utm_campaign}")
                        
                        if utm_params:
                            original_url = f"{original_url}{separator}{'&'.join(utm_params)}"
                    
                    # Generate link ID
                    if custom_id:
                        # Clean the custom ID
                        custom_id = re.sub(r'[^a-zA-Z0-9-_]', '', custom_id).lower()
                        link_id = custom_id
                    else:
                        link_id = base64.urlsafe_b64encode(os.urandom(3)).decode().rstrip('=')
                    
                    # Create cursor and execute query with retry logic
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            c = conn.cursor()
                            # Check if ID already exists
                            c.execute("SELECT id FROM links WHERE id=?", (link_id,))
                            if c.fetchone():
                                st.error("❌ This custom ID is already taken. Please try another one.")
                                break
                            else:
                                # Insert new link
                                custom_id_value = custom_id if custom_id else None
                                c.execute("""
                                    INSERT INTO links (id, original_url, clicks, created_date, custom_id) 
                                    VALUES (?, ?, ?, ?, ?)
                                """, (link_id, original_url, 0, datetime.now().isoformat(), custom_id_value))
                                conn.commit()
                                
                                # Use your actual deployed URL
                                base_url = "https://smartlink-tracker.streamlit.app"
                                short_url = f"{base_url}/?id={link_id}"
                                
                                # Display success with enhanced UI
                                st.markdown(f"""
                                <div class="success-message">
                                    <h3>✅ Link Created Successfully!</h3>
                                    <p style="font-size: 1.2rem;">Your tracking link is ready:</p>
                                    <div style="background: white; color: #333; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
                                        <a href="{short_url}" target="_blank" style="color: #667eea; font-size: 1.1rem; word-break: break-all;">
                                            {short_url}
                                        </a>
                                    </div>
                                    <p style="font-size: 1rem;">Link ID: <code>{link_id}</code></p>
                                    <p>Share this link to start tracking clicks!</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.balloons()
                                break
                                
                        except sqlite3.OperationalError as e:
                            if "database is locked" in str(e) and attempt < max_retries - 1:
                                time.sleep(1)
                                continue
                            else:
                                st.error(f"❌ Database error: {str(e)}")
                                break
                        except sqlite3.IntegrityError:
                            st.error("❌ This custom ID is already taken. Please choose another one.")
                            break
                        except Exception as e:
                            st.error(f"❌ An error occurred: {str(e)}")
                            break
                else:
                    st.error("❌ Please enter a URL to shorten")
    
    with col2:
        st.markdown("### 📈 Quick Stats")
        
        # Get total links count
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM links")
        total_links = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM clicks")
        total_clicks = c.fetchone()[0]
        
        # Display stats in cards
        st.markdown(f"""
        <div class="quick-stats">
            <h4>Total Links Created</h4>
            <h2 style="color: #667eea;">{total_links}</h2>
        </div>
        
        <div class="quick-stats">
            <h4>Total Clicks Tracked</h4>
            <h2 style="color: #764ba2;">{total_clicks}</h2>
        </div>
        
        <div class="quick-stats">
            <h4>Conversion Rate</h4>
            <h2 style="color: #10b981;">{((total_clicks/total_links)*100 if total_links > 0 else 0):.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)

# ANALYTICS (TAB 2)  
with tab2:
    st.markdown("### 📊 Link Analytics Dashboard")
    
    try:
        # Get all links for selection
        c = conn.cursor()
        c.execute("SELECT id, custom_id, created_date, clicks FROM links ORDER BY created_date DESC")
        all_links = c.fetchall()
        
        if all_links:
            # Create a selection box with all links
            link_options = {}
            for link in all_links:
                display_name = f"🔗 {link[1] if link[1] else link[0]}"
                display_name += f" (Created: {link[2][:10]})"
                if link[3] > 0:
                    display_name += f" - {link[3]} clicks"
                link_options[display_name] = link[0]
            
            selected_display = st.selectbox(
                "🔍 Select a link to analyze",
                options=list(link_options.keys()),
                help="Choose a link to view detailed analytics"
            )
            link_id = link_options[selected_display]
            
            if link_id:
                # Get link details
                c.execute("SELECT * FROM links WHERE id=?", (link_id,))
                link = c.fetchone()
                
                if link:
                    # Display link info in a nice card
                    st.markdown(f"""
                    <div class="custom-card">
                        <h4>Link Information</h4>
                        <p><strong>Original URL:</strong> <a href="{link[1]}" target="_blank">{link[1][:80]}...</a></p>
                        <p><strong>Created:</strong> {link[3]}</p>
                        <p><strong>Total Lifetime Clicks:</strong> {link[2]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Get detailed analytics
                    c.execute("SELECT COUNT(*) FROM clicks WHERE link_id=?", (link_id,))
                    total_clicks = c.fetchone()[0]
                    
                    # Time-based filters
                    st.markdown("### 📅 Time Range Filter")
                    time_filter = st.radio(
                        "Select period",
                        ["All Time", "Today", "Last 7 Days", "Last 30 Days", "Custom Range"],
                        horizontal=True
                    )
                    
                    today = datetime.now().date()
                    start_date = None
                    end_date = None
                    
                    if time_filter == "Today":
                        start_date = datetime.combine(today, datetime.min.time()).isoformat()
                    elif time_filter == "Last 7 Days":
                        start_date = (datetime.now() - timedelta(days=7)).isoformat()
                    elif time_filter == "Last 30 Days":
                        start_date = (datetime.now() - timedelta(days=30)).isoformat()
                    elif time_filter == "Custom Range":
                        col_a, col_b = st.columns(2)
                        with col_a:
                            start_date = st.date_input("Start Date", today - timedelta(days=7))
                        with col_b:
                            end_date = st.date_input("End Date", today)
                        if start_date and end_date:
                            start_date = datetime.combine(start_date, datetime.min.time()).isoformat()
                            end_date = datetime.combine(end_date, datetime.max.time()).isoformat()
                    
                    # Top metrics in columns
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        # Total clicks (filtered)
                        if start_date and end_date:
                            c.execute("SELECT COUNT(*) FROM clicks WHERE link_id=? AND timestamp BETWEEN ? AND ?", 
                                     (link_id, start_date, end_date))
                        elif start_date:
                            c.execute("SELECT COUNT(*) FROM clicks WHERE link_id=? AND timestamp>=?", 
                                     (link_id, start_date))
                        else:
                            c.execute("SELECT COUNT(*) FROM clicks WHERE link_id=?", (link_id,))
                        filtered_clicks = c.fetchone()[0]
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>{filtered_clicks}</h3>
                            <p>Total Clicks</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # Unique countries
                        query = "SELECT COUNT(DISTINCT country) FROM clicks WHERE link_id=?"
                        params = [link_id]
                        if start_date and end_date:
                            query += " AND timestamp BETWEEN ? AND ?"
                            params.extend([start_date, end_date])
                        elif start_date:
                            query += " AND timestamp >= ?"
                            params.append(start_date)
                        c.execute(query, params)
                        countries_count = c.fetchone()[0]
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>{countries_count}</h3>
                            <p>Countries</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        # Device breakdown
                        query = "SELECT device_type, COUNT(*) FROM clicks WHERE link_id=?"
                        params = [link_id]
                        if start_date and end_date:
                            query += " AND timestamp BETWEEN ? AND ?"
                            params.extend([start_date, end_date])
                        elif start_date:
                            query += " AND timestamp >= ?"
                            params.append(start_date)
                        query += " GROUP BY device_type"
                        
                        c.execute(query, params)
                        device_data = c.fetchall()
                        
                        mobile_clicks = sum(count for device, count in device_data if device and 'Mobile' in device)
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>{mobile_clicks}</h3>
                            <p>Mobile Clicks</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        # Average clicks per day
                        if filtered_clicks > 0 and start_date:
                            days = 1
                            if time_filter == "Last 7 Days":
                                days = 7
                            elif time_filter == "Last 30 Days":
                                days = 30
                            elif time_filter == "Custom Range" and end_date:
                                start = datetime.fromisoformat(start_date)
                                end = datetime.fromisoformat(end_date)
                                days = max((end - start).days, 1)
                            avg_per_day = filtered_clicks / days
                        else:
                            avg_per_day = filtered_clicks
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <h3>{avg_per_day:.1f}</h3>
                            <p>Avg/Day</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Charts Row
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📈 Clicks Over Time")
                        # Get clicks by date
                        query = """SELECT DATE(timestamp) as date, COUNT(*) 
                                  FROM clicks WHERE link_id=?"""
                        params = [link_id]
                        if start_date and end_date:
                            query += " AND timestamp BETWEEN ? AND ?"
                            params.extend([start_date, end_date])
                        elif start_date:
                            query += " AND timestamp >= ?"
                            params.append(start_date)
                        query += " GROUP BY DATE(timestamp) ORDER BY date"
                        
                        c.execute(query, params)
                        timeline_data = c.fetchall()
                        
                        if timeline_data:
                            df_timeline = pd.DataFrame(timeline_data, columns=['Date', 'Clicks'])
                            fig = px.line(df_timeline, x='Date', y='Clicks', markers=True)
                            fig.update_layout(
                                height=300,
                                margin=dict(l=20, r=20, t=30, b=20),
                                hovermode='x unified'
                            )
                            fig.update_traces(line_color='#667eea')
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("📊 No click data available for this period")
                    
                    with col2:
                        st.markdown("#### 🌍 Geographic Distribution")
                        # Get clicks by country
                        query = "SELECT country, COUNT(*) FROM clicks WHERE link_id=?"
                        params = [link_id]
                        if start_date and end_date:
                            query += " AND timestamp BETWEEN ? AND ?"
                            params.extend([start_date, end_date])
                        elif start_date:
                            query += " AND timestamp >= ?"
                            params.append(start_date)
                        query += " GROUP BY country ORDER BY COUNT(*) DESC LIMIT 10"
                        
                        c.execute(query, params)
                        country_data = c.fetchall()
                        
                        if country_data:
                            df_countries = pd.DataFrame(country_data, columns=['Country', 'Clicks'])
                            fig = px.bar(df_countries, x='Country', y='Clicks', color='Clicks')
                            fig.update_layout(
                                height=300,
                                margin=dict(l=20, r=20, t=30, b=20),
                                showlegend=False
                            )
                            fig.update_traces(marker_color='#764ba2')
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("🗺️ No country data available")
                    
                    # Second row of charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📱 Device Type Breakdown")
                        if device_data:
                            df_devices = pd.DataFrame(device_data, columns=['Device', 'Count'])
                            fig = px.pie(df_devices, values='Count', names='Device', hole=0.4)
                            fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                            fig.update_traces(marker=dict(colors=['#667eea', '#764ba2', '#10b981']))
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("📱 No device data available")
                    
                    with col2:
                        st.markdown("#### 🖥️ Operating Systems")
                        # Get OS breakdown
                        query = "SELECT os, COUNT(*) FROM clicks WHERE link_id=? AND os IS NOT NULL"
                        params = [link_id]
                        if start_date and end_date:
                            query += " AND timestamp BETWEEN ? AND ?"
                            params.extend([start_date, end_date])
                        elif start_date:
                            query += " AND timestamp >= ?"
                            params.append(start_date)
                        query += " GROUP BY os ORDER BY COUNT(*) DESC LIMIT 5"
                        
                        c.execute(query, params)
                        os_data = c.fetchall()
                        
                        if os_data:
                            df_os = pd.DataFrame(os_data, columns=['OS', 'Count'])
                            fig = px.bar(df_os, x='OS', y='Count', color='Count')
                            fig.update_layout(
                                height=300,
                                margin=dict(l=20, r=20, t=30, b=20),
                                showlegend=False
                            )
                            fig.update_traces(marker_color='#10b981')
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("💻 No OS data available")
                    
                    # Detailed click table
                    st.markdown("#### 📋 Recent Clicks")
                    
                    # Check which columns exist
                    c.execute("PRAGMA table_info(clicks)")
                    available_columns = [col[1] for col in c.fetchall()]
                    
                    # Build query based on available columns
                    base_columns = ['timestamp', 'country', 'city', 'device_type', 'browser', 'os', 'ip']
                    optional_columns = []
                    
                    if 'region' in available_columns:
                        optional_columns.append('region')
                    if 'latitude' in available_columns:
                        optional_columns.append('latitude')
                    if 'longitude' in available_columns:
                        optional_columns.append('longitude')
                    
                    all_columns = base_columns + optional_columns
                    columns_str = ', '.join(all_columns)
                    
                    query = f"SELECT {columns_str} FROM clicks WHERE link_id=? ORDER BY id DESC LIMIT 100"
                    
                    try:
                        clicks_df = pd.read_sql_query(query, conn, params=(link_id,))
                        
                        if not clicks_df.empty:
                            # Show map if we have coordinates
                            if 'latitude' in clicks_df.columns and 'longitude' in clicks_df.columns:
                                map_df = clicks_df[clicks_df['latitude'].notna() & (clicks_df['latitude'] != 0)]
                                if not map_df.empty:
                                    st.markdown("##### 🗺️ Click Locations Map")
                                    st.map(map_df[['latitude', 'longitude']])
                            
                            # Show data table
                            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                            
                            # Remove coordinate columns from display table
                            display_df = clicks_df.copy()
                            if 'latitude' in display_df.columns:
                                display_df = display_df.drop(['latitude', 'longitude'], axis=1)
                            
                            st.dataframe(display_df, use_container_width=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Export options
                            col1, col2 = st.columns(2)
                            with col1:
                                csv = clicks_df.to_csv(index=False)
                                st.download_button(
                                    "📥 Export Full Data as CSV", 
                                    csv, 
                                    f"{link_id}_clicks.csv",
                                    "text/csv",
                                    use_container_width=True
                                )
                            with col2:
                                st.info(f"**Total in period:** {len(clicks_df)} | **Last Click:** {clicks_df['timestamp'].iloc[0][:19] if len(clicks_df) > 0 else 'N/A'}")
                        else:
                            st.info("📭 No clicks recorded yet for this link in the selected period")
                    except Exception as e:
                        st.error(f"Error loading click data: {str(e)}")
                        # Fallback to simple query
                        try:
                            simple_df = pd.read_sql_query(
                                """SELECT timestamp, country, city, device_type, browser, os, ip 
                                   FROM clicks WHERE link_id=? ORDER BY id DESC LIMIT 100""", 
                                conn, params=(link_id,))
                            if not simple_df.empty:
                                st.dataframe(simple_df, use_container_width=True)
                        except:
                            st.info("No click data available")
        else:
            st.info("👋 No links created yet. Go to the 'Create Short Link' tab to create your first tracking link!")
            
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

# LIVE CLICK FEED (TAB 3)
with tab3:
    st.markdown("### 📡 Live Click Feed")
    st.markdown("*Watch clicks happen in real-time! Updates every 5 seconds.*")
    
    # Get recent clicks across all links
    try:
        c = conn.cursor()
        c.execute("""
            SELECT c.timestamp, COALESCE(l.custom_id, l.id), c.country, c.city, 
                   c.device_type, c.browser, c.os
            FROM clicks c
            JOIN links l ON c.link_id = l.id
            ORDER BY c.id DESC LIMIT 20
        """)
        recent_clicks = c.fetchall()
        
        if recent_clicks:
            for click in recent_clicks:
                timestamp, link_id, country, city, device, browser, os = click
                
                # Create an enhanced card for each click
                st.markdown(f"""
                <div class="click-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.1rem;"><b>🔗 {link_id}</b></span>
                        <span style="color: #666; font-size: 0.9rem;">{timestamp[:19]}</span>
                    </div>
                    <div style="display: flex; gap: 20px; margin-top: 10px; flex-wrap: wrap;">
                        <span>🌍 {country}{f' ({city})' if city else ''}</span>
                        <span>📱 {device}</span>
                        <span>🌐 {browser}</span>
                        <span>💻 {os}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Auto-refresh note
            st.caption("🔄 Live feed updates on page refresh")
        else:
            st.info("📭 No clicks recorded yet. Share your links to start tracking!")
            
    except Exception as e:
        st.info("📭 Waiting for first clicks...")

# FIXED: Click Tracker (hidden redirect) - This must run BEFORE any other UI elements
if 'id' in st.query_params:
    link_id = st.query_params['id']
    
    try:
        # Create cursor with error handling
        c = conn.cursor()
        c.execute("SELECT original_url FROM links WHERE id=?", (link_id,))
        result = c.fetchone()
        
        if result:
            original_url = result[0]
            
            # Get user agent for detailed device info
            user_agent_string = st.query_params.get('user_agent', 'Unknown')
            
            # Parse user agent if available
            try:
                user_agent = parse(user_agent_string)
                device_type = 'Mobile' if user_agent.is_mobile else 'Tablet' if user_agent.is_tablet else 'Desktop'
                browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
                os = f"{user_agent.os.family} {user_agent.os.version_string}"
            except:
                device_type = 'Unknown'
                browser = 'Unknown'
                os = 'Unknown'
            
            # Get enhanced geolocation data
            geo_data = get_visitor_info()
            
            # Generate session ID
            session_id = base64.urlsafe_b64encode(os.urandom(8)).decode()
            st.session_state.session_ip = geo_data['ip']
            
            # Get referrer
            referrer = st.query_params.get('referrer', 'Direct')
            
            # Insert click data with retry logic
            click_success = False
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    c.execute("""
                        INSERT INTO clicks 
                        (link_id, timestamp, country, city, region, latitude, longitude, isp,
                         device_type, browser, os, ip, referrer, user_agent, session_id) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        link_id, 
                        datetime.now().isoformat(), 
                        geo_data['country'], 
                        geo_data['city'],
                        geo_data['region'],
                        geo_data['latitude'],
                        geo_data['longitude'],
                        geo_data['isp'],
                        device_type,
                        browser,
                        os,
                        geo_data['ip'], 
                        referrer,
                        user_agent_string,
                        session_id
                    ))
                    
                    # Update click count
                    c.execute("UPDATE links SET clicks = clicks + 1 WHERE id = ?", (link_id,))
                    conn.commit()
                    click_success = True
                    print(f"✅ Click tracked for link: {link_id}")
                    break
                except Exception as e:
                    print(f"Error tracking click (attempt {attempt+1}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(0.5)
                        continue
            
            # Always redirect, even if tracking fails
            if click_success:
                # Show tracking page with info
                st.markdown(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta http-equiv="refresh" content="2;url={original_url}">
                    <style>
                        body {{
                            margin: 0;
                            padding: 0;
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
                        .info-card {{
                            background: rgba(255, 255, 255, 0.1);
                            backdrop-filter: blur(10px);
                            padding: 2rem;
                            border-radius: 20px;
                            margin: 2rem 0;
                        }}
                        .location-grid {{
                            display: grid;
                            grid-template-columns: repeat(2, 1fr);
                            gap: 1rem;
                            margin: 1.5rem 0;
                        }}
                        .location-item {{
                            background: rgba(255, 255, 255, 0.05);
                            padding: 1rem;
                            border-radius: 10px;
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
                        h2 {{ margin: 0.5rem 0; }}
                        p {{ margin: 0.5rem 0; opacity: 0.9; }}
                        a {{ color: white; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🔗</h1>
                        <h2>SmartLink Tracker</h2>
                        <div class="info-card">
                            <h3>📍 Your Location</h3>
                            <div class="location-grid">
                                <div class="location-item">
                                    <div>🌍 Country</div>
                                    <strong>{geo_data['country']}</strong>
                                </div>
                                <div class="location-item">
                                    <div>🏙️ City</div>
                                    <strong>{geo_data['city']}</strong>
                                </div>
                                <div class="location-item">
                                    <div>📱 Device</div>
                                    <strong>{device_type}</strong>
                                </div>
                                <div class="location-item">
                                    <div>🌐 Browser</div>
                                    <strong>{browser}</strong>
                                </div>
                            </div>
                        </div>
                        <div class="loader"></div>
                        <p style="font-size: 1.2rem;">Tracking your click...</p>
                        <p>Redirecting to destination in 2 seconds</p>
                        <p><small>If you're not redirected, <a href="{original_url}">click here</a></small></p>
                    </div>
                </body>
                </html>
                """, unsafe_allow_html=True)
            else:
                # Simple redirect if tracking failed
                st.markdown(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta http-equiv="refresh" content="1;url={original_url}">
                </head>
                <body>
                    <p>Redirecting...</p>
                </body>
                </html>
                """, unsafe_allow_html=True)
            
            # Stop further Streamlit execution
            st.stop()
            
        else:
            st.error("❌ Link not found. Please check the URL.")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        if 'result' in locals() and result and result[0]:
            st.markdown(f'<meta http-equiv="refresh" content="2;url={result[0]}">', unsafe_allow_html=True)