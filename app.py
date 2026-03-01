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
# ENHANCED UI/UX - High Contrast & Professional
# ============================================================================

st.markdown("""
<style>
    /* ===== ENHANCED COLOR PALETTE - High Contrast ===== */
    :root {
        --primary: #1a365d;
        --primary-light: #2c5282;
        --primary-dark: #0f2b4b;
        --accent: #3182ce;
        --accent-light: #4299e1;
        --accent-dark: #2b6cb0;
        --success: #2f855a;
        --warning: #dd6b20;
        --danger: #c53030;
        
        --bg-main: #ffffff;
        --bg-light: #f7fafc;
        --bg-card: #ffffff;
        --bg-hover: #ebf8ff;
        
        --text-primary: #1a202c;
        --text-secondary: #2d3748;
        --text-tertiary: #4a5568;
        --text-muted: #718096;
        --text-white: #ffffff;
        --text-link: #3182ce;
        --text-link-hover: #2c5282;
        
        --border-light: #e2e8f0;
        --border-medium: #cbd5e0;
        --border-focus: #3182ce;
        
        --shadow-sm: 0 2px 4px rgba(0,0,0,0.02);
        --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1);
        --shadow-focus: 0 0 0 3px rgba(49, 130, 206, 0.3);
        
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        
        --transition: all 0.2s ease;
    }

    /* ===== GLOBAL STYLES ===== */
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        box-sizing: border-box;
    }

    .stApp {
        background: var(--bg-light);
    }

    /* ===== TYPOGRAPHY - Enhanced Readability ===== */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        line-height: 1.3 !important;
        margin-bottom: 1rem !important;
    }

    h1 { font-size: 2.5rem !important; }
    h2 { font-size: 2rem !important; }
    h3 { font-size: 1.5rem !important; }
    h4 { font-size: 1.25rem !important; }

    p, li, span, div {
        color: var(--text-secondary) !important;
        line-height: 1.6 !important;
        font-size: 1rem !important;
    }

    small, .small-text {
        color: var(--text-tertiary) !important;
        font-size: 0.875rem !important;
    }

    /* ===== HEADER - Professional & Clean ===== */
    .professional-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        padding: 2.5rem 2rem;
        border-radius: var(--radius-lg);
        margin-bottom: 2rem;
        box-shadow: var(--shadow-lg);
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
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 100%);
        pointer-events: none;
    }

    .professional-header h1 {
        color: var(--text-white) !important;
        font-size: 2.5rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .professional-header p {
        color: rgba(255, 255, 255, 0.95) !important;
        font-size: 1.2rem !important;
        margin: 0.5rem 0 0 0 !important;
        position: relative;
        z-index: 1;
        font-weight: 400;
    }

    .domain-badge {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        padding: 0.75rem 2rem;
        border-radius: 100px;
        display: inline-flex;
        align-items: center;
        gap: 0.75rem;
        margin-top: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: var(--text-white) !important;
        font-size: 1.1rem;
        font-weight: 500;
        position: relative;
        z-index: 1;
        transition: var(--transition);
    }

    .domain-badge:hover {
        background: rgba(255, 255, 255, 0.25);
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }

    .domain-badge strong {
        color: var(--text-white) !important;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.25);
        padding: 0.35rem 1rem;
        border-radius: 50px;
        font-family: 'SF Mono', 'Monaco', monospace;
        font-size: 1rem;
    }

    /* ===== CARDS - Enhanced Visibility ===== */
    .professional-card {
        background: var(--bg-card);
        padding: 1.75rem;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-md);
        margin: 1.25rem 0;
        border: 1px solid var(--border-light);
        transition: var(--transition);
    }

    .professional-card:hover {
        box-shadow: var(--shadow-lg);
        border-color: var(--border-medium);
        transform: translateY(-2px);
    }

    .professional-card h4 {
        color: var(--text-primary) !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin: 0 0 1.25rem 0 !important;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--border-light);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .professional-card h4::before {
        content: '📌';
        font-size: 1.2rem;
        opacity: 0.8;
    }

    .professional-card p {
        color: var(--text-secondary) !important;
        margin: 0.75rem 0 !important;
        font-size: 1rem !important;
    }

    .professional-card strong {
        color: var(--text-primary) !important;
        font-weight: 600;
        font-size: 1rem;
    }

    .professional-card a {
        color: var(--text-link);
        text-decoration: none;
        font-weight: 500;
        transition: var(--transition);
        border-bottom: 1px solid transparent;
    }

    .professional-card a:hover {
        color: var(--text-link-hover);
        border-bottom-color: var(--text-link-hover);
    }

    /* ===== URL DISPLAY - High Contrast ===== */
    .url-container {
        background: var(--bg-light);
        padding: 1.75rem;
        border-radius: var(--radius-md);
        border: 2px solid var(--border-light);
        margin: 1.25rem 0;
        transition: var(--transition);
    }

    .url-container:hover {
        border-color: var(--border-focus);
        background: var(--bg-hover);
    }

    .short-url {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .short-url a {
        background: var(--accent);
        color: var(--text-white) !important;
        text-decoration: none;
        padding: 0.75rem 1.5rem;
        border-radius: var(--radius-sm);
        font-size: 1.2rem;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 0.75rem;
        transition: var(--transition);
        border: none;
        box-shadow: var(--shadow-md);
    }

    .short-url a:hover {
        background: var(--accent-dark);
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }

    .short-url a::before {
        content: '🔗';
        font-size: 1.3rem;
    }

    .copy-btn {
        background: white;
        border: 2px solid var(--border-medium);
        color: var(--text-secondary) !important;
        padding: 0.75rem 1.5rem;
        border-radius: var(--radius-sm);
        cursor: pointer;
        font-size: 1rem;
        font-weight: 500;
        transition: var(--transition);
        display: inline-flex;
        align-items: center;
        gap: 0.75rem;
    }

    .copy-btn:hover {
        background: var(--accent);
        border-color: var(--accent);
        color: var(--text-white) !important;
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

    .copy-btn::before {
        content: '📋';
        font-size: 1.2rem;
    }

    .original-url {
        color: var(--text-tertiary) !important;
        font-size: 0.95rem;
        word-break: break-all;
        padding: 1rem 1.25rem;
        background: white;
        border-radius: var(--radius-sm);
        border: 2px dashed var(--border-light);
        margin-top: 1rem;
        line-height: 1.5;
    }

    .original-url::before {
        content: '📎 Original: ';
        font-weight: 600;
        color: var(--text-secondary);
    }

    /* ===== METRIC CARDS - Better Visibility ===== */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.25rem;
        margin: 2rem 0;
    }

    .metric-card {
        background: var(--bg-card);
        padding: 1.75rem;
        border-radius: var(--radius-md);
        text-align: center;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary), var(--accent));
    }

    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-lg);
        border-color: var(--border-medium);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary) !important;
        line-height: 1.2;
        margin-bottom: 0.5rem;
    }

    .metric-label {
        color: var(--text-tertiary) !important;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        font-weight: 600;
    }

    /* ===== CLICK CARDS - Enhanced ===== */
    .click-card {
        background: var(--bg-card);
        padding: 1.5rem;
        border-radius: var(--radius-sm);
        margin: 1rem 0;
        border: 1px solid var(--border-light);
        border-left: 4px solid var(--accent);
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
        animation: slideIn 0.3s ease-out;
    }

    .click-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateX(4px);
        border-left-width: 6px;
        background: var(--bg-hover);
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
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
        margin-bottom: 1rem;
    }

    .click-card-code {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary) !important;
    }

    .click-card-code a {
        color: var(--text-link);
        text-decoration: none;
        font-weight: 600;
        transition: var(--transition);
    }

    .click-card-code a:hover {
        color: var(--text-link-hover);
        text-decoration: underline;
    }

    .click-card-time {
        color: var(--text-tertiary) !important;
        font-size: 0.9rem;
        font-weight: 500;
        background: var(--bg-light);
        padding: 0.35rem 1rem;
        border-radius: 50px;
        border: 1px solid var(--border-light);
    }

    .click-card-details {
        display: flex;
        gap: 2rem;
        flex-wrap: wrap;
    }

    .click-card-details span {
        color: var(--text-secondary) !important;
        font-size: 0.95rem;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: var(--bg-light);
        padding: 0.4rem 1rem;
        border-radius: 50px;
        border: 1px solid var(--border-light);
    }

    /* ===== SUCCESS BOX ===== */
    .success-box {
        background: #f0fff4;
        padding: 2.5rem;
        border-radius: var(--radius-md);
        border: 2px solid var(--success);
        margin: 2rem 0;
        box-shadow: var(--shadow-md);
    }

    .success-box h3 {
        color: var(--success) !important;
        font-size: 1.8rem !important;
        margin: 0 0 1.5rem 0 !important;
        font-weight: 600 !important;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .success-box h3::before {
        content: '✅';
        font-size: 2rem;
    }

    .success-box p {
        color: var(--text-secondary) !important;
        font-size: 1rem !important;
    }

    .success-box strong {
        color: var(--text-primary) !important;
        font-weight: 600;
    }

    .success-box code {
        background: #e6fffa;
        color: var(--success) !important;
        padding: 0.3rem 0.8rem;
        border-radius: var(--radius-sm);
        font-weight: 600;
        border: 1px solid var(--success);
        font-size: 1rem;
    }

    /* ===== INFO BOX ===== */
    .info-box {
        background: #ebf8ff;
        padding: 1.25rem 2rem;
        border-radius: var(--radius-sm);
        border-left: 4px solid var(--accent);
        color: var(--text-secondary) !important;
        margin: 1.25rem 0;
        font-weight: 500;
        border: 1px solid #bee3f8;
    }

    /* ===== FORM ELEMENTS - Enhanced ===== */
    .stTextInput > div > div > input {
        border: 2px solid var(--border-light) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.75rem 1.25rem !important;
        font-size: 1rem !important;
        transition: var(--transition) !important;
        background: white !important;
        color: var(--text-primary) !important;
    }

    .stTextInput > div > div > input:hover {
        border-color: var(--border-medium) !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--border-focus) !important;
        box-shadow: var(--shadow-focus) !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: var(--text-muted) !important;
        font-size: 0.95rem;
    }

    .stSelectbox > div > div > div {
        border: 2px solid var(--border-light) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.5rem !important;
        color: var(--text-primary) !important;
    }

    .stSelectbox:hover > div > div > div {
        border-color: var(--border-medium) !important;
    }

    /* ===== BUTTONS - Professional ===== */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%) !important;
        color: var(--text-white) !important;
        border: none !important;
        padding: 0.75rem 2.5rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        border-radius: var(--radius-sm) !important;
        transition: var(--transition) !important;
        width: 100%;
        box-shadow: var(--shadow-md) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
        background: linear-gradient(135deg, var(--accent-dark) 0%, var(--accent) 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ===== TABS - Clean ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2.5rem;
        background: transparent;
        padding: 0;
        border-bottom: 2px solid var(--border-light);
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 0;
        font-weight: 600;
        color: var(--text-tertiary) !important;
        font-size: 1.1rem;
        transition: var(--transition);
        margin-bottom: -2px;
    }

    .stTabs [aria-selected="true"] {
        color: var(--accent) !important;
        border-bottom: 3px solid var(--accent) !important;
        font-weight: 600;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
    }

    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: var(--bg-light) !important;
        border: 2px solid var(--border-light) !important;
        border-radius: var(--radius-sm) !important;
        padding: 1rem 1.5rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        transition: var(--transition) !important;
        font-size: 1rem !important;
    }

    .streamlit-expanderHeader:hover {
        border-color: var(--border-focus) !important;
        background: var(--bg-hover) !important;
    }

    .streamlit-expanderContent {
        border: 2px solid var(--border-light) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-sm) var(--radius-sm) !important;
        padding: 2rem !important;
        background: white;
    }

    /* ===== DATAFRAMES ===== */
    .stDataFrame {
        border: 2px solid var(--border-light) !important;
        border-radius: var(--radius-sm) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stDataFrame th {
        background: var(--bg-light) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        font-size: 0.95rem !important;
        border-bottom: 2px solid var(--border-light) !important;
    }

    .stDataFrame td {
        color: var(--text-secondary) !important;
        padding: 0.9rem 1rem !important;
        font-size: 0.95rem !important;
        border-bottom: 1px solid var(--border-light) !important;
    }

    .stDataFrame tr:hover td {
        background: var(--bg-hover) !important;
    }

    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton > button {
        background: white !important;
        color: var(--accent) !important;
        border: 2px solid var(--accent) !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        border-radius: var(--radius-sm) !important;
        transition: var(--transition) !important;
        width: 100%;
        font-size: 1rem !important;
    }

    .stDownloadButton > button:hover {
        background: var(--accent) !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-md) !important;
    }

    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        padding: 3rem 2rem 1.5rem;
        color: var(--text-muted) !important;
        font-size: 0.9rem;
        border-top: 2px solid var(--border-light);
        margin-top: 4rem;
        background: white;
        border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    }

    .footer span {
        color: var(--text-tertiary) !important;
        font-weight: 500;
    }

    .footer-dot {
        color: var(--accent) !important;
        font-size: 1.2rem;
        margin: 0 0.75rem;
        font-weight: 700;
    }

    /* ===== RADIO BUTTONS ===== */
    .stRadio > div {
        background: white;
        padding: 0.75rem;
        border-radius: var(--radius-sm);
        border: 2px solid var(--border-light);
        transition: var(--transition);
    }

    .stRadio:hover > div {
        border-color: var(--border-medium);
    }

    .stRadio label {
        color: var(--text-secondary) !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }

    /* ===== METRICS ===== */
    [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-size: 2.2rem !important;
        font-weight: 600 !important;
        line-height: 1.2;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-tertiary) !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    /* ===== TOOLTIPS ===== */
    [data-testid="stTooltip"] {
        background: var(--primary-dark) !important;
        color: var(--text-white) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.75rem 1.25rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        box-shadow: var(--shadow-lg) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }

    /* ===== PLOTLY CHARTS ===== */
    .js-plotly-plot {
        border-radius: var(--radius-sm);
        background: white;
        padding: 1rem;
        border: 2px solid var(--border-light);
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
    }

    .js-plotly-plot:hover {
        border-color: var(--border-medium);
        box-shadow: var(--shadow-md);
    }

    /* ===== PROGRESS BARS ===== */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--accent) 0%, var(--primary-light) 100%) !important;
        border-radius: var(--radius-sm) !important;
    }

    /* ===== ALERTS ===== */
    .stAlert {
        border-radius: var(--radius-sm) !important;
        border: 2px solid transparent !important;
        box-shadow: var(--shadow-md) !important;
        padding: 1.25rem 1.5rem !important;
        font-weight: 500 !important;
    }

    .stAlert > div {
        color: var(--text-primary) !important;
    }

    /* ===== SPINNERS ===== */
    .stSpinner > div {
        border-color: var(--accent) transparent transparent transparent !important;
    }

    /* ===== SCROLLBARS ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-light);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border-medium);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# PROFESSIONAL HEADER - Enhanced
# ============================================================================
APP_URL = "https://smartlink-tracker.streamlit.app"

st.markdown(f"""
<div class="professional-header">
    <h1>🔗 URL Shortener & Analytics</h1>
    <p>Create short links and track every click with precision</p>
    <div class="domain-badge">
        <span>✨ Your branded domain</span>
        <strong>yourbrand.com/<span style="font-weight:400;">[your-code]</span></strong>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# DATABASE SETUP (Same as before - keep your existing database code)
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
# ACCURATE IP AND GEOLOCATION FUNCTIONS (Same as before)
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
# ACCURATE TIME FUNCTIONS (Same as before)
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
# TAB 1: Create Short Link (Enhanced)
# ============================================================================
with tab1:
    st.markdown("### ✨ Create New Short Link")
    st.markdown("*Generate short, trackable links for your campaigns*")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("create_link"):
            # Main URL input
            url = st.text_input(
                "Enter your long URL",
                placeholder="https://example.com/very/long/path?with=parameters",
                help="Paste the URL you want to shorten and track"
            )
            
            # Advanced options
            with st.expander("⚙️ Advanced Options", expanded=False):
                col_a, col_b = st.columns(2)
                with col_a:
                    custom_code = st.text_input(
                        "Custom short code (optional)",
                        placeholder="my-campaign",
                        help="Choose a memorable short code (letters, numbers, hyphens only)"
                    )
                with col_b:
                    expires_in = st.selectbox(
                        "Link expiration",
                        ["Never", "7 days", "30 days", "90 days"],
                        index=0,
                        help="Set when this link should automatically expire"
                    )
                
                st.markdown("##### 📊 UTM Campaign Parameters")
                st.markdown("*Track your marketing campaigns*")
                col_c, col_d, col_e = st.columns(3)
                with col_c:
                    utm_source = st.text_input(
                        "Source", 
                        placeholder="facebook",
                        help="Campaign source (e.g., facebook, newsletter)"
                    )
                with col_d:
                    utm_medium = st.text_input(
                        "Medium", 
                        placeholder="social",
                        help="Campaign medium (e.g., social, email)"
                    )
                with col_e:
                    utm_campaign = st.text_input(
                        "Campaign", 
                        placeholder="summer2024",
                        help="Campaign name (e.g., summer_sale)"
                    )
            
            submit = st.form_submit_button("🚀 Generate Short Link", use_container_width=True)
            
            if submit and url:
                # Validate and clean URL
                url = validate_url(url)
                
                # Add UTM parameters
                if utm_source or utm_medium or utm_campaign:
                    separator = '&' if '?' in url else '?'
                    utm_parts = []
                    if utm_source:
                        utm_parts.append(f"utm_source={utm_source.replace(' ', '_')}")
                    if utm_medium:
                        utm_parts.append(f"utm_medium={utm_medium.replace(' ', '_')}")
                    if utm_campaign:
                        utm_parts.append(f"utm_campaign={utm_campaign.replace(' ', '_')}")
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
                                <p><strong>Status:</strong> <span style="color: #2f855a; font-weight:600;">Active</span></p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.balloons()
                    
                except sqlite3.IntegrityError:
                    st.error("❌ This short code is already taken. Please try another one.")
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
    
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
                <div class="metric-value">{total_links:,}</div>
                <div class="metric-label">Total Links</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{total_clicks:,}</div>
                <div class="metric-label">Total Clicks</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{active_links:,}</div>
                <div class="metric-label">Active Links</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{((total_clicks/total_links)*100 if total_links > 0 else 0):.1f}%</div>
                <div class="metric-label">CTR</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# TAB 2: Analytics Dashboard (Enhanced)
# ============================================================================
with tab2:
    st.markdown("### 📊 Analytics Dashboard")
    st.markdown("*Detailed insights for your shortened links*")
    
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
            display_name = f"🔗 {link[0]} ({link[3]:,} click{'s' if link[3] != 1 else ''})"
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
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem;">
                    <div>
                        <p><strong>Short Code:</strong> <code>{short_code}</code></p>
                        <p><strong>Short URL:</strong> <a href="{APP_URL}/?go={short_code}" target="_blank">Open Link ↗</a></p>
                    </div>
                    <div>
                        <p><strong>Created:</strong> {created_display}</p>
                        <p><strong>Total Clicks:</strong> {link[4] if len(link) > 4 else 0:,}</p>
                    </div>
                </div>
                <p><strong>Original URL:</strong> <a href="{link[1]}" target="_blank">{link[1][:80]}{'...' if len(link[1]) > 80 else ''}</a></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Time range filter
            st.markdown("##### 📅 Select Time Range")
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
            clicks_data = []
            try:
                if start_date:
                    c.execute("""
                        SELECT * FROM clicks 
                        WHERE short_code=? AND timestamp >= ? 
                        ORDER BY timestamp DESC
                    """, (short_code, start_date))
                else:
                    c.execute("SELECT * FROM clicks WHERE short_code=? ORDER BY timestamp DESC", (short_code,))
                clicks_data = c.fetchall()
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
                        clicks_data = c.fetchall()
                except:
                    clicks_data = []
            
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
                st.markdown("##### 📊 Key Metrics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{len(df):,}</div>
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
                        <div class="metric-value">{unique_visitors:,}</div>
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
                st.markdown("##### 📈 Visual Analytics")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("###### Clicks Over Time")
                    if 'timestamp' in df.columns and not df.empty:
                        # Convert timestamp strings to datetime objects safely
                        df['timestamp_dt'] = pd.to_datetime(df['timestamp'], errors='coerce')
                        # Drop rows with invalid timestamps
                        df_clean = df.dropna(subset=['timestamp_dt'])
                        
                        if not df_clean.empty:
                            # Extract date safely
                            df_clean['date'] = df_clean['timestamp_dt'].dt.date
                            timeline = df_clean.groupby('date').size().reset_index(name='count')
                            
                            if not timeline.empty:
                                fig = px.line(timeline, x='date', y='count', markers=True)
                                fig.update_layout(
                                    height=350,
                                    margin=dict(l=40, r=40, t=40, b=40),
                                    hovermode='x unified',
                                    plot_bgcolor='white',
                                    paper_bgcolor='white',
                                    title="Click Timeline"
                                )
                                fig.update_traces(line_color='#3182ce', marker_color='#3182ce', line_width=3)
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("No timeline data available")
                        else:
                            st.info("No valid timestamp data")
                    else:
                        st.info("No timeline data available")
                
                with col2:
                    st.markdown("###### Top Countries")
                    if 'country' in df.columns:
                        # Filter out unknown countries
                        countries = df[df['country'] != 'Unknown']['country'].value_counts().head(10)
                        if not countries.empty:
                            fig = px.bar(
                                x=countries.values, 
                                y=countries.index, 
                                orientation='h',
                                labels={'x': 'Clicks', 'y': 'Country'}
                            )
                            fig.update_layout(
                                height=350,
                                margin=dict(l=40, r=40, t=40, b=40),
                                showlegend=False,
                                plot_bgcolor='white',
                                paper_bgcolor='white',
                                title="Click Distribution by Country"
                            )
                            fig.update_traces(marker_color='#3182ce')
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No country data available")
                    else:
                        st.info("No country data available")
                
                # Second row of charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("###### Device Types")
                    if 'device_type' in df.columns:
                        devices = df['device_type'].value_counts()
                        if not devices.empty:
                            fig = px.pie(
                                values=devices.values, 
                                names=devices.index, 
                                hole=0.4,
                                title="Device Breakdown"
                            )
                            fig.update_layout(
                                height=350,
                                margin=dict(l=40, r=40, t=60, b=40),
                                plot_bgcolor='white',
                                paper_bgcolor='white'
                            )
                            fig.update_traces(marker=dict(colors=['#3182ce', '#2c3e50', '#2f855a']))
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No device data available")
                    else:
                        st.info("No device data available")
                
                with col2:
                    st.markdown("###### Top Browsers")
                    if 'browser' in df.columns:
                        browsers = df[df['browser'] != 'Unknown']['browser'].value_counts().head(5)
                        if not browsers.empty:
                            fig = px.bar(
                                x=browsers.values, 
                                y=browsers.index, 
                                orientation='h',
                                labels={'x': 'Clicks', 'y': 'Browser'}
                            )
                            fig.update_layout(
                                height=350,
                                margin=dict(l=40, r=40, t=60, b=40),
                                showlegend=False,
                                plot_bgcolor='white',
                                paper_bgcolor='white',
                                title="Browser Distribution"
                            )
                            fig.update_traces(marker_color='#2f855a')
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
                        st.map(map_df[['latitude', 'longitude']], zoom=1, use_container_width=True)
                
                # Detailed data
                st.markdown("##### 📋 Recent Clicks")
                display_cols = ['display_time' if 'display_time' in df.columns else 'timestamp']
                display_cols.append('country') if 'country' in df.columns else None
                display_cols.append('city') if 'city' in df.columns else None
                display_cols.append('device_type') if 'device_type' in df.columns else None
                display_cols.append('browser') if 'browser' in df.columns else None
                display_cols.append('os') if 'os' in df.columns else None
                
                if display_cols:
                    display_df = df[display_cols].head(100)
                    if 'display_time' in display_df.columns:
                        display_df = display_df.rename(columns={'display_time': 'Time'})
                    st.dataframe(display_df, use_container_width=True)
                
                # Export
                st.markdown("##### 📥 Export Data")
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Download Full Data as CSV",
                    csv,
                    f"{short_code}_analytics.csv",
                    "text/csv",
                    use_container_width=True
                )
                
            else:
                st.info("📭 No clicks recorded for this link yet. Share your link to start tracking!")
    else:
        st.info("👋 No links created yet. Go to the 'Create Short Link' tab to create your first tracking link!")

# ============================================================================
# TAB 3: Live Click Feed (Enhanced)
# ============================================================================
with tab3:
    st.markdown("### 🔴 Live Click Feed")
    st.markdown("*Watch clicks happen in real-time across all your links*")
    
    # Add auto-refresh option
    auto_refresh = st.checkbox("Auto-refresh (every 10 seconds)", value=True)
    
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
        st.markdown(f"*Showing {len(recent)} most recent clicks*")
        
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
                    minutes = int(time_diff.total_seconds()/60)
                    time_str = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
                elif time_diff.total_seconds() < 86400:
                    hours = int(time_diff.total_seconds()/3600)
                    time_str = f"{hours} hour{'s' if hours != 1 else ''} ago"
                else:
                    days = int(time_diff.total_seconds()/86400)
                    time_str = f"{days} day{'s' if days != 1 else ''} ago"
            except:
                time_str = "recently"
            
            st.markdown(f"""
            <div class="click-card">
                <div class="click-card-header">
                    <span class="click-card-code">🔗 <a href="{APP_URL}/?go={code}" target="_blank">{code}</a></span>
                    <span class="click-card-time">{time_str}</span>
                </div>
                <div class="click-card-details">
                    <span>🌍 {country}{f' · {city}' if city and city != 'Unknown' else ''}</span>
                    <span>📱 {device}</span>
                    <span>🌐 {browser}</span>
                    <span>💻 {os}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if auto_refresh:
            st.caption("🔄 Page will auto-refresh every 10 seconds")
            time.sleep(10)
            st.rerun()
        else:
            st.caption("🔄 Refresh the page to see new clicks")
    else:
        st.info("📭 No clicks recorded yet. Share your links to start tracking!")

# ============================================================================
# FIXED REDIRECT HANDLER - This runs when someone clicks a short link
# ============================================================================
short_code = None

if 'go' in st.query_params:
    short_code = st.query_params['go']
elif 'id' in st.query_params:
    short_code = st.query_params['id']

# IMPORTANT: This must run before any other UI elements
if short_code:
    try:
        # Try to get by short_code first
        c.execute("SELECT id, original_url, clicks FROM links WHERE short_code=?", (short_code,))
        result = c.fetchone()
        
        # If not found, try by id (for backward compatibility)
        if not result:
            c.execute("SELECT id, original_url, clicks FROM links WHERE id=?", (short_code,))
            result = c.fetchone()
        
        if result:
            link_id = result[0]
            original_url = result[1]
            current_clicks = result[2]
            
            # Get accurate geolocation
            geo_data = get_accurate_geo_info()
            
            # Parse user agent
            user_agent_string = st.query_params.get('user_agent', 'Unknown')
            ua_info = parse_user_agent_accurate(user_agent_string)
            
            # Get local time for click timestamp
            click_time = get_local_time()
            
            # Generate session ID for unique visitor tracking
            session_id = hashlib.md5(
                f"{geo_data['ip']}{short_code}{datetime.now().strftime('%Y-%m-%d')}".encode()
            ).hexdigest()
            
            # Get referrer
            referrer = st.query_params.get('referrer', 'Direct')
            
            # ===== RECORD THE CLICK =====
            try:
                # Insert click record
                c.execute("""
                    INSERT INTO clicks (
                        link_id, short_code, timestamp, ip_address, country, city, 
                        device_type, browser, os, referrer, user_agent, session_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    link_id, short_code, click_time, geo_data['ip'],
                    geo_data['country'], geo_data['city'],
                    ua_info['device_type'], ua_info['browser'],
                    ua_info['os'], referrer, user_agent_string, session_id
                ))
                
                # Update click count in links table
                c.execute("UPDATE links SET clicks = clicks + 1 WHERE id = ?", (link_id,))
                conn.commit()
                
                print(f"✅ Click recorded for {short_code} - Total clicks: {current_clicks + 1}")
                
            except Exception as e:
                print(f"Error recording click: {e}")
                conn.rollback()
            
            # ===== REDIRECT TO ORIGINAL URL =====
            # Use HTML meta refresh for reliable redirect
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
                        background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
                        color: white;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }}
                    .container {{
                        text-align: center;
                        padding: 2rem;
                        max-width: 500px;
                    }}
                    .card {{
                        background: rgba(255, 255, 255, 0.1);
                        backdrop-filter: blur(10px);
                        padding: 2rem;
                        border-radius: 12px;
                        margin: 2rem 0;
                        border: 1px solid rgba(255,255,255,0.2);
                    }}
                    .loader {{
                        width: 48px;
                        height: 48px;
                        border: 4px solid rgba(255,255,255,0.3);
                        border-top: 4px solid white;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                        margin: 2rem auto;
                    }}
                    @keyframes spin {{
                        0% {{ transform: rotate(0deg); }}
                        100% {{ transform: rotate(360deg); }}
                    }}
                    .location {{
                        display: flex;
                        justify-content: center;
                        gap: 1.5rem;
                        margin: 1rem 0;
                        font-size: 1.1rem;
                    }}
                    .details {{
                        color: rgba(255,255,255,0.9);
                        font-size: 0.95rem;
                        margin-top: 0.5rem;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 style="font-size: 4rem; margin:0;">🔗</h1>
                    <h2 style="font-weight:400; margin:0.5rem 0;">URL Shortener</h2>
                    <div class="card">
                        <div class="location">
                            <span>🌍 {geo_data['country']}</span>
                            <span>📱 {ua_info['device_type']}</span>
                        </div>
                        <div class="details">
                            {geo_data['city'] if geo_data['city'] != 'Unknown' else ''} · {ua_info['browser']}
                        </div>
                    </div>
                    <div class="loader"></div>
                    <p style="font-size:1.2rem;">Redirecting you to your destination...</p>
                    <p style="opacity:0.8; font-size:0.9rem;">Click tracked successfully</p>
                </div>
            </body>
            </html>
            """
            
            # Clear any existing content and show redirect page
            st.markdown(html_content, unsafe_allow_html=True)
            
            # Stop further Streamlit execution
            st.stop()
            
        else:
            st.error("❌ Link not found. Please check the URL.")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
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
    <span class="footer-dot">•</span>
    <span>Real-time Tracking</span>
</div>
""", unsafe_allow_html=True)