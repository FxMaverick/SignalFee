import requests

URL = "https://www.signalstart.com/search-signals-json"

def get_signals():
    params = {
        "length": 100
    }

    response = requests.get(URL, params=params)
    data = response.json()

    return data["data"]


def get_my_signal():
    signals = get_signals()

    for s in signals:
        if "Daily Gold Returns" in s["name"]:
            return {
                "rank": s["rank"],
                "gain": s["gain"],
                "dd": s["drawdown"],
                "trades": s["trades"],
                "price": s["price"]
            }

    return None


if __name__ == "__main__":
    print(get_my_signal())
