import json
import os
from pathlib import Path
import urllib.request

import feedparser
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

FEEDS_FILE = Path("accounts.txt")
SENT_FILE = Path("sent.json")


def load_sent():
    if SENT_FILE.exists():
        return json.loads(SENT_FILE.read_text(encoding="utf-8"))
    return {}


def save_sent(sent):
    SENT_FILE.write_text(
        json.dumps(sent, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def read_feeds():
    return [
        line.strip()
        for line in FEEDS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def send_discord(feed_title, post_title, link):
    payload = {
        "content": f"📢 **{feed_title}**\n\n{post_title}\n\n🔗 {link}"
    }

    req = urllib.request.Request(
        WEBHOOK_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        },
        method="POST"
    )

    with urllib.request.urlopen(req) as response:
        print("Discord通知成功:", response.status)


def main():
    sent = load_sent()
    feeds = read_feeds()

    for feed_url in feeds:
        print("確認中:", feed_url)

        feed = feedparser.parse(feed_url)

        if not feed.entries:
            print("投稿が見つかりません:", feed_url)
            continue

        latest = feed.entries[0]

        feed_title = feed.feed.get("title", "X公式")
        post_title = latest.get("title", "新しい投稿")
        link = latest.get("link", feed_url)
        entry_id = latest.get("id") or link
        if sent.get(feed_url) == entry_id:
            print("新着なし:", feed_title)
            continue

        send_discord(feed_title, post_title, link)
        sent[feed_url] = entry_id

    save_sent(sent)


if __name__ == "__main__":
    main()