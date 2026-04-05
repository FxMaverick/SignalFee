import requests

URL = "https://www.signalstart.com/search-signals"

def get_signals():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest"
    }

    payload = {
        "draw": 1,
        "start": 0,
        "length": 100
    }

    response = requests.post(URL, data=payload, headers=headers)

    print("Status:", response.status_code)
    print("Raw response (first 200 chars):", response.text[:200])

    return response.text


if __name__ == "__main__":
    get_signals()
