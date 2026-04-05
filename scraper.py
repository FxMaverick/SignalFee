from playwright.sync_api import sync_playwright

SIGNAL_NAME = "Daily Gold Returns"

def get_signal_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://www.signalstart.com/search-signals")

        # seleccionar 100 resultados
        page.select_option('select[name="signals_length"]', '100')
        page.wait_for_timeout(5000)

        rows = page.query_selector_all("table tbody tr")

        for row in rows:
            cols = row.query_selector_all("td")

            if len(cols) < 10:
                continue

            name = cols[1].inner_text().strip()

            if SIGNAL_NAME.lower() in name.lower():
                data = {
                    "rank": cols[0].inner_text(),
                    "gain": cols[2].inner_text(),
                    "dd": cols[4].inner_text(),
                    "trades": cols[5].inner_text(),
                    "price": cols[8].inner_text(),
                }
                browser.close()
                return data

        browser.close()
        return None


if __name__ == "__main__":
    print(get_signal_data())
