import requests
from bs4 import BeautifulSoup

URL = "https://www.signalstart.com/search-signals"

def get_page():
    proxy_url = f"https://api.allorigins.win/raw?url={URL}"
    res = requests.get(proxy_url)
    return res.text

def get_my_signal():
    html = get_page()
    soup = BeautifulSoup(html, "html.parser")

    rows = soup.select("table tbody tr")

    print(f"Filas encontradas: {len(rows)}")

    for row in rows:
        cols = row.find_all("td")

        if len(cols) < 10:
            continue

        name = cols[1].text.strip()

        if "Daily Gold Returns" in name:
            return {
                "rank": cols[0].text.strip(),
                "gain": cols[2].text.strip(),
                "dd": cols[4].text.strip(),
                "trades": cols[5].text.strip(),
                "price": cols[8].text.strip()
            }

    return None


if __name__ == "__main__":
    print(get_my_signal())
