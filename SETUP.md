# ULP Bot Setup Guide

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- A Telegram Bot Token (from @BotFather)
- A hosting server or local machine

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/mdump0538-cpu/ulp-bot.git
cd ulp-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Bot

Edit `config.json` and add your bot token:

```json
{
  "bot_token": "YOUR_TELEGRAM_BOT_TOKEN_HERE",
  "admin_ids": [123456789],
  "database_path": "database/ulp_bot.db",
  "inventory_path": "inventory/",
  "logs_path": "logs/",
  "search_cost": 1,
  "generation_cost": 2,
  "daily_search_limit": 100,
  "daily_generation_limit": 50,
  "max_file_size": 52428800,
  "cooldown_seconds": 5,
  "maintenance_mode": false
}
```

### 4. Create Necessary Directories

```bash
mkdir -p database
mkdir -p inventory
mkdir -p logs
mkdir -p exports
```

### 5. Add Inventory Files

Place your ULP files (.txt) in the `inventory/` directory:

```bash
cp your_ulp_file.txt inventory/
```

### 6. Run the Bot

```bash
python main.py
```

## Getting Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Follow the instructions to create your bot
4. Copy the token and paste it in `config.json`

## ULP Format Support

The bot supports multiple ULP formats:

### Standard Format
```
authenticate.riotgames.com:UltrAmAgil:Caminando12
```

### HTTPS Format
```
https://jshsjja.com:example:example
```

### Android/Custom Scheme Format
```
android://qC14t1Ub7KIS36fonnrWkpRA6OyZuOHIwtt-oIfaTa4yCdydz9zArLhfxPHaVvpMBIVi3ECOZHmHI1SdAg==@com.lf.lfvtandroid/:Felicia.Beijer2010@gmail.com:Sommar23!
```

## Configuration Details

| Setting | Description | Default |
|---------|-------------|----------|
| `bot_token` | Telegram bot token | Required |
| `admin_ids` | List of admin user IDs | [] |
| `database_path` | SQLite database location | database/ulp_bot.db |
| `inventory_path` | ULP files directory | inventory/ |
| `logs_path` | Logs directory | logs/ |
| `search_cost` | Credits per search | 1 |
| `generation_cost` | Credits per credential | 2 |
| `daily_search_limit` | Max searches per day | 100 |
| `daily_generation_limit` | Max generations per day | 50 |
| `max_file_size` | Max file size in bytes | 52MB |
| `cooldown_seconds` | Cooldown between actions | 5 |
| `maintenance_mode` | Enable maintenance mode | false |

## Running on a Server

### Using systemd (Linux)

Create `/etc/systemd/system/ulp-bot.service`:

```ini
[Unit]
Description=ULP Telegram Bot
After=network.target

[Service]
Type=simple
User=nobody
WorkingDirectory=/path/to/ulp-bot
ExecStart=/usr/bin/python3 /path/to/ulp-bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then run:

```bash
sudo systemctl enable ulp-bot
sudo systemctl start ulp-bot
sudo systemctl status ulp-bot
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Build and run:

```bash
docker build -t ulp-bot .
docker run -d --name ulp-bot -v $(pwd)/config.json:/app/config.json ulp-bot
```

## Troubleshooting

### Bot not responding
- Check bot token in `config.json`
- Ensure internet connection
- Check logs: `tail -f logs/bot.log`

### Inventory not loading
- Verify `.txt` files are in `inventory/` directory
- Check file permissions
- Verify ULP format is correct

### Database errors
- Delete `database/ulp_bot.db` to reset
- Check disk space
- Verify write permissions

## Next Steps

1. Add admin ID to `config.json`
2. Use `/admin` command to manage the bot
3. Add inventory files via admin panel
4. Start with `/start` command

## Support

For issues and questions:
- Check logs: `logs/bot.log`
- Review configuration
- Check GitHub issues
