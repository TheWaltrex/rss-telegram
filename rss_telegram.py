import os, json, time, html, re
import feedparser, requests
from urllib.parse import urlparse

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
API = f"https://api.telegram.org/bot{TOKEN}"
FEEDS_FILE = "feeds.txt"
STATE_FILE = "seen.json"
MAX_IDS = 300        # noticias recordadas por feed
MAX_PER_FEED = 10    # máximo que se publica por feed en cada pasada

def load_feeds():
    with open(FEEDS_FILE, encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]

def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)

def entry_id(e):
    return e.get("id") or e.get("link") or e.get("title", "")

def send(title, link):
    # Enlace corto visible (solo el dominio) que apunta a la noticia completa
    domain = urlparse(link).netloc.removeprefix("www.") or link
    payload = {
        "chat_id": CHAT_ID,
        "text": f'{html.escape(title)}\n<a href="{html.escape(link, quote=True)}">{html.escape(domain)}</a>',
        "parse_mode": "HTML",
        "link_preview_options": {"url": link},   # vista previa de la noticia
    }
    for _ in range(5):
        r = requests.post(f"{API}/sendMessage", json=payload, timeout=30)
        if r.ok:
            return True
        if r.status_code == 429:  # Telegram pide esperar
            time.sleep(r.json().get("parameters", {}).get("retry_after", 10) + 1)
            continue
        print("Error de Telegram:", r.status_code, r.text)
        return False
    return False

def main():
    state = load_state()
    for url in load_feeds():
        d = feedparser.parse(url, agent="Mozilla/5.0 (RSS a Telegram)")
        if not d.entries:
            print(f"No se pudo leer {url}: {d.get('bozo_exception', 'sin entradas')}")
            continue

        ids = [entry_id(e) for e in d.entries]
        if url not in state:
            # Feed nuevo: se marca todo como leído para no inundar el canal
            state[url] = ids[:MAX_IDS]
            print(f"Feed registrado: {url}")
            continue

        seen = state[url]
        seen_set = set(seen)
        nuevas = [e for e in d.entries if entry_id(e) not in seen_set]

        # Las que superan el límite se marcan como leídas sin publicarse
        for e in nuevas[MAX_PER_FEED:]:
            seen.insert(0, entry_id(e))

        # Se publican de la más antigua a la más reciente
        for e in reversed(nuevas[:MAX_PER_FEED]):
            title = re.sub(r"\s+", " ", e.get("title", "(sin título)")).strip()
            if send(title, e.get("link", "")):
                seen.insert(0, entry_id(e))
                time.sleep(3)

        state[url] = seen[:MAX_IDS]
    save_state(state)

if __name__ == "__main__":
    main()
