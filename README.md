
# 🤖 Orbit Lay-Odds Arbitrage Bot

A sophisticated, real-time football betting arbitrage detection system that monitors **Orbit LAY odds** against **Golbet odds** to identify profitable betting opportunities. The bot uses **OpenAI GPT-4** for intelligent analysis and sends **Telegram notifications** when arbitrage opportunities are detected.

## 🎯 **Core Concept**

The bot identifies arbitrage opportunities where:
- **Orbit LAY odds** ≤ **Golbet odds** 
- **Percentage difference** is within **-1% to +30%** threshold
- Only **football matches** with **1X2 markets** are analyzed
- **Real-time monitoring** every 60 seconds

## 🚀 **Quick Start**

### **Prerequisites**
- **Python 3.11+** (recommended)
- **Playwright** browser automation
- **OpenAI API key** for intelligent analysis
- **Telegram Bot Token** for notifications

### **Installation**

1. **Clone the repository:**
```bash
git clone <repository-url>
cd Orbit-Telegram-Bot
```

2. **Create virtual environment:**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install Playwright browsers:**
```bash
playwright install chromium
```

5. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your actual values
```

6. **Run the bot:**
```bash
python -m bot.main
```

## ⚙️ **Environment Configuration**

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Bot Settings
SCAN_INTERVAL_SECONDS=60
ALERT_DEDUPE_MINUTES=10

# Timezone (for notifications)
TZ=Asia/Tokyo
```

### **Required Environment Variables:**
- **`OPENAI_API_KEY`**: Your OpenAI API key for GPT-4 analysis
- **`TELEGRAM_BOT_TOKEN`**: Bot token from @BotFather
- **`TELEGRAM_CHAT_ID`**: Chat ID where notifications will be sent

### **Optional Settings:**
- **`SCAN_INTERVAL_SECONDS`**: How often to scan for opportunities (default: 60)
- **`ALERT_DEDUPE_MINUTES`**: Prevent duplicate alerts (default: 10)
- **`TZ`**: Timezone for timestamps (default: Asia/Tokyo)

## 🏗️ **Project Architecture**

```
Orbit-Telegram-Bot/
├── bot/
│   ├── core/                    # Core bot logic
│   │   ├── models.py           # Pydantic data models
│   │   ├── scheduler.py        # Main scheduling loop
│   │   ├── openai.py           # OpenAI GPT-4 integration
│   │   ├── notify.py           # Telegram notification system
│   │   └── dedupe.py          # Duplicate prevention
│   ├── sites/                  # Betting site scrapers
│   │   ├── orbit.py            # Orbit betting site scraper
│   │   └── golbet.py           # Golbet betting site scraper
│   └── main.py                 # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

## 🔧 **Core Components**

### **1. Data Models (`bot/core/models.py`)**
- **`OddsQuote`**: Individual odds with site, market, selection, and type (LAY/BACK)
- **`MarketSnapshot`**: Complete match data with multiple odds quotes

### **2. OpenAI Integration (`bot/core/openai.py`)**
- **GPT-4 Analysis**: Intelligent comparison of betting data
- **Threshold Filtering**: Only opportunities within -1% to +30% range
- **Structured Output**: JSON-formatted arbitrage opportunities

### **3. Notification System (`bot/core/notify.py`)**
- **Telegram Integration**: Rich HTML-formatted messages
- **Professional UI**: Beautiful formatting with emojis and sections
- **Error Handling**: Graceful fallbacks for parsing issues

### **4. Scheduler (`bot/core/scheduler.py`)**
- **Continuous Monitoring**: 60-second scan intervals
- **Data Validation**: Ensures data quality before analysis
- **Error Recovery**: Robust error handling and notifications

### **5. Deduplication (`bot/core/dedupe.py`)**
- **Smart Caching**: Prevents duplicate alerts
- **Configurable Window**: Adjustable deduplication timeframe

## 🌐 **Betting Site Scrapers**

### **Orbit Scraper (`bot/sites/orbit.py`)**
- **Advanced Browser Automation**: Uses Playwright with custom headers
- **Cookie Management**: Maintains session state
- **LAY Odds Extraction**: Focuses on pink box values
- **Football Filtering**: Only processes football matches
- **Smart Scrolling**: Efficient data collection

### **Golbet Scraper (`bot/sites/golbet.py`)**
- **Login Integration**: Automated authentication
- **Session Management**: Maintains logged-in state
- **Data Extraction**: Collects 1X2 market odds
- **Error Handling**: Graceful fallbacks for failures

## 📊 **Arbitrage Detection Logic**

### **Threshold System**
The bot only alerts on opportunities where:
```
-1% ≤ ((Golbet odds - Orbit LAY odds) / Orbit LAY odds) × 100 ≤ +30%
```

### **Examples:**
- **✅ Profitable**: Orbit LAY: 2.00, Golbet: 2.20 → **+10%** (INCLUDE)
- **✅ Small Risk**: Orbit LAY: 2.00, Golbet: 1.99 → **-0.5%** (INCLUDE)
- **❌ Too Risky**: Orbit LAY: 2.00, Golbet: 1.95 → **-2.5%** (EXCLUDE)
- **❌ Too Extreme**: Orbit LAY: 2.00, Golbet: 2.80 → **+40%** (EXCLUDE)

### **AI Analysis Process**
1. **Data Collection**: Scrape both betting sites
2. **Team Matching**: Identify same matches across sites
3. **Odds Comparison**: Calculate percentage differences
4. **Threshold Filtering**: Apply -1% to +30% criteria
5. **Opportunity Ranking**: Sort by profitability
6. **Notification**: Send formatted Telegram alerts

## 📱 **Telegram Notification Format**

### **Opportunity Alert Example:**
```
🎯 ARBITRAGE OPPORTUNITIES REPORT 🎯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 ANALYSIS SUMMARY
⏰ Time: 2024-01-15 14:30:25
🔍 Data Sources:
   • Orbit: 15 matches
   • Golbet: 12 matches

🎯 FILTERING CRITERIA
   • Percentage threshold: -1% to +30%
   • Only profitable opportunities within range

💰 FOUND 2 PROFITABLE OPPORTUNITIES 💰
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 OPPORTUNITY #1

⚽ Match: Arsenal vs Chelsea
🎲 Market: 1X2

📊 ODDS COMPARISON
   🔴 Orbit LAY: 2.50
   🟢 Golbet: 2.75

💵 PROFIT ANALYSIS
   💰 Difference: 0.25 (10.00%)
   ✅ Threshold Status: WITHIN RANGE
   💚 Profit Potential: +0.25 (+10.00%)

⏰ Detected: 2024-01-15 14:30:25
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 Powered by OpenAI GPT-4
⚡ Real-time monitoring active
🎯 Threshold filtering: -1% to +30%
🔄 Next scan in 60 seconds
```

## 🛠️ **Dependencies**

### **Core Requirements:**
- **`httpx`**: Async HTTP client for API calls
- **`pydantic`**: Data validation and serialization
- **`python-dotenv`**: Environment variable management
- **`playwright`**: Browser automation for scraping
- **`beautifulsoup4`**: HTML parsing
- **`openai`**: OpenAI API integration

### **System Requirements:**
- **Chromium Browser**: Installed via Playwright
- **Network Access**: To betting sites and OpenAI API
- **Memory**: Minimum 2GB RAM for browser automation

## 🔒 **Security & Privacy**

### **Data Protection:**
- **No Hardcoded Credentials**: All sensitive data in environment variables
- **Secure Scraping**: Uses legitimate browser automation
- **Rate Limiting**: Respects site policies and API limits

### **Best Practices:**
- **Environment Variables**: Never commit `.env` files
- **API Key Rotation**: Regularly update OpenAI API keys
- **Access Control**: Limit Telegram bot access to authorized users

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **Playwright Installation:**
```bash
playwright install chromium
```

2. **Environment Variables:**
```bash
# Check if .env file exists and has correct values
cat .env
```

3. **Dependencies:**
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

4. **Browser Issues:**
```bash
# Clear Playwright cache
playwright install --force
```

### **Debug Mode:**
Set `headless=False` in scraper files to see browser automation in action.

## 📈 **Performance & Scaling**

### **Current Capabilities:**
- **Scan Interval**: 60 seconds (configurable)
- **Data Sources**: 2 betting sites
- **Market Types**: Football 1X2 markets
- **Notification**: Real-time Telegram alerts

### **Optimization Tips:**
- **Adjust Scan Intervals**: Balance between responsiveness and resource usage
- **Browser Resources**: Monitor memory usage during long runs
- **Network Latency**: Consider proxy usage for better performance

## 🔮 **Future Enhancements**

### **Planned Features:**
- **Multiple Betting Sites**: Expand beyond Orbit and Golbet
- **Advanced Markets**: Over/Under, Correct Score markets
- **Historical Analysis**: Track opportunity patterns over time
- **Risk Management**: Advanced filtering and scoring systems
- **Web Dashboard**: Real-time monitoring interface

### **Integration Possibilities:**
- **Betting APIs**: Direct integration with bookmaker APIs
- **Database Storage**: Persistent opportunity tracking
- **Machine Learning**: Enhanced pattern recognition
- **Mobile App**: Push notifications and mobile interface

## 📄 **License & Disclaimer**

### **Legal Notice:**
This bot is for **educational and research purposes only**. Users are responsible for:
- **Compliance** with local gambling laws
- **Verification** of betting site terms of service
- **Risk Assessment** of any betting decisions
- **Financial Responsibility** for any losses

### **Terms of Use:**
- **No Warranty**: Use at your own risk
- **No Guarantees**: Past performance doesn't predict future results
- **Educational Purpose**: Intended for learning about arbitrage concepts

## 🤝 **Contributing**

### **Development Setup:**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### **Code Standards:**
- **Type Hints**: Use Python type annotations
- **Documentation**: Add docstrings for new functions
- **Error Handling**: Implement proper exception handling
- **Testing**: Include tests for new features

## 📞 **Support & Contact**

### **Getting Help:**
- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Documentation**: Check this README first

### **Community:**
- **Telegram Group**: Join our community chat
- **Discord Server**: Real-time support and discussions
- **Email Support**: For business inquiries

---

## 🎉 **Getting Started Checklist**

- [ ] Install Python 3.11+
- [ ] Clone the repository
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Install Playwright browsers
- [ ] Copy `.env.example` to `.env`
- [ ] Add your OpenAI API key
- [ ] Add your Telegram bot token
- [ ] Add your Telegram chat ID
- [ ] Test the installation
- [ ] Run the bot: `python -m bot.main`

**Happy arbitrage hunting! 🚀💰**
