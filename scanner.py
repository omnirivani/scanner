from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

card_name = input("Enter name of product to search: ")
search = f"https://www.tcgplayer.com/search/pokemon/product?productLineName=pokemon&q={card_name.replace(' ', '+')}"


driver = webdriver.Chrome()
driver.get(search)
# Wait for javascript to load  before getting pg src
WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.CLASS_NAME, "search-results"))
)
html = driver.page_source
driver.quit()
soup = BeautifulSoup(html, "html.parser")
search_results = soup.find("section", class_="search-results")
print(f"Number of products found: {len(list(search_results.children))}")
for child in search_results.children:
    print(f"product name: {child.find('span', class_='product-card__title truncate').text}")
    print(f"product set: {child.find('div', class_='product-card__set-name__variant').text}")
    rarity = child.find('div', class_='product-card__rarity__variant')
    if rarity:
        print(f"product rarity: {rarity.text}")
    else:
        print("SEALED PRODUCT")
    print(f"product price: {child.find('span', class_='product-card__market-price--value').text}")
    print("###############################")





