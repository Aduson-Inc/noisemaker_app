"""General-purpose YouTube search via yt-dlp. Returns structured trending results."""

import json
import sys
from datetime import datetime, timedelta

import yt_dlp


def search_youtube(query: str, max_results: int = 15, months: int = 3) -> list[dict]:
    cutoff = datetime.now() - timedelta(days=months * 30)
    cutoff_str = cutoff.strftime("%Y%m%d")

    # Over-fetch so we have enough after date filtering, then rank by views
    fetch_count = max_results * 3

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "skip_download": True,
    }

    raw = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{fetch_count}:{query}", download=False)
        if not info or "entries" not in info:
            return []

        for entry in info["entries"]:
            if entry is None:
                continue

            upload_date = entry.get("upload_date", "")
            if upload_date and upload_date < cutoff_str:
                continue

            raw_views = entry.get("view_count") or 0
            dur_secs = entry.get("duration") or 0

            # Format duration
            mins, secs = divmod(int(dur_secs), 60)
            hrs, mins = divmod(mins, 60)
            duration = f"{hrs}:{mins:02d}:{secs:02d}" if hrs else f"{mins}:{secs:02d}"

            # Format view count for display
            if raw_views >= 1_000_000:
                view_str = f"{raw_views / 1_000_000:.1f}M"
            elif raw_views >= 1_000:
                view_str = f"{raw_views / 1_000:.1f}K"
            else:
                view_str = str(raw_views)

            # Format upload date
            date_str = ""
            if upload_date and len(upload_date) == 8:
                date_str = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"

            raw.append({
                "title": entry.get("title", "Unknown"),
                "channel": entry.get("channel") or entry.get("uploader", "Unknown"),
                "views": view_str,
                "views_raw": raw_views,
                "duration": duration,
                "date": date_str,
                "url": entry.get("webpage_url") or f"https://youtube.com/watch?v={entry.get('id', '')}",
            })

    # Sort by view count descending — surface the most trending/popular
    raw.sort(key=lambda x: x["views_raw"], reverse=True)

    # Drop the raw sort key, return top N
    results = []
    for item in raw[:max_results]:
        results.append({
            "title": item["title"],
            "channel": item["channel"],
            "views": item["views"],
            "duration": item["duration"],
            "date": item["date"],
            "url": item["url"],
        })

    return results


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not query:
        print("Usage: python yt_search.py <search query>")
        sys.exit(1)

    results = search_youtube(query)
    print(json.dumps(results, indent=2))
