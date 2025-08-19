from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re
from tabulate import tabulate
import time

# Display loading message with dots during waits
def loading_msg(msg):
    print(msg, end='', flush=True)
    for _ in range(3):
        time.sleep(0.5)
        print('.', end='', flush=True)
    print()


# function using regex to separate search term into 3 variables
def parse_searchterm(search):
    # Look for a pattern of name, number, condition such as "charizard ex #105/112 nm". Allow accidental whitespace
    pattern = r"(.+)\s+#([\w/]+)(?:\s+(\w+))?\s*$"
    match = re.match(pattern, search.strip(), re.IGNORECASE)

    # extract variables
    if match:
        name, number, condition = match.groups()
        # If condition is not specified, default to "nm" (Near Mint)
        if not condition:
            condition = "nm"
        return name.strip(), number.strip(), condition.lower()
    else:
        raise ValueError("Search term must be in a format like 'charizard ex #105/112 nm'")


def get_search_url(name):    
    # Format the search url by adding name to end
    search_url = f"https://www.tcgplayer.com/search/pokemon/product?productLineName=pokemon&q={name.replace(' ', '+')}"
    return search_url


def get_product_links(html, number):
    soup = BeautifulSoup(html, "html.parser")
    search_results = soup.find("section", class_="search-results")
    products = []

    # Look through each search result 
    for card in search_results.find_all('div', class_='product-card'):
        product_id = None
        spans = card.find_all('span')
        for span in spans:
            if span.text.startswith('#'):
                product_id = span.text.strip()
                break
        # If product ID not found, go next
        if not product_id:
            continue
        # If the product ID matches the number we are looking for
        if number in product_id:
            # Get product name
            name_elem = card.find('span', class_='product-card__title truncate')
            name = name_elem.text.strip() if name_elem else "Unknown Product"

            # Get product set
            set_elem = card.find('h4', class_='product-card__set-name')
            set = set_elem.text.strip() if set_elem else "Unknown Set"

            market_price_elem = card.find('span', class_='product-card__market-price--value')
            market_price = market_price_elem.text.strip() if market_price_elem else "N/A"

            # Filter out 'a' tags that don't have href attributes
            link = card.find('a', href=True)
            if link:
                product = {"name": name,
                           "set": set,
                           "id": product_id,
                           "url": link['href'],
                           "market price": market_price
                        }
                products.append(product)
                
    return products

# Allow user to choose product if multiple are found with same number
def choose_product(product_links):
    if len(product_links) > 1:
        print("\nMultiple products found with same number:")
        for idx, product in enumerate(product_links):
            print(f"{idx+1}: {product['name']} | Set: {product['set']} | Market Price: {product['market price']} | ID: {product['id']}")

        while True:
            try:
                choice = int(input("Select product number to lookup: ")) - 1
                if 0 <= choice < len(product_links):
                    selected_link = product_links[choice]['url']
                    break
                else:
                    print("Invalid selection. Try again.")
            except ValueError:
                print("Please enter a valid number.")
    else:
        selected_link = product_links[0]['url']

    return selected_link


# Format product link to include condition filter
def format_product_url(product_link, condition):
    url = "https://www.tcgplayer.com"

    # Append condition to product link
    url_suffix = ""
    match condition:
        # By default, if condition is not specified, use "Near Mint"
        case None:
            url_suffix = "Near+Mint"
        case "nm":
            url_suffix = "Near+Mint"
        case "lp":
            url_suffix = "Lightly+Played"
        case "mp":
            url_suffix = "Moderately+Played"
        case "hp":
            url_suffix = "Heavily+Played"
        case "d":
            url_suffix = "Damaged"

    formatted = url + product_link + f"&Condition={url_suffix}"
    return formatted


# Get sales data from product page
def parse_data(html):
    # Parse the html with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Create list to store dictionaries that contain sales data
    sales_data = []

    sales_instances = soup.find("tbody", class_="latest-sales-table__tbody")
    for sale in sales_instances.find_all("tr"):
        # Get the data of each sale
        price_td = sale.find("td", class_="latest-sales-table__tbody__price")
        date_td = sale.find("td", class_="latest-sales-table__tbody__date")
        quantity_td = sale.find("td", class_="latest-sales-table__tbody_quantity")
        condition_div = sale.find("div", class_="tcg-tooltip__toggle")

        # Make sure to handle cases when data is not present
        price = price_td.text.strip() if price_td else "N/A"
        date = date_td.text.strip() if date_td else "N/A"
        quantity = quantity_td.text.strip() if quantity_td else "N/A"

        # The condition div is toggleable(has children), so need to get only the first text node
        if condition_div:
            # Get only the direct text, not from children
            condition = condition_div.find(string=True, recursive=False).strip()
        else:
            condition = "N/A"

        # Create dictionary for each sale, then add to the list
        sale_data = {"Price": price, "Date": date, "Quantity": quantity, "Condition": condition}
        sales_data.append(sale_data)
    
    return sales_data


if __name__ == "__main__":
    # Keep prompting for input until user exits
    while True:
        search = input("\nEnter card search (or type 'exit' to quit): ")
        if search.strip().lower() == 'exit':
            print("Exiting...")
            break
        try:
            name, number, condition = parse_searchterm(search)
        except ValueError as e:
            print(e)
            continue

        search_url = get_search_url(name)

        # Navigate to search url with selenium
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1200,800")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(search_url)

        loading_msg("Loading search results")
        # Wait for javascript to load  before getting pg src
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "search-results"))
        )

        # Get the page source after javascript has loaded, then get product link
        html = driver.page_source
        product_links = get_product_links(html, number)
        # If no results, reprompt user
        if not product_links:
            print("No results found for your query. There may be no sales data for that card+condition.")
            driver.quit()
            continue

        # If multiple products found, let user choose
        selected_link = choose_product(product_links)

        # Add condition to product link
        formatted_product_url = format_product_url(selected_link, condition)

        # Now navigate to formatted link to view more information
        driver.get(formatted_product_url)
        loading_msg("Loading product data")

        # Wait for button to load then click "View More Data"
        view_more_data_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "modal__activator"))
        )
        view_more_data_button.click()
        time.sleep(1)
        # Grab html after enough time has passed to update the table
        table_elem = driver.find_element(By.CLASS_NAME, "latest-sales-table__tbody")
        html_table = table_elem.get_attribute("outerHTML")

        # Close driver, as we have our data now
        driver.quit()

        # Extract sales data from page source
        sales_data = parse_data(html_table)

        # Print out data in a table format
        print(f"\nSales Data for: {name} #{number}, {condition.upper()}\n")
        print(tabulate(sales_data, headers="keys", tablefmt="pretty"))

