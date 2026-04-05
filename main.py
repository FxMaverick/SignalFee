import requests
from bs4 import BeautifulSoup
import numpy as np

# =========================
# CONFIGURATION
# =========================
SIGNAL_NAME = "Daily Gold Returns"
MY_SIGNAL_URL = "https://www.signalstart.com/analysis/daily-gold-returns/287480"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# =========================
# MODULE 1: FETCH TOP SIGNALS (MARKET CONTEXT)
# =========================
def get_top_signals():
    url = "https://www.signalstart.com/search-signals"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.select("table tbody tr")

    signals = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 10:
            continue

        try:
            name = cols[1].text.strip()
            gain = float(cols[2].text.replace('%', '').replace(',', ''))
            dd = float(cols[4].text.replace('%', '').replace(',', ''))
            price = float(cols[8].text.replace('$', '').replace(',', ''))

            if dd == 0:
                dd = 0.1

            signals.append({
                "name": name,
                "gain": gain,
                "dd": dd,
                "price": price
            })

        except:
            continue

    return signals


# =========================
# MODULE 2: FETCH TARGET SIGNAL DATA
# =========================
def get_my_signal():
    res = requests.get(MY_SIGNAL_URL, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    try:
        # Buscar todos los bloques tipo "stat"
        stats = soup.find_all("div")

        data = {
            "rank": None,
            "gain": None,
            "dd": None,
            "price": None
        }

        for s in stats:
            text = s.get_text(" ", strip=True)

            if "Rank" in text and data["rank"] is None:
                try:
                    data["rank"] = int(''.join(filter(str.isdigit, text)))
                except:
                    pass

            elif "Gain" in text and data["gain"] is None:
                try:
                    data["gain"] = float(text.split('%')[0].split()[-1])
                except:
                    pass

            elif "Drawdown" in text and data["dd"] is None:
                try:
                    data["dd"] = float(text.split('%')[0].split()[-1])
                except:
                    pass

            elif "Price" in text and data["price"] is None:
                try:
                    data["price"] = float(text.replace('$', '').split()[-1])
                except:
                    pass

        # Validación mínima
        if None in data.values():
            return None

        if data["dd"] == 0:
            data["dd"] = 0.1

        return data

    except:
        return None


# =========================
# MODULE 3: PRICING ENGINE
# =========================
def calculate_price(top_signals, my_signal):

    # Remove self from benchmark if present
    filtered = [
        s for s in top_signals
        if SIGNAL_NAME.lower() not in s["name"].lower()
    ][:20]

    # Market baseline (median price)
    prices = [s["price"] for s in filtered]
    price_base = np.median(prices)

    # Quality comparison
    quality_top = np.median([s["gain"] / s["dd"] for s in filtered])
    quality_me = my_signal["gain"] / my_signal["dd"]

    # Continuous adjustment factor
    factor = (quality_me / quality_top) ** 0.5
    estimated_price = price_base * factor

    # Visibility cap (rank-based)
    rank = my_signal["rank"]

    if rank <= 20:
        cap = 60
    elif rank <= 30:
        cap = 50
    elif rank <= 50:
        cap = 40
    else:
        cap = 30

    final_price = min(estimated_price, cap)

    # Normalize
    final_price = max(30, round(final_price / 5) * 5)

    return final_price


# =========================
# MAIN EXECUTION
# =========================
if __name__ == "__main__":

    top_signals = get_top_signals()
    my_signal = get_my_signal()

    if not my_signal:
        print("Error: Signal data not found")
        exit()

    price = calculate_price(top_signals, my_signal)

    print(f"Fair Signal Price: ${price}")
