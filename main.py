"""
Instagram Niche Scraper — Telegram Userbot
Uses Telethon (userbot) + Instagrapi (Instagram scraping)
"""

import asyncio
import logging
from telethon import TelegramClient, events
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import Config
from scraper import InstagramScraper
from formatter import format_profile_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# ── Telegram client (userbot — uses your account, not a bot token) ──
client = TelegramClient("userbot_session", Config.API_ID, Config.API_HASH)
scraper = InstagramScraper()
scheduler = AsyncIOScheduler()


# ────────────────────────────────────────────────
# COMMAND HANDLERS
# ────────────────────────────────────────────────

@client.on(events.NewMessage(pattern=r"\.scrape (.+)"))
async def cmd_scrape(event):
    """
    Usage in any chat:
      .scrape fitness
      .scrape @username
    """
    if not Config.ALLOWED_USER_IDS or event.sender_id not in Config.ALLOWED_USER_IDS:
        return  # ignore unauthorized users

    query = event.pattern_match.group(1).strip()
    await event.reply(f"🔍 Scraping Instagram for **{query}**… please wait.")

    try:
        if query.startswith("@"):
            # Single profile lookup
            username = query.lstrip("@")
            profile = await scraper.get_profile(username)
            followers = await scraper.get_followers(username, limit=Config.FOLLOWER_LIMIT)
            report = format_profile_report(profile, followers)
        else:
            # Niche/hashtag — top accounts in that niche
            profiles = await scraper.search_niche(query, limit=Config.NICHE_RESULT_LIMIT)
            report = "\n\n".join(
                format_profile_report(p, followers=[]) for p in profiles
            )

        await send_to_group(report, context=f"Query: {query}")

    except Exception as e:
        log.error(f"Scrape error: {e}")
        await event.reply(f"❌ Error: {e}")


@client.on(events.NewMessage(pattern=r"\.addniche (.+)"))
async def cmd_add_niche(event):
    """Add a niche to the auto-schedule list."""
    if not Config.ALLOWED_USER_IDS or event.sender_id not in Config.ALLOWED_USER_IDS:
        return
    niche = event.pattern_match.group(1).strip()
    Config.add_scheduled_niche(niche)
    await event.reply(f"✅ Added **{niche}** to scheduled niches.\n"
                      f"Current list: {', '.join(Config.SCHEDULED_NICHES)}")


@client.on(events.NewMessage(pattern=r"\.listniche"))
async def cmd_list_niches(event):
    if not Config.ALLOWED_USER_IDS or event.sender_id not in Config.ALLOWED_USER_IDS:
        return
    niches = Config.SCHEDULED_NICHES or ["(none)"]
    await event.reply("📋 Scheduled niches:\n• " + "\n• ".join(niches))


@client.on(events.NewMessage(pattern=r"\.help"))
async def cmd_help(event):
    if not Config.ALLOWED_USER_IDS or event.sender_id not in Config.ALLOWED_USER_IDS:
        return
    await event.reply(
        "**📸 Instagram Niche Scraper — Commands**\n\n"
        "`.scrape <niche>`  — Scrape top Instagram profiles in a niche\n"
        "`.scrape @username` — Scrape a specific profile + followers\n"
        "`.addniche <niche>` — Add niche to auto-schedule\n"
        "`.listniche`        — List scheduled niches\n"
        "`.help`             — Show this message\n\n"
        f"⏰ Auto-scrape runs every **{Config.SCHEDULE_INTERVAL_HOURS}h**"
    )


# ────────────────────────────────────────────────
# SCHEDULED JOB
# ────────────────────────────────────────────────

async def scheduled_scrape():
    """Runs on a schedule — scrapes all configured niches."""
    if not Config.SCHEDULED_NICHES:
        log.info("No niches scheduled, skipping.")
        return

    log.info(f"⏰ Scheduled scrape — niches: {Config.SCHEDULED_NICHES}")
    for niche in Config.SCHEDULED_NICHES:
        try:
            profiles = await scraper.search_niche(niche, limit=Config.NICHE_RESULT_LIMIT)
            report = "\n\n".join(
                format_profile_report(p, followers=[]) for p in profiles
            )
            await send_to_group(report, context=f"⏰ Scheduled — Niche: {niche}")
            await asyncio.sleep(5)  # polite delay between niches
        except Exception as e:
            log.error(f"Scheduled scrape error for '{niche}': {e}")


# ────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────

async def send_to_group(text: str, context: str = ""):
    """Send scraped data to the configured Telegram group."""
    header = f"**📊 Instagram Scrape Report**\n_{context}_\n{'─' * 30}\n"
    full_message = header + text

    # Telegram max message length = 4096 chars; chunk if needed
    chunk_size = 4000
    for i in range(0, len(full_message), chunk_size):
        chunk = full_message[i : i + chunk_size]
        await client.send_message(Config.TARGET_GROUP, chunk)
        await asyncio.sleep(1)


# ────────────────────────────────────────────────
# ENTRY POINT
# ────────────────────────────────────────────────

async def main():
    await client.start(phone=Config.PHONE_NUMBER)
    me = await client.get_me()
    log.info(f"✅ Logged in as {me.first_name} (@{me.username})")

    # Login to Instagram
    scraper.login()
    log.info("✅ Instagram logged in")

    # Start scheduler
    scheduler.add_job(
        scheduled_scrape,
        "interval",
        hours=Config.SCHEDULE_INTERVAL_HOURS,
        id="niche_scrape"
    )
    scheduler.start()
    log.info(f"⏰ Scheduler started — every {Config.SCHEDULE_INTERVAL_HOURS}h")

    log.info("🤖 Userbot running. Type .help in any chat.")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
