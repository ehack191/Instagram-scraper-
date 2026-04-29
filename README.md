# 📸 Instagram Niche Scraper — Telegram Userbot

Scrapes Instagram profiles & followers by niche, delivers results to a Telegram group.
Triggered by commands OR on an automatic schedule.

---

## 📁 Project Structure

```
instagram_userbot/
├── main.py          # Userbot entry point, command handlers, scheduler
├── scraper.py       # Instagram scraping logic (Instagrapi)
├── formatter.py     # Formats data into Telegram messages
├── config.py        # Loads all settings from .env
├── requirements.txt
└── .env.example     # Copy this to .env and fill in your values
```

---

## ⚙️ Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Telegram API credentials

1. Go to https://my.telegram.org
2. Log in → **App Management** → Create an app
3. Copy `api_id` and `api_hash`

### 3. Configure your `.env`

```bash
cp .env.example .env
# Edit .env with your values
```

Key values to fill in:

| Variable | Description |
|---|---|
| `TG_API_ID` | From my.telegram.org |
| `TG_API_HASH` | From my.telegram.org |
| `TG_PHONE` | Your phone number (+91...) |
| `TG_TARGET_GROUP` | Group username or numeric ID |
| `TG_ALLOWED_IDS` | Your Telegram user ID (from @userinfobot) |
| `IG_USERNAME` | Instagram username (use a secondary account) |
| `IG_PASSWORD` | Instagram password |
| `SCHEDULED_NICHES` | Comma-separated niches to auto-scrape |
| `SCHEDULE_HOURS` | Auto-scrape interval in hours |

### 4. Add the userbot to your Telegram group

- Open your Telegram group settings
- Add your own account as admin (or at least a member who can send messages)
- The userbot runs as **you**, so it can post as a member automatically

### 5. Run

```bash
python main.py
```

On first run, Telegram will ask for your phone number + OTP to create a session.
The session is saved to `userbot_session.session` — keep it safe.

---

## 💬 Commands

Type these in **any chat** (the bot listens to your own messages):

| Command | Description |
|---|---|
| `.scrape fitness` | Scrape top profiles in the "fitness" niche |
| `.scrape @username` | Scrape a specific profile + sample of followers |
| `.addniche travel` | Add "travel" to the auto-schedule list |
| `.listniche` | Show all scheduled niches |
| `.help` | Show command list |

Results are always sent to the configured `TG_TARGET_GROUP`.

---

## ⚠️ Important Notes

### Use a secondary Instagram account
Instagrapi makes unofficial API calls. Instagram may rate-limit or temporarily ban accounts that scrape heavily. **Do not use your main personal account.**

### Respect rate limits
The scraper has built-in delays (`delay_range = [2, 5]` seconds). Don't set `NICHE_RESULT_LIMIT` or `FOLLOWER_LIMIT` too high.

### Follower scraping requires a public or followed account
Instagram restricts follower lists for private accounts you don't follow.

### Session files
- `userbot_session.session` — Telegram session (your login)
- `ig_session.json` — Instagram session (reused to avoid repeated logins)
- `niches.json` — Persisted niche list (updated by `.addniche`)

---

## 🔧 Customization

- **Change schedule interval**: Set `SCHEDULE_HOURS` in `.env`
- **Change result count**: Set `NICHE_RESULT_LIMIT` and `FOLLOWER_LIMIT` in `.env`
- **Add more niches at runtime**: Use `.addniche <niche>` command — persisted across restarts

---

## 🚀 Running as a background service (Linux)

Create `/etc/systemd/system/ig-userbot.service`:

```ini
[Unit]
Description=Instagram Niche Scraper Userbot
After=network.target

[Service]
WorkingDirectory=/path/to/instagram_userbot
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable ig-userbot
sudo systemctl start ig-userbot
sudo systemctl status ig-userbot
```
