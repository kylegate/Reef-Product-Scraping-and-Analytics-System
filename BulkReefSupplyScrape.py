from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
import pandas as pd
import time
import datetime
from Product import Product


def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for loading
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def get_Item_Status(product):
    primary_action = product.find_element(By.XPATH, './/div[@class="actions-primary"]/*[self::a or self::button][1]')
    class_name = primary_action.get_attribute("class")
    status = class_name[26:].replace("-"," ")
    return status


#  Return Price Information
def price_check(product, selector):
    price = None
    price_elements = product.find_elements(By.CSS_SELECTOR, selector)
    if price_elements:
        price_data = price_elements[0].get_attribute("data-product-price")
        if price_data is not None:
            price = float(price_data)
    return price


#  Return Item Object (contains product info from website)
def Get_Product_Info(product, status):
    # Extract product information for each product on the page
    product_sku = product.get_attribute("data-product-sku")
    product_name = product.get_attribute("data-product-title")
    product_brand = product.get_attribute("data-product-brand")
    product_category = product.get_attribute("data-product-category")
    old_price = price_check(product, selector=".price-wrapper.price.brs-product-price-old")
    sale_price = price_check(product, selector=".price-wrapper.price.brs-product-price-current")

    item = Product(name=product_name, brand=product_brand, sku=product_sku, category=product_category,
                   sale_price=sale_price, old_price=old_price, option=status)
    return item



conn = sqlite3.connect('Bulk_Reef_Supply_DB')  # connect to database
cursor = conn.cursor()  # create cursor object to interact with database
driver = webdriver.Chrome() # create driver
driver.get("https://www.bulkreefsupply.com/specials.html")  # load bulk reef supply home page

''' Get Category Links from Home Page '''
WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located(
        (By.XPATH, '//div[contains(@id, "narrow-by-list2")]/div/ul[contains(@class, "items")]/li/a')
    )
)

anchors = driver.find_elements(By.XPATH,
                               '//div[contains(@id, "narrow-by-list2")]/div/ul[contains(@class, "items")]/li/a'
                               )
link_urls = [anchor.get_attribute('href') for anchor in anchors]  # Extract link for each category page


''' Go to Each Category Page and Scrape All Items '''
sub_product_links = []
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d %H")

for url in link_urls:

    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, '//ol[@class="products list items product-items"]/li')
        )
    )

    scroll_to_bottom(driver)

    category_product_list = driver.find_elements(By.XPATH, '//ol[@class="products list items product-items"]/li')

    ''' Scrape Each Individual Product Information '''
    for product in category_product_list:
        product_status = get_Item_Status(product)
        if product_status == 'choose options':
            link_element = product.find_element(By.XPATH, './/div/div/div[4]/div/div[1]/a[1]')
            URL = link_element.get_attribute('href')
            sub_product_links.append(URL)  # Save this link to be revisited later
            pass
        else:
            item = Get_Product_Info(product, product_status)
            cursor.execute(
                "INSERT INTO Product(SKU, Name, Brand, Category, Sale_Price, Price, Option, Date) VALUES (?, ?, ?, ?, ?, ?, ?,?)",
                (item.sku, item.name, item.brand, item.category, item.sale_price, item.old_price, item.option, formatted_datetime)
            )
            conn.commit()
            print(item)

print("done")

query = "SELECT * FROM Product"
df = pd.read_sql_query(query, conn)
df = df.reset_index(drop=True)
df.to_excel('BulkReefSupplyProduct.xlsx', index=False, engine='openpyxl')

cursor.close()
conn.close()
driver.quit()

'''
print(sub_product_links)
for sub_link in sub_product_links:
    time.sleep(random.randint(2, 4))
    driver.get(sub_link)
    print(f'sub link {sub_link}')
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, '//ol[@class="products list items product-items"]/li')
        )
    )
    sub_product_list = driver.find_elements(By.XPATH, '//ol[@class="products list items product-items"]/li')
    for product in category_product_list:
        product_status = get_Item_Status(product)
        item = Get_Product_Info(product, product_status)
        cursor.execute(
            "INSERT INTO Product(SKU, Name, Brand, Category, Sale_Price, Price, Option) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (item.sku, item.name, item.brand, item.category, item.sale_price, item.old_price, item.option)
        )
        conn.commit()
        print(item)
'''