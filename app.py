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

# TOOL 1: SQLite Database (auto-creates) - FIXED FOR STREAMLIT CLOUD
@st.cache_resource
def init_db():
    # Check if running on Streamlit Cloud
    import os
    import tempfile
    
    # Use /tmp directory on Streamlit Cloud, local directory otherwise
    if os.getenv('STREAMLIT_SERVER_ADDRESS'):  # Running on Streamlit Cloud
        db_path = os.path.join(tempfile.gettempdir(), 'urls.db')
    else:  # Running locally
        db_path = 'urls.db'
    
    conn = sqlite3.connect(db_path, check_same_thread=False)
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
                  device_type TEXT,
                  browser TEXT,
                  os TEXT,
                  ip TEXT, 
                  referrer TEXT,
                  user_agent TEXT,
                  FOREIGN KEY (link_id) REFERENCES links (id))''')
    
    conn.commit()
    return conn
conn = init_db()

st.set_page_config(page_title="SmartLink Tracker", page_icon="🔗", layout="wide")

st.title("🔗 SmartLink Tracker")
st.markdown("**Advanced URL Shortener + Detailed Click Analytics**")

# TOOL 2: Streamlit Tabs UI
tab1, tab2, tab3 = st.tabs(["➕ Create Short Link", "📊 Analytics Dashboard", "📈 Live Click Feed"])

# CREATE LINK (TAB 1)
with tab1:
    st.subheader("Create New Tracking Link")
    with st.form("shorten"):
        col1, col2 = st.columns([3,1])
        with col1:
            original_url = st.text_input("📎 Paste long URL", placeholder="https://your-long-sales-page.com")
        with col2:
            custom_id = st.text_input("🔖 Custom ID (optional)", placeholder="demo")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            utm_source = st.text_input("UTM Source", placeholder="facebook")
        with col2:
            utm_medium = st.text_input("UTM Medium", placeholder="social")
        with col3:
            utm_campaign = st.text_input("UTM Campaign", placeholder="summer_sale")
        
        if st.form_submit_button("✂️ Generate Short Link", use_container_width=True):
            if original_url:  # Check if URL is provided
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
                    link_id = custom_id
                else:
                    link_id = base64.urlsafe_b64encode(os.urandom(3)).decode().rstrip('=')
                
                # Create cursor and execute query
                c = conn.cursor()
                try:
                    # FIXED: Explicit INSERT with proper NULL handling
                    custom_id_value = custom_id if custom_id else None
                    
                    c.execute("""
                        INSERT INTO links (id, original_url, clicks, created_date, custom_id) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (link_id, original_url, 0, datetime.now().isoformat(), custom_id_value))
                    conn.commit()
                    
                    # FIXED: Use your actual deployed URL
                    base_url = "https://smartlink-tracker.streamlit.app"
                    
                    short_url = f"{base_url}/?id={link_id}"
                    
                    st.success("✅ Link created successfully!")
                    
                    # Display link in a nice box
                    st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 10px 0;">
                        <h4 style="margin:0">Your Tracking Link:</h4>
                        <p style="font-size: 18px; margin:10px 0">
                            <a href='{short_url}' target='_blank'>{short_url}</a>
                        </p>
                        <p style="color: #666; margin:5px 0">ID: <code>{link_id}</code></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.balloons()
                    
                except sqlite3.IntegrityError as e:
                    st.error(f"❌ This custom ID is already taken. Please choose another one.")
                    print(f"Database error: {e}")
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
                    print(f"Error: {e}")
            else:
                st.error("❌ Please enter a URL")

# ANALYTICS (TAB 2)  
with tab2:
    st.subheader("Link Analytics Dashboard")
    
    # Get all links for selection
    c = conn.cursor()
    c.execute("SELECT id, custom_id, created_date, clicks FROM links ORDER BY created_date DESC")
    all_links = c.fetchall()
    
    if all_links:
        # Create a selection box with all links
        link_options = {f"{link[1] if link[1] else link[0]} (Created: {link[2][:10]})": link[0] for link in all_links}
        selected_display = st.selectbox("Select a link to analyze", options=list(link_options.keys()))
        link_id = link_options[selected_display]
        
        if link_id:
            # Get link details
            c.execute("SELECT * FROM links WHERE id=?", (link_id,))
            link = c.fetchone()
            
            if link:
                # Display link info
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Original URL:** {link[1][:50]}..." if len(link[1]) > 50 else f"**Original URL:** {link[1]}")
                with col2:
                    st.info(f"**Created:** {link[3]}")
                
                # Get detailed analytics
                c.execute("SELECT COUNT(*) FROM clicks WHERE link_id=?", (link_id,))
                total_clicks = c.fetchone()[0]
                
                # Time-based filters
                time_filter = st.radio("Time Range", ["All Time", "Today", "Last 7 Days", "Last 30 Days"], horizontal=True)
                
                today = datetime.now().date()
                if time_filter == "Today":
                    start_date = datetime.combine(today, datetime.min.time()).isoformat()
                elif time_filter == "Last 7 Days":
                    start_date = (datetime.now() - timedelta(days=7)).isoformat()
                elif time_filter == "Last 30 Days":
                    start_date = (datetime.now() - timedelta(days=30)).isoformat()
                else:
                    start_date = None
                
                # Apply time filter to queries
                def add_time_filter(query):
                    if start_date:
                        return query + " AND timestamp >= ?"
                    return query
                
                # Top metrics
                col1, col2, col3, col4 = st.columns(4)
                
                # Total clicks (filtered)
                if start_date:
                    c.execute("SELECT COUNT(*) FROM clicks WHERE link_id=? AND timestamp>=?", (link_id, start_date))
                else:
                    c.execute("SELECT COUNT(*) FROM clicks WHERE link_id=?", (link_id,))
                filtered_clicks = c.fetchone()[0]
                
                col1.metric("📊 Total Clicks", filtered_clicks, delta=filtered_clicks-total_clicks if filtered_clicks != total_clicks else None)
                
                # Unique countries
                query = "SELECT COUNT(DISTINCT country) FROM clicks WHERE link_id=?"
                if start_date:
                    c.execute(add_time_filter(query), (link_id, start_date))
                else:
                    c.execute(query, (link_id,))
                countries_count = c.fetchone()[0]
                col2.metric("🌍 Countries", countries_count)
                
                # Device breakdown
                query = "SELECT device_type, COUNT(*) FROM clicks WHERE link_id=?"
                params = [link_id]
                if start_date:
                    query += " AND timestamp>=?"
                    params.append(start_date)
                query += " GROUP BY device_type"
                
                c.execute(query, params)
                device_data = c.fetchall()
                
                mobile_clicks = sum(count for device, count in device_data if device and 'Mobile' in device)
                col3.metric("📱 Mobile", mobile_clicks)
                
                # Browsers
                query = "SELECT COUNT(DISTINCT browser) FROM clicks WHERE link_id=? AND browser IS NOT NULL"
                if start_date:
                    c.execute(add_time_filter(query), (link_id, start_date))
                else:
                    c.execute(query, (link_id,))
                browsers_count = c.fetchone()[0]
                col4.metric("🌐 Browsers", browsers_count)
                
                # Charts Row
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 Clicks Over Time")
                    # Get clicks by date
                    query = """SELECT DATE(timestamp) as date, COUNT(*) 
                              FROM clicks WHERE link_id=?"""
                    params = [link_id]
                    if start_date:
                        query += " AND timestamp>=?"
                        params.append(start_date)
                    query += " GROUP BY DATE(timestamp) ORDER BY date"
                    
                    c.execute(query, params)
                    timeline_data = c.fetchall()
                    
                    if timeline_data:
                        df_timeline = pd.DataFrame(timeline_data, columns=['Date', 'Clicks'])
                        fig = px.line(df_timeline, x='Date', y='Clicks', markers=True)
                        fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No click data available for this period")
                
                with col2:
                    st.subheader("🌍 Geographic Distribution")
                    # Get clicks by country
                    query = "SELECT country, COUNT(*) FROM clicks WHERE link_id=?"
                    params = [link_id]
                    if start_date:
                        query += " AND timestamp>=?"
                        params.append(start_date)
                    query += " GROUP BY country ORDER BY COUNT(*) DESC LIMIT 10"
                    
                    c.execute(query, params)
                    country_data = c.fetchall()
                    
                    if country_data:
                        df_countries = pd.DataFrame(country_data, columns=['Country', 'Clicks'])
                        fig = px.bar(df_countries, x='Country', y='Clicks', color='Clicks')
                        fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No country data available")
                
                # Second row of charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📱 Device Type Breakdown")
                    if device_data:
                        df_devices = pd.DataFrame(device_data, columns=['Device', 'Count'])
                        fig = px.pie(df_devices, values='Count', names='Device', hole=0.4)
                        fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No device data available")
                
                with col2:
                    st.subheader("🖥️ Operating Systems")
                    # Get OS breakdown
                    query = "SELECT os, COUNT(*) FROM clicks WHERE link_id=? AND os IS NOT NULL"
                    params = [link_id]
                    if start_date:
                        query += " AND timestamp>=?"
                        params.append(start_date)
                    query += " GROUP BY os ORDER BY COUNT(*) DESC LIMIT 5"
                    
                    c.execute(query, params)
                    os_data = c.fetchall()
                    
                    if os_data:
                        df_os = pd.DataFrame(os_data, columns=['OS', 'Count'])
                        fig = px.bar(df_os, x='OS', y='Count', color='Count')
                        fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No OS data available")
                
                # Detailed click table
                st.subheader("📋 Recent Clicks")
                clicks_df = pd.read_sql_query(
                    """SELECT timestamp, country, city, device_type, browser, os, ip 
                       FROM clicks WHERE link_id=? ORDER BY id DESC LIMIT 100""", 
                    conn, params=(link_id,))
                
                if not clicks_df.empty:
                    st.dataframe(clicks_df, use_container_width=True)
                    
                    # Export options
                    col1, col2 = st.columns(2)
                    with col1:
                        csv = clicks_df.to_csv(index=False)
                        st.download_button(
                            "📥 Export as CSV", 
                            csv, 
                            f"{link_id}_clicks.csv",
                            "text/csv",
                            use_container_width=True
                        )
                    with col2:
                        # Summary statistics
                        st.info(f"**Total Clicks:** {len(clicks_df)} | **Last Click:** {clicks_df['timestamp'].iloc[0][:19] if len(clicks_df) > 0 else 'N/A'}")
                else:
                    st.info("No clicks recorded yet for this link")
    else:
        st.info("👋 No links created yet. Go to the 'Create Short Link' tab to create your first tracking link!")

# LIVE CLICK FEED (TAB 3)
with tab3:
    st.subheader("📡 Live Click Feed")
    
    # Auto-refresh every 5 seconds
    refresh_interval = 5
    
    # Get recent clicks across all links
    c = conn.cursor()
    c.execute("""
        SELECT c.timestamp, l.custom_id or l.id, c.country, c.city, c.device_type, c.browser
        FROM clicks c
        JOIN links l ON c.link_id = l.id
        ORDER BY c.id DESC LIMIT 20
    """)
    recent_clicks = c.fetchall()
    
    if recent_clicks:
        for click in recent_clicks:
            timestamp, link_id, country, city, device, browser = click
            
            # Create a nice card for each click
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 4px solid #ff4b4b;">
                <div style="display: flex; justify-content: space-between;">
                    <span><b>🔗 {link_id}</b></span>
                    <span style="color: #666;">{timestamp[:19]}</span>
                </div>
                <div style="margin-top: 5px;">
                    <span>🌍 {country}{f' ({city})' if city else ''}</span> | 
                    <span>📱 {device}</span> | 
                    <span>🌐 {browser}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.caption(f"🔄 Auto-refreshes every {refresh_interval} seconds")
        st.markdown("""
        <script>
            setTimeout(function() {
                window.location.reload();
            }, 5000);
        </script>
        """, unsafe_allow_html=True)
    else:
        st.info("No clicks recorded yet")

# TOOL 5: Click Tracker (hidden redirect)
if 'id' in st.query_params:
    link_id = st.query_params['id']
    
    # Create cursor
    c = conn.cursor()
    c.execute("SELECT original_url FROM links WHERE id=?", (link_id,))
    result = c.fetchone()
    
    if result:
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
        
        # TOOL 6: Free IP geolocation with city-level data
        try:
            # Try to get client IP (in production, you'd get this from headers)
            ip_response = requests.get('http://ip-api.com/json', timeout=2)
            ip_data = ip_response.json()
            country = ip_data.get('country', 'Unknown')
            city = ip_data.get('city', 'Unknown')
            ip = ip_data.get('query', '1.2.3.4')
            
            # Override device detection with IP data if available
            if 'mobile' in ip_data:
                device_type = 'Mobile' if ip_data.get('mobile', False) else device_type
        except:
            country, city, ip = 'Unknown', 'Unknown', '1.2.3.4'
        
        # Get referrer
        referrer = st.query_params.get('referrer', 'Direct')
        
        # Insert detailed click data
        c.execute("""
            INSERT INTO clicks 
            (link_id, timestamp, country, city, device_type, browser, os, ip, referrer, user_agent) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            link_id, 
            datetime.now().isoformat(), 
            country, 
            city,
            device_type,
            browser,
            os,
            ip, 
            referrer,
            user_agent_string
        ))
        
        # Update click count in links table
        c.execute("UPDATE links SET clicks = clicks + 1 WHERE id = ?", (link_id,))
        conn.commit()
        
        # Redirect to original URL with loading animation
        st.markdown(f"""
        <style>
            .redirect-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .loader {{
                border: 5px solid #f3f3f3;
                border-top: 5px solid #3498db;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
        
        <div class="redirect-container">
            <h2>🔗 SmartLink Tracker</h2>
            <div class="loader"></div>
            <p>Tracking your click... Redirecting to destination.</p>
            <p><small>You'll be redirected in 2 seconds</small></p>
            <p><a href="{result[0]}" style="color: white;">Click here if not redirected</a></p>
        </div>
        
        <meta http-equiv="refresh" content="2;url={result[0]}">
        """, unsafe_allow_html=True)
    else:
        st.error("❌ Link not found. Please check the URL.")