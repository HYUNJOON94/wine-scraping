import re
import time
import random
import pandas as pd
from tqdm import tqdm

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# inner module
# import config


def scraping():
    url = "https://www.vivino.com/explore"
    a_class_path = "_3qc2M wineCard__cardLink--3F_uB"
    selector_path = "#explore-page-app > div > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(1)"
    selector_path = "#explore-page-app > div > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div"
    selector_path = "#explore-page-app > div > div > div:nth-child(2) > div:nth-child(1) > div:nth-child({}) > div > a"
    selector_path = "#explore-page-app > div > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(31) > div > a"
    # explore-page-app > div > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div > a
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    # options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62"
    )
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    # 응답 딜레이 대기
    driver.implicitly_wait(3)
    driver.get(url)

    element_body = driver.find_element(by=By.TAG_NAME, value="body")
    prev_height = driver.execute_script("return document.body.scrollHeight")
    print(prev_height)
    scroll_cnt = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(8)
        current_height = driver.execute_script("return document.body.scrollHeight")
        print(f"current_height: {current_height}, prev_height: {prev_height}")

        if current_height == prev_height:
            print("last_height: " + str(prev_height))
            driver.get_screenshot_as_file("webpage_screenshot.png")
            break
        else:
            prev_height = current_height

    href_list = []
    #
    wine_type_btn_path = "#explore-page-app > div > div > div.explorerPage__columns--1TTaK > div.explorerPage__filters--1Hmly > div > div.filterByWineType__filterByWineType--1HocL > div.filterByWineType__items--2GBgf > label:nth-child(1)"
    wine_review_btn_path = "#explore-page-app > div > div > div.explorerPage__columns--1TTaK > div.explorerPage__filters--1Hmly > div > div.filterByRating__filterByRating--2FBCl.explorerPageFilters__filter--3ku7u > label:nth-child(5) > div._2K-I_._25kxz"
    wine_price_min_path = "#explore-page-app > div > div > div.explorerPage__columns--1TTaK > div.explorerPage__filters--1Hmly > div > div.filterByPriceRange__filterByPriceRange--2FDne.explorerPageFilters__filter--3ku7u > div.rangeSlider__rangeSlider--3Gh0- > div.rangeSlider__slider--DaZc5 > div > div.rc-slider-handle.rc-slider-handle-1"
    wine_price_max_path = ""
    wine_type = driver.find_element(by=By.CSS_SELECTOR, value=wine_type_btn_path)
    wine_review = driver.find_element(by=By.CSS_SELECTOR, value=wine_review_btn_path)
    wine_price_min = driver.find_element(by=By.CSS_SELECTOR, value=wine_price_min_path)
    wine_price_max = driver.find_element(by=By.CSS_SELECTOR, value=wine_price_max_path)

    if wine_type.is_selected():
        wine_type.click()

    if not wine_review.is_selected():
        wine_review.click()

    driver.execute_script(
        "arguments[0].setAttribute('value',arguments[1])", wine_price_min, 0
    )

    div_tag = driver.find_elements(by=By.CLASS_NAME, value="wineCard__wineCard--2dj2T")
    div_len = len(div_tag)
    print("div length : {}".format(div_len))

    for div in div_tag:
        a = div.find_element(by=By.TAG_NAME, value="a")
        href = a.get_attribute("href")
        href_list += [href]

    data = {"href": href_list}

    df = pd.DataFrame(data)

    df.to_csv("vivino_href.csv", index=False)
    driver.quit()

    return True


# explore-page-app > div > div > div.explorerPage__columns--1TTaK > div.explorerPage__results--3wqLw > div:nth-child(1) > div:nth-child(1)
# href
# explore-page-app > div > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div > a

# image
# explore-page-app > div > div > div.explorerPage__columns--1TTaK > div.explorerPage__results--3wqLw > div:nth-child(1) > div:nth-child(1) > div > a > div > div.wineCard__bottleSection--3Bzic > img
# region
# explore-page-app > div > div > div.explorerPage__columns--1TTaK > div.explorerPage__results--3wqLw > div:nth-child(1) > div:nth-child(1) > div > a > div > div.wineCard__infoColumn--3NKrN > div > div.wineInfoVintage__wineInfoVintage--bXr7s.wineInfoVintage__large--OaWjm.wineInfo__vintage--2wqwE > div:nth-child(1)
# title
# explore-page-app > div > div > div.explorerPage__columns--1TTaK > div.explorerPage__results--3wqLw > div:nth-child(1) > div:nth-child(1) > div > a > div > div.wineCard__infoColumn--3NKrN > div > div.wineInfoVintage__wineInfoVintage--bXr7s.wineInfoVintage__large--OaWjm.wineInfo__vintage--2wqwE > div:nth-child(1)


# 교육 세션 마지막 페이지 번호 불러오기
def get_last_pagenum(driver, page_num, input_date, no_loop):
    driver.get(config.NAVER_PATH["main_url"].format(page_num, input_date))
    paging = driver.find_element(
        by="css selector", value=config.NAVER_PATH["main_paging"]
    )
    paging_text = paging.text.split(" ")

    if "다음" not in paging_text:
        no_loop = True

    paging_list = []
    for t in paging_text:
        if t.isdigit():
            paging_list.append(int(t))

    paging_list.sort(reverse=True)
    last_page = paging_list[0]
    return last_page, no_loop


def crawling_news(input_date):

    news_date_list = []
    news_title_list = []
    news_content_list = []
    naver_href_list = []
    raw_href_list = []

    page_num = 1
    no_loop = False
    url_pattern = re.compile("news.naver.com")
    css_list = [config.NAVER_PATH["main_top10"], config.NAVER_PATH["main_bot10"]]

    options = webdriver.ChromeOptions()

    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    while True:
        last_page, no_loop = get_last_pagenum(driver, page_num, input_date, no_loop)

        for i in range(1, 11):
            for css in css_list:
                try:
                    a_tag = driver.find_element(by="css selector", value=css.format(i))
                    title = a_tag.text
                    href = a_tag.get_attribute("href")

                    naver_href_list += [href]
                    news_title_list += [title]
                    news_date_list += [input_date]
                except:
                    pass

        if last_page % 10 == 0:
            next_page = page_num + 1
            last_page, no_loop = get_last_pagenum(
                driver, next_page, input_date, no_loop
            )

        if last_page == page_num:
            if no_loop:
                print(input_date, ": {} Pages end".format(last_page))
                break
        page_num += 1

    for naver_href in tqdm(naver_href_list):
        driver.get(naver_href)
        time.sleep(1)

        url = driver.current_url

        if re.search(url_pattern, url) == None:
            print("error url:", url)
            news_content_list += [""]
            raw_href_list += [""]

        else:
            try:
                content = driver.find_elements(
                    by="css selector", value=config.NAVER_PATH["mnews_content_1"]
                )
                raw_href = driver.find_elements(
                    by="css selector", value=config.NAVER_PATH["mnews_raw_href"]
                )

                if content == []:
                    content = driver.find_elements(
                        by="css selector", value=config.NAVER_PATH["mnews_content_2"]
                    )

                content = content[0].text

                # 너무 짧은 기사(날려쓴기사) 제거
                if len(content.split("\n")) <= 1:
                    content = ""

                raw_href = raw_href[0].get_attribute("href")
                news_content_list += [content]
                raw_href_list += [raw_href]

            except Exception as e:
                print("error", e)
                news_content_list += [""]
                raw_href_list += [""]

    driver.close()

    crawl_data = {
        "news_date": news_date_list,
        "naver_href": naver_href_list,
        "raw_href": raw_href_list,
        "news_title": news_title_list,
        "news_content": news_content_list,
    }

    df = pd.DataFrame(crawl_data)

    drop_idx = df[df["news_content"] == ""].index
    df.drop(df.index[drop_idx], inplace=True)
    df.drop_duplicates("news_title", inplace=True)
    df.reset_index(drop=True, inplace=True)
    records = df.to_dict("records")

    return records


if __name__ == "__main__":
    df = scraping()
    print(df)
