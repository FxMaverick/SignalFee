import requests
from bs4 import BeautifulSoup

URL = "https://www.signalstart.com/search-signals"

def get_my_signal():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.select("table tbody tr")

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
