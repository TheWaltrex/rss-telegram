"""Envío puntual: publica, en orden cronológico, las noticias posteriores a DESDE."""
import os, calendar, re, time
from datetime import datetime
from zoneinfo import ZoneInfo
import feedparser
from rss_telegram import load_feeds, send

DESDE = datetime.fromisoformat(os.environ["DESDE"]).replace(tzinfo=ZoneInfo("Europe/Madrid")).timestamp()
YA_PUBLICADAS = [l for l in os.environ.get("SALTAR", "").split() if l]

noticias = []
for url in load_feeds():
    d = feedparser.parse(url, agent="Mozilla/5.0 (RSS a Telegram)")
    for e in d.entries:
        fecha = e.get("published_parsed") or e.get("updated_parsed")
        if not fecha:
            continue
        ts = calendar.timegm(fecha)
        link = e.get("link", "")
        if ts > DESDE and not any(s in link for s in YA_PUBLICADAS):
            title = re.sub(r"\s+", " ", e.get("title", "(sin título)")).strip()
            noticias.append((ts, title, link))

noticias.sort()
print(f"Noticias a publicar: {len(noticias)}")
for ts, title, link in noticias:
    print(time.strftime("%d/%m %H:%M UTC", time.gmtime(ts)), title)
    if send(title, link):
        time.sleep(3)
