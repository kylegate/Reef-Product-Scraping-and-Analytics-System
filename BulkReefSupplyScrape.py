from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import sqlite3
import pandas as pd
import time
from datetime import datetime
from Product import Product


# Scroll to bottom of Page
def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for loading
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


#  Return Price Information
def price_check(product, selector):
    price = None
    price_elements = product.find_elements(By.CSS_SELECTOR, selector)
    if price_elements:
        price_data = price_elements[0].get_attribute("data-product-price")
        if price_data is not None:
            price = float(price_data)
    return price


def Scrape_Products(url, driver, XPATH):
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, XPATH)
        )
    )
    scroll_to_bottom(driver)

    products_elements = driver.find_elements(By.XPATH, XPATH)
    products_scraped = []

    # Scrape Each Individual Product Information
    for category_product in products_elements:
        product_data = Product(
            name=None, brand=None, sku=None, category=None, sale_price=None, old_price=None, option=None, link=None
        )

        try:
            is_multi_option = category_product.find_element(
                By.XPATH,
                './/div[@class="actions-primary"]/a[contains(normalize-space(.), "Choose Options")]'
            )
            product_data.link = is_multi_option.get_attribute("href")
            product_data.option = True

        except:
            try:
                product_data.option = False
                product_data.sku = category_product.get_attribute("data-product-sku")
                product_data.name = category_product.get_attribute("data-product-title")
                product_data.brand = category_product.get_attribute("data-product-brand")
                product_data.category = category_product.get_attribute("data-product-category")
                product_data.old_price = price_check(category_product, selector=".price-wrapper.price.brs-product-price-old")
                product_data.sale_price = price_check(category_product, selector=".price-wrapper.price.brs-product-price-current")
            except:
                pass

        products_scraped.append(product_data)

    return products_scraped


def BulkReefSupplyScrape(driver, url):
    try:
        driver.get(url)

        all_products = Scrape_Products(url, driver, XPATH='//ol[@class="products list items product-items"]/li')
        #print(f"Found {len(all_products)} products on main page")

        scraped_products = []

        for product in all_products:
            if product.link is not None:
                variants = Scrape_Products(product.link, driver, XPATH='//*[@class="grouped-simple brs-product-cta-container"]')
                scraped_products.extend(variants)
                time.sleep(3)
            else:
                scraped_products.append(product)

        #print(f"\n Done scraping. Total final products: {len(scraped_products)}")
        for p in scraped_products:
            print(p)

        return scraped_products

    except Exception as e:
        print(f" Error in BulkReefSupplyScrape: {e}")
        return []


#####################################################################################################
conn = sqlite3.connect('Bulk_Reef_Supply_DB')  # connect to database
cursor = conn.cursor()  # create cursor object to interact with database

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)  # create driver
driver.get("https://www.bulkreefsupply.com/specials.html")  # load bulk reef supply home page

'''
anchors = driver.find_elements(By.XPATH,
                               '//div[contains(@id, "narrow-by-list2")]/div/ul[contains(@class, "items")]/li/a'
                               )
link_urls = [anchor.get_attribute('href') for anchor in anchors]  # Extract link for each category page
'''

link_urls = [
    'https://www.bulkreefsupply.com/sumps-tanks-refugiums.html',
    'https://www.bulkreefsupply.com/aquarium-lighting.html',
    'https://www.bulkreefsupply.com/pumps-plumbing.html',
    'https://www.bulkreefsupply.com/calcium-alkalinity-trace-elements.html',
    'https://www.bulkreefsupply.com/bulk-reverse-osmosis-filters-systems.html',
    'https://www.bulkreefsupply.com/aquarium-monitors-controllers.html',
    'https://www.bulkreefsupply.com/tank-maintenance-salt-mix.html',
    'https://www.bulkreefsupply.com/protein-skimmers.html',
    'https://www.bulkreefsupply.com/filter-media.html',
    'https://www.bulkreefsupply.com/auto-top-off.html',
    'https://www.bulkreefsupply.com/aquarium-heaters-chillers.html',
    'https://www.bulkreefsupply.com/fish-coral-foods.html',
    'https://www.bulkreefsupply.com/bulk-dry-live-rock-live-sand.html',
    'https://www.bulkreefsupply.com/saltwater-aquarium-fragging-supplies.html',
    'https://www.bulkreefsupply.com/live-goods.html'
]

link_urls = [
    'https://www.bulkreefsupply.com/sumps-tanks-refugiums.html']

all_products = []
for link in link_urls:
    all_products.extend(BulkReefSupplyScrape(driver, link))


for product in all_products:
    cursor.execute(
        "INSERT INTO Product(SKU, Name, Brand, Category, Sale_Price, Price, Date) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (product.sku, product.name, product.brand, product.category, product.sale_price, product.price, product.date)
    )
    conn.commit()

print("done")

query = "SELECT * FROM Product"
df = pd.read_sql_query(query, conn)
df = df.reset_index(drop=True)
df.to_csv('BulkReefSupplyProduct.csv', index=False)

cursor.close()
conn.close()
driver.quit()