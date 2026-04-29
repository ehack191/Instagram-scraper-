"""
scraper.py — Instagram scraping via Instagrapi.
Instagrapi is a third-party unofficial Instagram API library.
"""

import asyncio
import logging
from functools import partial
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, UserNotFound
from config import Config

log = logging.getLogger(__name__)


class InstagramScraper:
    def __init__(self):
        self.cl = Client()
        self.cl.delay_range = [2, 5]  # polite random delay between requests

    def login(self):
        """Login to Instagram. Call once at startup."""
        session_file = "ig_session.json"
        try:
            self.cl.load_settings(session_file)
            self.cl.login(Config.IG_USERNAME, Config.IG_PASSWORD)
            log.info("Instagram: session reloaded")
        except Exception:
            log.info("Instagram: fresh login")
            self.cl.login(Config.IG_USERNAME, Config.IG_PASSWORD)
            self.cl.dump_settings(session_file)

    # ── Async wrappers (instagrapi is sync; run in executor) ──

    async def _run(self, func, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, partial(func, *args, **kwargs))

    async def get_profile(self, username: str) -> dict:
        """Fetch a single Instagram profile."""
        try:
            user = await self._run(self.cl.user_info_by_username, username)
            return {
                "username": user.username,
                "full_name": user.full_name,
                "biography": user.biography,
                "follower_count": user.follower_count,
                "following_count": user.following_count,
                "media_count": user.media_count,
                "is_verified": user.is_verified,
                "is_private": user.is_private,
                "category": user.category,
                "external_url": str(user.external_url) if user.external_url else None,
                "profile_url": f"https://instagram.com/{user.username}",
            }
        except UserNotFound:
            raise ValueError(f"Instagram user @{username} not found")

    async def get_followers(self, username: str, limit: int = 50) -> list[dict]:
        """Fetch a sample of followers for a given username."""
        try:
            user_id = await self._run(self.cl.user_id_from_username, username)
            raw_followers = await self._run(
                self.cl.user_followers, user_id, amount=limit
            )
            followers = []
            for uid, user in list(raw_followers.items())[:limit]:
                followers.append({
                    "username": user.username,
                    "full_name": user.full_name,
                    "is_verified": user.is_verified,
                    "is_private": user.is_private,
                    "profile_url": f"https://instagram.com/{user.username}",
                })
            return followers
        except LoginRequired:
            log.warning("Login required to fetch followers — skipping")
            return []
        except Exception as e:
            log.warning(f"Could not fetch followers for @{username}: {e}")
            return []

    async def search_niche(self, niche: str, limit: int = 5) -> list[dict]:
        """
        Search for top Instagram accounts in a niche.
        Strategy: search hashtag → get top posts → collect unique authors.
        """
        try:
            hashtag = niche.replace(" ", "").lower()
            medias = await self._run(
                self.cl.hashtag_medias_top, hashtag, amount=20
            )

            seen = set()
            profiles = []
            for media in medias:
                uid = media.user.pk
                if uid in seen:
                    continue
                seen.add(uid)
                try:
                    profile = await self.get_profile(media.user.username)
                    profiles.append(profile)
                    if len(profiles) >= limit:
                        break
                    await asyncio.sleep(2)
                except Exception as e:
                    log.warning(f"Skipping user {media.user.username}: {e}")

            return profiles

        except Exception as e:
            log.error(f"Niche search failed for '{niche}': {e}")
            raise ValueError(f"Could not search niche '{niche}': {e}")
          
