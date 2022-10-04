import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

import re
import time
import random
import pandas as pd
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config import vivino


def selenium_driver(web_disabled=False):
    options = webdriver.ChromeOptions()

    if web_disabled:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument(
            "user-agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62"
        )

    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    return driver


def scraping_href(web):
    driver = selenium_driver(web_disabled=False)

    # 응답 딜레이 대기
    driver.implicitly_wait(3)
    driver.get(web["url"])

    # 검색 옵션 세팅
    for i in range(2, 7):
        wine_type = driver.find_element(
            by=By.CSS_SELECTOR, value=web["wine_type_btn_path"].format(i)
        )
        wine_type.click()

    wine_review = driver.find_element(
        by=By.CSS_SELECTOR, value=web["wine_review_btn_path"]
    )
    wine_price_min = driver.find_element(
        by=By.CSS_SELECTOR, value=web["wine_price_min_path"]
    )
    wine_price_max = driver.find_element(
        by=By.CSS_SELECTOR, value=web["wine_price_max_path"]
    )

    if not wine_review.is_selected():
        wine_review.click()

    action_chains = ActionChains(driver)
    action_chains.drag_and_drop_by_offset(wine_price_min, -100, 0).perform()
    action_chains.drag_and_drop_by_offset(wine_price_max, 100, 0).perform()

    # 현재 스크립트 높이 측정
    prev_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    time.sleep(5)

    # 스크립트 맨 바닥까지 이동
    while True:
        current_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.implicitly_wait(1)

        print(f"current_height: {current_height}, prev_height: {prev_height}")

        if current_height == prev_height:
            print("last_height: " + str(prev_height))
            driver.get_screenshot_as_file("webpage_screenshot.png")
            break
        else:
            prev_height = current_height
            time.sleep(5)

    href_list = []

    div_tag = driver.find_elements(by=By.CLASS_NAME, value="wineCard__wineCard--2dj2T")
    div_len = len(div_tag)
    print("div length : {}".format(div_len))

    for div in div_tag:
        a = div.find_element(by=By.TAG_NAME, value="a")
        href = a.get_attribute("href")
        href_list += [href]

    data = {"href": href_list}

    df = pd.DataFrame(data)

    df.to_csv(BASE_DIR / "data/vivino/vivino_href.csv", index=False)

    time.sleep(20)
    driver.quit()

    return df


def scraping_detail(href_list):

    items = []
    for href in href_list:
        items.append(href["item"])

    return items


if __name__ == "__main__":
    a = 1
    print(BASE_DIR)
    # df = scraping_href(vivino)
    # print(df)
