import requests
from bs4 import BeautifulSoup

URL = "https://www.signalstart.com/search-signals"

def get_top_signals():
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(URL, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.select("table tbody tr")

    signals = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 10:
            continue

        signals.append({
            "rank": int(cols[0].text.strip()),
            "gain": float(cols[2].text.replace('%','')),
            "dd": float(cols[4].text.replace('%','')),
            "price": float(cols[8].text.replace('$',''))
        })

    return signals
