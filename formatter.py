"""
formatter.py — Format scraped Instagram data into clean Telegram messages.
"""


def format_profile_report(profile: dict, followers: list[dict]) -> str:
    """Format a single profile + optional followers into a Telegram message."""

    verified_badge = "✅" if profile.get("is_verified") else ""
    private_tag = "🔒 Private" if profile.get("is_private") else "🌐 Public"

    lines = [
        f"👤 **@{profile['username']}** {verified_badge}",
        f"📛 {profile.get('full_name') or 'N/A'}",
        f"🏷 {profile.get('category') or 'No category'}  |  {private_tag}",
        f"👥 Followers: **{_fmt_num(profile.get('follower_count', 0))}**  "
        f"Following: {_fmt_num(profile.get('following_count', 0))}",
        f"📸 Posts: {_fmt_num(profile.get('media_count', 0))}",
    ]

    bio = profile.get("biography", "").strip()
    if bio:
        # Truncate long bios
        bio_short = bio[:200] + "…" if len(bio) > 200 else bio
        lines.append(f"📝 _{bio_short}_")

    url = profile.get("external_url")
    if url:
        lines.append(f"🔗 {url}")

    lines.append(f"🔎 {profile.get('profile_url', '')}")

    if followers:
        lines.append(f"\n**Followers sample ({len(followers)})**")
        for f in followers[:20]:  # cap display at 20
            badge = "✅" if f.get("is_verified") else ""
            lock = "🔒" if f.get("is_private") else ""
            lines.append(f"  • @{f['username']} {badge}{lock}")

        if len(followers) > 20:
            lines.append(f"  … and {len(followers) - 20} more")

    return "\n".join(lines)


def _fmt_num(n: int) -> str:
    """Format large numbers: 1234567 → 1.2M"""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)
  
