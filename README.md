# 🔗 SmartLink Tracker

**Advanced URL Shortener + Detailed Click Analytics** - Built for marketing campaigns, GHL, Facebook ads, webinars, and more.

![SmartLink Tracker](https://via.placeholder.com/800x400.png?text=SmartLink+Tracker+Demo)

## 📋 Features

### Core Functionality
- **URL Shortening** - Create short, trackable links from long URLs
- **Custom IDs** - Use memorable custom slugs (e.g., `summer-sale`)
- **UTM Builder** - Automatically add UTM parameters to track campaign sources
- **Click Tracking** - Track every click with detailed analytics

### Analytics Dashboard
- **Real-time Metrics** - Live click counts and statistics
- **Geographic Data** - Country and city-level location tracking
- **Device Detection** - Mobile vs Desktop vs Tablet breakdown
- **Browser & OS Stats** - See what browsers and operating systems your visitors use
- **Time Filters** - View data for Today, Last 7 days, Last 30 days, or All Time
- **Click Timeline** - Visual chart of clicks over time
- **Export Data** - Download click data as CSV

### Live Features
- **Live Click Feed** - See clicks in real-time as they happen
- **Auto-refresh** - Feed updates every 5 seconds
- **Redirect Tracking** - Smooth redirect with loading animation

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Step 1: Clone or Download
```bash
git clone https://github.com/yourusername/smartlink-tracker.git
cd smartlink-tracker
```

### Step 2: Install Dependencies
```bash
pip install streamlit sqlite3 requests pandas plotly user-agents
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 3: Run Locally
```bash
streamlit run app.py
```
The app will open at `http://localhost:8501`

## 📦 Dependencies

Create a `requirements.txt` file:
```txt
streamlit>=1.28.0
pandas>=2.0.0
requests>=2.31.0
plotly>=5.18.0
user-agents>=2.2.0
```

## 🎯 How to Use

### Creating a Short Link
1. Go to **"Create Short Link"** tab
2. Paste your long URL
3. (Optional) Add a custom ID
4. (Optional) Add UTM parameters
5. Click **"Generate Short Link"**
6. Copy your new tracking link!

### Viewing Analytics
1. Go to **"Analytics Dashboard"** tab
2. Select your link from the dropdown
3. View metrics, charts, and detailed click data
4. Export data as CSV if needed

### Live Monitoring
1. Go to **"Live Click Feed"** tab
2. Watch clicks appear in real-time
3. See device, location, and browser info instantly

## 🌐 Deployment

### Deploy to Streamlit Cloud (Free)

1. **Push code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/smartlink-tracker.git
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click **"New app"**
   - Select your repository
   - Set main file path to `app.py`
   - Click **"Deploy"**

3. **Update your app URL**
   - In your code, replace `YOUR-APP-NAME` with your actual Streamlit app name
   - Or use the auto-detection code included

### Environment Auto-Detection
The app automatically detects if it's running locally or on Streamlit Cloud:
```python
if os.getenv('STREAMLIT_SERVER_ADDRESS'):
    base_url = "https://your-app-name.streamlit.app"  # Update this!
else:
    base_url = "http://localhost:8501"
```

## 📊 Database Schema

### Links Table
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key, short link identifier |
| original_url | TEXT | Original long URL |
| clicks | INTEGER | Total click count |
| created_date | TEXT | Creation timestamp |
| custom_id | TEXT | User-provided custom ID |

### Clicks Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| link_id | TEXT | Foreign key to links table |
| timestamp | TEXT | Click timestamp |
| country | TEXT | Visitor country |
| city | TEXT | Visitor city |
| device_type | TEXT | Mobile/Tablet/Desktop |
| browser | TEXT | Browser name and version |
| os | TEXT | Operating system |
| ip | TEXT | IP address (anonymized) |
| referrer | TEXT | Traffic source |
| user_agent | TEXT | Full user agent string |

## 🔧 Troubleshooting

### Common Issues

**Q: I get "Module not found" errors**
A: Install missing packages: `pip install plotly user-agents`

**Q: Database errors about missing columns**
A: Delete the old database: `Remove-Item urls.db` (PowerShell) or `rm urls.db` (Mac/Linux)

**Q: Links show "App not found" when clicked**
A: You're using the Streamlit Cloud URL while testing locally. Use `http://localhost:8501` for local testing.

**Q: No geographic data showing**
A: The free IP API has rate limits. Wait a few minutes and try again.

## 📝 License

MIT License - feel free to use and modify for your own projects!

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 🙏 Credits

- Built with [Streamlit](https://streamlit.io)
- IP Geolocation by [ip-api.com](http://ip-api.com)
- Icons from Unicode/Emoji

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter) - email@example.com

Project Link: [https://github.com/yourusername/smartlink-tracker](https://github.com/yourusername/smartlink-tracker)

---

**⭐ Star this repo if you find it useful!**
