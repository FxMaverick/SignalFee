from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

SIGNAL_NAME = "Daily Gold Returns"

def get_signal_data():

    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.signalstart.com/search-signals")

    time.sleep(5)

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")

        if len(cols) < 10:
            continue

        name = cols[1].text.strip()

        if SIGNAL_NAME.lower() in name.lower():

            data = {
                "rank": cols[0].text.strip(),
                "name": name,
                "gain": cols[2].text.strip(),
                "dd": cols[4].text.strip(),
                "trades": cols[5].text.strip(),
                "age": cols[9].text.strip(),
            }

            driver.quit()
            return data

    driver.quit()
    return None


if __name__ == "__main__":
    data = get_signal_data()

    if data:
        print("✅ Señal encontrada:")
        for k, v in data.items():
            print(f"{k}: {v}")
    else:
        print("❌ No encontrada")
