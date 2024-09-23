from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
import random
import time

''' occasionally name will be confused for SKU -> because of "choose options" button OR out of stock '''
''' could go back to sku as key then '''


# CAN ALSO COLLECT IF THE ITEM is IN STOCK / OUT OF STOCK / DISCONTINUED


conn = sqlite3.connect('Bulk_Reef_Supply_DB')  # connect to database
cursor = conn.cursor()  # create cursor object to interact with database

driver = webdriver.Chrome() # Initialize the driver
driver.get("https://www.bulkreefsupply.com/specials.html")  # get bulk reef supply home page

WebDriverWait(driver, 10).until(  # Wait for and find the anchors of each category page
    EC.presence_of_all_elements_located((By.XPATH, '//*[@id="narrow-by-list2"]/div/ul/li/a'))
)
anchors = driver.find_elements(By.XPATH, '//*[@id="narrow-by-list2"]/div/ul/li/a')

# Extract category page URLs
link_urls = [anchor.get_attribute('href') for anchor in anchors]

# Loop through each category link to scrape products
for url in link_urls[:2]:
    driver.get(url)  # Navigate to the category page

    # Wait for the list of products to load on the page
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.item.product.product-item.brs-product-cta-container"))
    )

    # Extract the product list
    product_list = driver.find_elements(By.CSS_SELECTOR, "li.item.product.product-item.brs-product-cta-container")

    # Extract product information for each product on the page
    for product in product_list:
        product_name = product.get_attribute("data-product-title")
        product_brand = product.get_attribute("data-product-brand")
        product_sku = product.get_attribute("data-product-sku")
        product_category = product.get_attribute("data-product-category")

        # Initialize prices
        sale_price = None
        old_price = None

        # Check for sale price
        sale_price_elements = product.find_elements(By.CSS_SELECTOR, ".price-wrapper.price.brs-product-price-current")
        if sale_price_elements:
            sale_price_data = sale_price_elements[0].get_attribute("data-product-price")
            if sale_price_data is not None:
                sale_price = float(sale_price_data)

        # Check for old price
        old_price_elements = product.find_elements(By.CSS_SELECTOR, ".price-wrapper.price.brs-product-price-old")
        if old_price_elements:
            old_price_data = old_price_elements[0].get_attribute("data-product-price")
            if old_price_data is not None:
                old_price = float(old_price_data)

        # Print extracted information
        print(f"Product Name {product_name} - Product SKU {product_sku} - Sale Price: {sale_price}, Old Price: {old_price}")

        cursor.execute("INSERT INTO Product(SKU, Name, Brand, Category, Sale_Price, Price) VALUES (?, ?, ?, ?, ?, ?)",
                       (product_sku, product_name, product_brand, product_category, sale_price, old_price))

        conn.commit()
        time.sleep(random.uniform(2, 5))

# close database
cursor.close()
conn.close()

# Close the browser
driver.quit()
