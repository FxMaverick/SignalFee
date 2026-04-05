import requests
from bs4 import BeautifulSoup
import numpy as np
import re
from flask import Flask

app = Flask(__name__)

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
# MODULE 2: FETCH TARGET SIGNAL DATA (LABEL → VALUE)
# =========================
def get_my_signal():
    res = requests.get(MY_SIGNAL_URL, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    try:
        data = {
            "rank": None,
            "gain": None,
            "dd": None,
            "price": None
        }

        elements = soup.find_all(string=True)

        for i, el in enumerate(elements):
            text = el.strip()

            if not text:
                continue

            # Rank
            if text == "Rank" and data["rank"] is None:
                if i + 1 < len(elements):
                    next_text = elements[i + 1].strip()
                    match = re.search(r'\d+', next_text)
                    if match:
                        data["rank"] = int(match.group())

            # Gain
            elif text == "Gain" and data["gain"] is None:
                if i + 1 < len(elements):
                    next_text = elements[i + 1].strip()
                    match = re.search(r'(\d+(\.\d+)?)%', next_text)
                    if match:
                        data["gain"] = float(match.group(1))

            # Drawdown
            elif text == "Drawdown" and data["dd"] is None:
                if i + 1 < len(elements):
                    next_text = elements[i + 1].strip()
                    match = re.search(r'(\d+(\.\d+)?)%', next_text)
                    if match:
                        data["dd"] = float(match.group(1))

            # Price
            elif text == "Price" and data["price"] is None:
                if i + 1 < len(elements):
                    next_text = elements[i + 1].strip()
                    match = re.search(r'(\d+(\.\d+)?)', next_text)
                    if match:
                        data["price"] = float(match.group(1))

        if None in data.values():
            return None

        if data["dd"] == 0:
            data["dd"] = 0.1

        return data

    except:
        return None


# =========================
# MODULE 3: CONTINUOUS RANK CAP
# =========================
def cap_por_rank(rank):
    if rank > 50:
        return 30
    return 30 + (50 - rank)


# =========================
# MODULE 4: PRICING ENGINE
# =========================
def calculate_price(top_signals, my_signal):

    filtered = [
        s for s in top_signals
        if SIGNAL_NAME.lower() not in s["name"].lower()
    ][:20]

    prices = [s["price"] for s in filtered]
    price_base = np.median(prices)

    quality_top = np.median([s["gain"] / s["dd"] for s in filtered])
    quality_me = my_signal["gain"] / my_signal["dd"]

    quality_rel = quality_me / quality_top

    factor = quality_rel ** 0.5
    estimated_price = price_base * factor

    cap = cap_por_rank(my_signal["rank"])

    final_price = min(estimated_price, cap)
    final_price = max(30, round(final_price / 5) * 5)

    return final_price, quality_rel


# =========================
# WEB OUTPUT
# =========================
@app.route("/")
def home():

    top_signals = get_top_signals()
    my_signal = get_my_signal()

    if not my_signal:
        return "<h2>Error: Signal data not found</h2>"

    price, quality_rel = calculate_price(top_signals, my_signal)

    return f"""
    <html>
        <head>
            <title>Signal Pricing</title>
        </head>
        <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h1>Fair Signal Price</h1>
            <h2>${price}</h2>
            <p>Rank: {my_signal['rank']}</p>
            <p>Quality (vs market): {round(quality_rel, 2)}</p>
        </body>
    </html>
    """


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
