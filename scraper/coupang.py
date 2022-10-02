import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from scraper.cp_metadata import DRIVER_PATH
from scraper.cp_metadata import IMG_SRC_CSS, HREF_CSS, PRODUCT_TITLE_CSS, PRICE_CSS, NEXT_ARROW_BTN_CSS

# start_pixel = 1000 #int(input("Start_Pixel : "))
# end_pixel = 4000 #int(input("End_Pixel : "))
# driver.execute_script("document.body.style.zoom='25%'")
# driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")


def main():
    global count

    print("In progress..")
    build_df()
    for count in range(len(keyword)):
        build_driver()
        scroll_range(0, 7000)
        get_elements()
        multi_pages()
    df_to_csv()
    driver.quit()
    print("Success!")


def build_df():
    global df_detected_time, df_img_src, df_href, df_title, df_price
    df_detected_time, df_img_src, df_href, df_title, df_price = [], [], [], [], []


def build_driver():
    global driver
    url = f"https://www.coupang.com/np/search?q={keyword[count]}&channel=user&component=&eventCategory=SRP&trcid=&traid=&sorter=scoreDesc&minPrice=&maxPrice=&priceRange=&filterType=&listSize=36&filter=&isPriceRange=false&brand=&offerCondition=&rating=0&page=1&rocketAll=false&searchIndexingToken=1=6&backgroundColor="

    headlessoptions = webdriver.ChromeOptions()
    headlessoptions.add_argument('headless')
    headlessoptions.add_argument('window-size=1920x1080')
    headlessoptions.add_argument("disable-gpu")
    headlessoptions.add_argument(
        "User-Agent:  Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36")
    headlessoptions.add_argument("lang=ko_KR")

    # driver = webdriver.Chrome(service=Service(DRIVER_PATH), options=headlessoptions)
    driver = webdriver.Chrome(service=Service(DRIVER_PATH))
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """ Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) """})  # 크롤링 방지 설정을 "undefined"로 변경.
    driver.get(url)


def scroll_range(start_pixel, end_pixel):
    for pixel in range(start_pixel, end_pixel, 1000):
        driver.execute_script(f"window.scrollTo(0, {pixel})")
        time.sleep(1.5)


def get_elements():
    get_img_src = driver.find_elements(By.CSS_SELECTOR, IMG_SRC_CSS)
    get_href = driver.find_elements(By.CSS_SELECTOR, HREF_CSS)
    get_title = driver.find_elements(By.CSS_SELECTOR, PRODUCT_TITLE_CSS)
    get_price = driver.find_elements(By.CSS_SELECTOR, PRICE_CSS)

    for img_src, product_href, product_title, price_value in zip(get_img_src, get_href, get_title,
                                                                 get_price):
        src = img_src.get_attribute('src')
        href = product_href.get_attribute('href')
        # print(src, href, product_title.text, price_value.text, seller_info.text)

        df_detected_time.append(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
        df_img_src.append(src)
        df_href.append(href)
        df_title.append(product_title.text)
        df_price.append(price_value.text)


def next_arrow_btn():
    next_button = driver.find_element(By.CSS_SELECTOR, NEXT_ARROW_BTN_CSS)
    next_button.click()
    time.sleep(2)


def multi_pages():
    for page in range(pages - 1):
        next_arrow_btn()
        scroll_range(0, 5000)
        get_elements()


def df_to_csv():
    df = pd.DataFrame(
        {"detected_date": df_detected_time,
         "img_src": df_img_src,
         "href": df_href,
         "product_title": df_title,
         "price_value": df_price}
    )
    today = datetime.today().strftime("%Y%m%d")
    df.to_csv(f"coupang_{keyword}_{today}.csv", index=True, encoding='utf-8-sig')
    print("File Saved.")


if __name__ == "__main__":
    keyword = list(map(str, input('Keywords : ').split(',')))
    pages = int(input("Max Crawl Pages : "))
    main()
