# Loop through each product
for product in product_list:
    product_name = product.get_attribute("data-product-title")

    # Check if the item is out of stock
    try:
        out_of_stock_button = product.find_element(By.CSS_SELECTOR, "button.brs-notify-me")
        print(f"{product_name} is out of stock.")
        continue  # Skip to the next product since this one is out of stock
    except:
        # No out-of-stock button, so item is available
        print(f"{product_name} is in stock.")

    # Check if the item has more options (like a "Choose Options" button)
    try:
        more_options_button = product.find_element(By.CSS_SELECTOR, "a.brs-choose-options")
        options_url = more_options_button.get_attribute("href")
        print(f"{product_name} has more options. Navigating to {options_url}...")

        # Navigate to the options page to scrape additional details
        driver.get(options_url)

        # Wait for the product details on the new page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "li.item.product.product-item.brs-product-cta-container"))
        )

        # Scrape the additional options here as needed
        # You can repeat the scraping logic for price, SKU, etc.
        product_list_options = driver.find_elements(By.CSS_SELECTOR,
                                                    "li.item.product.product-item.brs-product-cta-container")
        for option in product_list_options:
            # Scrape each option's details similar to your main scraping logic
            option_name = option.get_attribute("data-product-title")
            option_sku = option.get_attribute("data-product-sku")
            option_price = option.find_element(By.CSS_SELECTOR, ".price-wrapper").get_attribute("data-product-price")
            print(f"Option: {option_name}, SKU: {option_sku}, Price: {option_price}")

            # Insert data into the database as needed
            cursor.execute("INSERT INTO Product(SKU, Name, Price) VALUES (?, ?, ?)",
                           (option_sku, option_name, option_price))
            conn.commit()

        # After scraping options, go back to the category page
        driver.back()
    except:
        print(f"{product_name} does not have additional options.")

    # Continue with scraping price, SKU, etc., for the in-stock items
    try:
        sale_price = product.find_element(By.CSS_SELECTOR,
                                          ".price-wrapper.price.brs-product-price-current").get_attribute(
            "data-product-price")
    except:
        sale_price = None

    try:
        old_price = product.find_element(By.CSS_SELECTOR, ".price-wrapper.price.brs-product-price-old").get_attribute(
            "data-product-price")
    except:
        old_price = None

    print(f"Product: {product_name}, Sale Price: {sale_price}, Old Price: {old_price}")

    # Insert product data into the database
    cursor.execute("INSERT INTO Product(SKU, Name, Sale_Price, Price) VALUES (?, ?, ?, ?)",
                   (product_sku, product_name, sale_price, old_price))
    conn.commit()

    # Random delay to avoid getting flagged by the website
    time.sleep(random.uniform(2, 5))