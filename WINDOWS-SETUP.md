# GdeDoctor Bot v2.0 - Windows Setup Guide

Telegram бот для поиска врачей в медицинских учреждениях Калуги.

## 🪟 Windows Installation

### 1. Prerequisites
- Python 3.9+ installed
- Git installed
- PowerShell 5.0+ (comes with Windows 10/11)

### 2. Quick Start (3 minutes)

```cmd
# Clone repository
git clone https://github.com/Syricoff/GdeDoctorBot.git
cd GdeDoctorBot

# Install dependencies
install.bat

# Configure environment
# Edit .env file with your tokens:
# - TELEGRAM_TOKEN=your_bot_token
# - YANDEX_API_KEY=your_yandex_key

# Run bot
run-bot.bat
```

### 3. Manual Installation

```cmd
# Install bot dependencies
cd bot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 🚀 Running the Bot

### Batch Scripts (Recommended)

| Script | Description |
|--------|-------------|
| `install.bat` | Install all dependencies |
| `run-bot.bat` | Start bot |
| `stop-all.bat` | Stop bot |

### PowerShell Commands

```powershell
# Import management module
Import-Module .\GdeDoctor-Management.psm1

# Install dependencies
Install-Dependencies

# Start bot
Start-Bot

# Check status
Get-Status

# Stop bot
Stop-All
```

### Manual Commands

```cmd
# Bot
cd bot
.venv\Scripts\activate
python -m app.main
```

## 📁 Project Structure

```
GdeDoctorBot/
├── bot/                    # Telegram bot
│   ├── app/
│   │   ├── handlers/      # Command handlers
│   │   ├── keyboards/     # Inline keyboards
│   │   ├── services/      # Data service
│   │   └── states/        # FSM states
│   ├── .venv/             # Virtual environment
│   └── requirements.txt
├── medical_data.db        # SQLite database
├── .env                   # Environment variables
├── install.bat           # Windows installer
├── run-bot.bat          # Bot runner
└── stop-all.bat         # Stop script
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# Telegram Bot
TELEGRAM_TOKEN=your_telegram_bot_token_here

# Yandex Maps API (для геокодирования)
YANDEX_API_KEY=your_yandex_api_key_here

# Database
DATABASE_PATH=medical_data.db
```

### Getting API Keys

1. **Telegram Bot Token:**
   - Message [@BotFather](https://t.me/BotFather)
   - Use `/newbot` command
   - Copy the token

2. **Yandex API Key:**
   - Register at [Yandex.Cloud](https://cloud.yandex.ru/)
   - Create API key for Maps (Geocoder API)

## 🌐 Access Points

- **Telegram Bot**: Find your bot in Telegram and use `/start`

## 🛠️ Development

### Virtual Environment

Bot has its own virtual environment:
- `bot/.venv/` - Bot dependencies

### Code Formatting

```cmd
# Format bot code
cd bot
.venv\Scripts\activate
ruff format app/
```

## 🐛 Troubleshooting

### Common Issues

1. **"Could not import module 'app.main'"**
   - Make sure you're in the bot directory
   - Use the provided batch scripts

2. **"No module named 'app.main'"**
   - Check virtual environment is activated
   - Verify you're in the bot directory

3. **"Token is invalid"**
   - Check TELEGRAM_TOKEN in .env file
   - Ensure token is valid and not expired

4. **"Cannot connect to host"**
   - Check internet connection
   - Verify firewall settings

### Service Management

```cmd
# Check running processes
tasklist | findstr python

# Stop specific process
taskkill /f /pid <process_id>

# Stop all Python processes
stop-all.bat
```

## 📚 Additional Resources

- [Quick Start Guide](QUICK_START.md)
- [Main README](README.md)

## 🤝 Support

If you encounter issues:
1. Check this Windows-specific guide
2. Review the main [README.md](README.md)
3. Check [troubleshooting section](#-troubleshooting)
4. Open an issue on GitHub

---

**Ready to use on Windows!** 🎉
