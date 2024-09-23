from bs4 import BeautifulSoup
import requests

# Define the URL you want to scrape
url = "https://www.bulkreefsupply.com/radion-xr30-g6-pro-led-light-fixture-ecotech-marine.html"

# Send a request to the webpage
result = requests.get(url)

# Check if the request was successful
if result.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(result.text, 'html.parser')

    # Find the brand name (within the <a> tag)
    brand = soup.find('a', href="https://www.bulkreefsupply.com/brands/ecotech-marine.html").text.strip()

    # Find the item name (within the <span> tag with specific class)
    item_name = soup.find('span', class_="base", itemprop="name").text.strip()

    # Find the price (within the <span> tag with specific attributes)
    price = soup.find('span', id="product-price-14459", class_="price-wrapper").text.strip()

    # Print the scraped information
    print(f"Brand: {brand}")
    print(f"Item Name: {item_name}")
    print(f"Price: {price}")

else:
    print(f"Failed to retrieve the webpage. Status code: {result.status_code}")


'''
url = "https://www.bulkreefsupply.com/gryphon-xl-aquasaw-diamond-band-frag-saw.html"

result = requests.get(url)

doc = BeautifulSoup(result.text, "html.parser")
#print(doc.prettify())

all_prices = doc.find_all(string=lambda text: text and text.startswith("$"))

# Print each price
for price in all_prices:
    print(price.strip())

#parent = prices[0].parent
#print(parent)
#strong = parent.find("strong")
#print(strong.string)


with open("index.html", "r") as f:
    doc = BeautifulSoup(f, "html.parser")

#tag = doc.title.string
tag = doc.find_all("p")[0]
print(tag.find_all("b"))
'''


##########


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://www.bulkreefsupply.com/specials.html") # Open the desired webpage

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "items"))
)

items_container = driver.find_element(By.CLASS_NAME, "items")

WebDriverWait(driver, 5).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "item"))
)

items = driver.find_elements(By.CLASS_NAME, "item")

# Step 2: Find all the item elements within the container
item_elements = items_container.find_elements(By.CLASS_NAME, "item")

# Step 3: Loop through each item and extract the link
for item in item_elements:
    link_element = item.find_element(By.TAG_NAME, "a")
    link = link_element.get_attribute("href")
    print(link)
driver.quit()

################