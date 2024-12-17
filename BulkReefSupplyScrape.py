from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3

from Product import Product

''' last step is to go to the sub pages'''
''' also instead of just find_elements do find_all_elements then loop through those ? instead of the different cases?? '''

def Get_Bulk_Reef_Supply(driver, cursor, conn) -> list:
    WebDriverWait(driver, 10).until(  # Wait to find list of categories
        EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@id, "narrow-by-list2")]/div/ul[contains(@class, "items")]')))
    anchors = driver.find_elements(By.XPATH, '//div[contains(@id, "narrow-by-list2")]/div/ul[contains(@class, "items")]/li/a')
    link_urls = [anchor.get_attribute('href') for anchor in anchors]  # Extract href attribute

    for link in link_urls:  # Scrape each category link
        product = Get_Products_from_Category(Driver=driver, URL=link)  # find list of products
        ParseItems(driver, product, cursor, conn) ##########

# Returns List of links for each category
def Get_Products_from_Category(Driver, URL):
#    try:
    Driver.get(URL)  # goto -> (category page)
    WebDriverWait(Driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, '//ol[@class="products list items product-items"]/li')))
    # Extract the product list
    products = Driver.find_elements(By.XPATH, '//ol[@class="products list items product-items"]/li')
    return products

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
def Get_Product(product, option):
    if option == 'in-stock' or 'unavailable' or 'discontinued':
        # Extract product information for each product on the page
        product_sku = product.get_attribute("data-product-sku")
        product_name = product.get_attribute("data-product-title")
        product_brand = product.get_attribute("data-product-brand")
        product_category = product.get_attribute("data-product-category")
        old_price = price_check(product, selector=".price-wrapper.price.brs-product-price-old")
        sale_price = price_check(product, selector=".price-wrapper.price.brs-product-price-current")

        item = Product(name=product_name, brand=product_brand, sku=product_sku, category=product_category,
                       sale_price=sale_price, old_price=old_price, option=option)
        return item
    else:
        return None


def main():
    conn = sqlite3.connect('Bulk_Reef_Supply_DB')  # connect to database
    cursor = conn.cursor()  # create cursor object to interact with database

    driver = webdriver.Chrome()  # Initialize the driver
    driver.get("https://www.bulkreefsupply.com/specials.html")  # get bulk reef supply home page

    Get_Bulk_Reef_Supply(driver, cursor, conn)  # grab links from landing page
    print("done")
    # close database
    cursor.close()
    conn.close()
    # Close the browser
    driver.quit()

def ParseItems(Driver, products, cursor, conn):
    items = []  # List to store main product items
    sub_product_links = []  # List to store URLs of products with 'Choose Options'

    for product in products:
        option = None
        item = None

        try:
            # Check if the "Notify Me When In-Stock" button is displayed
            notify_me_button = product.find_element(By.XPATH, '//button[contains(@class, "brs-notify-me") and @title="Notify Me When In-Stock"]')
            if notify_me_button.is_displayed():
                option = 'unavailable'
                item = Get_Product(product, option)

        except NoSuchElementException:
            pass

        try:
            # Check if the "Add to Cart" button is displayed
            add_to_cart_button = product.find_element(By.XPATH, '//button[contains(@class, "tocart") and @title="Add to Cart"]')
            if add_to_cart_button.is_displayed():
                option = 'in-stock'
                item = Get_Product(product, option)

        except NoSuchElementException:
            pass

        try:
            # Check if the "Discontinued" element is displayed
            discontinued_element = product.find_element(By.XPATH, '//div[contains(text(), "Discontinued by Bulk Reef Supply")]')
            if discontinued_element.is_displayed():
                option = 'discontinued'
                item = Get_Product(product, option)

        except NoSuchElementException:
            pass

        # Handle cases where the "Choose Options" button is visible
        try:
            choose_options_button = product.find_element(By.XPATH, '//button[contains(text(), "Choose Options")]')
            if choose_options_button.is_displayed():
                option = 'choose-options'
                item = Get_Product(product, option)  # Get the main product details

                # Process the main product before saving the link to the options page
                if item:
                    items.append(item)
                    print(f" - Product Name: {item.name}\n- Brand: {item.brand}\n- SKU: {item.sku}\n- Category: {item.category}\n- Sale Price: {item.sale_price}\n- Old Price: {item.old_price}\n- Option: {item.option}")
                    cursor.execute(
                        "INSERT INTO Product(SKU, Name, Brand, Category, Sale_Price, Price, Option) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (item.sku, item.name, item.brand, item.category, item.sale_price, item.old_price, item.option)
                    )
                    conn.commit()

                    # Capture the URL of the options page
                    link_element = product.find_element(By.XPATH, './/div/div/div[4]/div/div[1]/a[1]')
                    URL = link_element.get_attribute('href')
                    sub_product_links.append(URL)  # Save this link to be revisited later

        except NoSuchElementException:
            pass

        # If a valid item was found and has a numeric SKU, process it
        if item and item.sku and item.sku.isdigit():
            items.append(item)
            print(f" - Product Name: {item.name}\n- Brand: {item.brand}\n- SKU: {item.sku}\n- Category: {item.category}\n- Sale Price: {item.sale_price}\n- Old Price: {item.old_price}\n- Option: {item.option}")
            cursor.execute(
                "INSERT INTO Product(SKU, Name, Brand, Category, Sale_Price, Price, Option) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (item.sku, item.name, item.brand, item.category, item.sale_price, item.old_price, item.option)
            )
            conn.commit()

    # After processing the main product list, revisit the sub-product pages
    for sub_link in sub_product_links:
        try:
            Driver.get(sub_link)  # Go to the options page

            WebDriverWait(Driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//ol[@class="products list items product-items"]/li[@class="product-item-info"]')
                )
            )

            # Extract sub-products and process them
            sub_products = Driver.find_elements(By.XPATH, '//ol[@class="products list items product-items"]/li[@class="product-item-info"]')
            ParseItems(Driver, sub_products, cursor, conn)  # Process the sub-products recursively

        except Exception as e:
            print(f"Failed to process sub-products for URL: {sub_link} - Error: {e}")

if __name__ == "__main__":
    main()