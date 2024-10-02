from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
import random
import time


from Product import Product # class file

''' occasionally name will be confused for SKU -> because of "choose options" button OR out of stock '''
''' could go back to sku as key then '''


# CAN ALSO COLLECT IF THE ITEM is IN STOCK / OUT OF STOCK / DISCONTINUED

# CHECK IF SKU is not INT ?


def Get_Bulk_Reef_Supply(driver, cursor, conn) -> list:
    WebDriverWait(driver, 10).until(  # Wait to find list of categories
        EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@id, "narrow-by-list2")]/div/ul[contains(@class, "items")]')))
    anchors = driver.find_elements(By.XPATH, '//div[contains(@id, "narrow-by-list2")]/div/ul[contains(@class, "items")]/li/a')
    link_urls = [anchor.get_attribute('href') for anchor in anchors]  # Extract href attribute

    for link in link_urls:  # Scrape each category link
        product_list = Get_Products(Driver=driver, URL=link)  # find list of products

        for product in product_list:  # Collect product information for each product
            item = scrape_product_info(product)
            # Print extracted information
            print(f" - Product Name {item.name} \n- Brand: {item.brand}, \n- SKU {item.sku}, \n- Category: {item.category}, \n- Sale Price: {item.sale_price}, \n- Old Price: {item.old_price}")

            cursor.execute(
                "INSERT INTO Product(SKU, Name, Brand, Category, Sale_Price, Price) VALUES (?, ?, ?, ?, ?, ?)",
                (item.sku, item.name, item.brand, item.category, item.sale_price, item.old_price))
            conn.commit()
            time.sleep(random.uniform(2, 5))

# Returns List of links for each category
def Get_Products(Driver, URL):
    Driver.get(URL)  # Go To -> (category page)

    WebDriverWait(Driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, '//ol[@class="products list items product-items"]/li/[@class="product-item-info"]')))

    # Extract the product list
    product_list = Driver.find_elements(By.XPATH, '//ol[@class="products list items product-items"]/li/[@class="product-item-info"]')

    return product_list


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
def Get_Product(product,option):

    if option == 'Add to Cart':
        # Extract product information for each product on the page
        product_sku = product.get_attribute("data-product-sku")
        product_name = product.get_attribute("data-product-title")
        product_brand = product.get_attribute("data-product-brand")
        product_category = product.get_attribute("data-product-category")
        old_price = price_check(product, selector=".price-wrapper.price.brs-product-price-old")
        sale_price = price_check(product, selector=".price-wrapper.price.brs-product-price-current")

        item = Product(name=product_name, brand=product_brand, sku=product_sku, category=product_category,
                       sale_price=sale_price, old_price=old_price)
        return item
    elif option == 'CHOOSE OPTIONS':


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


if __name__ == "__main__":
    main()



def Check_Option(driver):
    # Check if the product is discontinued
    try:
        discontinued_element = driver.find_element(By.XPATH, '//div[contains(text(), "Discontinued by Bulk Reef Supply")]')
        if discontinued_element.is_displayed():
            return  # call Get_Product() with option 'discontinued'
    except NoSuchElementException:
        pass

    # Check if the "Notify Me When In-Stock" button is displayed
    try:
        notify_me_button = driver.find_element(By.XPATH,'//button[contains(@class, "brs-notify-me") and @title="Notify Me When In-Stock"]')
        if notify_me_button.is_displayed():
            # call Get_Product() with option 'out of stock'
    except NoSuchElementException:
        pass

    # Check if the "Add to Cart" button is displayed
    try:
        add_to_cart_button = driver.find_element(By.XPATH,'//button[contains(@class, "tocart") and @title="Add to Cart"]')
        if add_to_cart_button.is_displayed():
            # call Get_Product() with option 'in stock'
    except NoSuchElementException:
        pass

    try:
        # Check if the "Choose Options" button is displayed
        choose_options_button = driver.find_element(By.XPATH, '//button[contains(text(), "Choose Options")]')
        if choose_options_button.is_displayed():
            # call to get products of sub page then call get_product for each product on sub page
            #
    except NoSuchElementException:
        print("Could not find any of the expected buttons or statuses.")


def get_choose_options_link(driver):
    try:
        # Locate the "Choose Options" anchor element
        choose_options_link = driver.find_element(By.XPATH,'//a[contains(@class, "brs-choose-options") and text()="Choose Options"]')
        # Extract the href attribute (link)
        link = choose_options_link.get_attribute('href')
        print(f"Choose Options link: {link}")

        return link  # You can return the link for further processing if needed

    except NoSuchElementException:
        print("No 'Choose Options' button found on the page.")
        return None



'''



'''