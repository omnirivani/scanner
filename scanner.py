from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import re
from tabulate import tabulate
import time


# Change these global variables for your use case as needed!
LOOK_FOR_MULTIPLE_PRODUCTS = False
MAX_PAGES = 5
IGNORE_JUMBO_CARDS = True


# Display loading message with dots during waits
def loading_msg(msg):
    print(msg, end="", flush=True)
    for _ in range(3):
        time.sleep(0.5)
        print(".", end="", flush=True)
    print()


# function using regex to separate search term into 3 variables
def parse_searchterm(search):
    # Look for a pattern of name, number, condition, pg number such as "charizard ex #105/112 nm p5". Allow accidental whitespace
    pattern = r"(.+)\s+#([\w/]+)(?:\s+(?!p(?:age)?\d*|pg\d*)(\w+))?(?:\s+(?:p|pg|page)\s*(\d+))?\s*$"
    match = re.match(pattern, search.strip(), re.IGNORECASE)

    # extract variables
    if match:
        name, number, condition, pg = match.groups()
        if not condition:
            condition = "unspecified"
        if not pg:
            pg = MAX_PAGES
        return name.strip(), number.strip().upper(), condition.lower(), int(pg)
    else:
        raise ValueError("Search term must be in a format like 'charizard ex #105/112 nm p4'")


# Get each product information on the current page
def get_product_links(html, number, pg):
    soup = BeautifulSoup(html, "html.parser")
    search_results = soup.find("section", class_="search-results")
    products = []
    
    # Look through each search result 
    for card in search_results.find_all("div", class_="product-card"):
        product_id = None
        spans = card.find_all("span")
        for span in spans:
            if span.text.startswith("#"):
                product_id = span.text.strip()
                break
        # If product ID not found, go next
        if not product_id:
            continue
        # If the product ID matches the number we are looking for
        if number in product_id:
            # Get product name
            name_elem = card.find("span", class_="product-card__title truncate")
            name = name_elem.text.strip() if name_elem else "Unknown Product"

            # Get product set
            set_elem = card.find("h4", class_="product-card__set-name")
            set = set_elem.text.strip() if set_elem else "Unknown Set"
            
            # Skip over jumbo cards if bool is true
            if IGNORE_JUMBO_CARDS and "Jumbo Cards" in set:
                continue

            market_price_elem = card.find("span", class_="product-card__market-price--value")
            market_price = market_price_elem.text.strip() if market_price_elem else "N/A"

            # Filter out 'a' tags that don't have href attributes
            link = card.find("a", href=True)
            if link:
                product = {"name": name,
                           "set": set,
                           "id": product_id,
                           "url": link["href"],
                           "market price": market_price
                        }
                products.append(product)
                print(f"Found matching product on page {pg}")
                
    return products


# See if there exists a next page
def check_next_page(html, page):
    soup = BeautifulSoup(html, "html.parser")
    pagination = soup.find("div", class_="tcg-pagination__pages")
    for page_link_button in pagination.find_all("a", class_="is-active router-link-exact-active tcg-button tcg-button--md tcg-standard-button tcg-standard-button--flat"):
        button_number = page_link_button.text.strip()
        if int(button_number) > page:
            # If next page number is greater than current page, there exists a next page
            return True
    # If no page number is greater than current page, there is no next page
    print(f"No page {page+1} found")
    return False


# Search multiple result pages until product is found or limit reached
def get_all_product_links(driver, name, number, page):
    products = []
    # initial page number
    pg = 1
    max_pages = page
    while pg <= max_pages:
        print(f"Checking page {pg}...")
        url = f"https://www.tcgplayer.com/search/all/product?&q={name.replace(' ', '+')}&page={pg}"
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "search-results"))
            )
        except TimeoutException:
            print("Timed out while looking for products. Please try again.")

        html = driver.page_source
        page_products = get_product_links(html, number, pg)
        products.extend(page_products)

        # Toggle for first match or look for multiple matching products
        if not LOOK_FOR_MULTIPLE_PRODUCTS and products:
            break

        if check_next_page(html, pg):
            pg += 1
        else:
            break
    print(products)

    return products


# Allow user to choose product if multiple are found with same number
def choose_product(product_links):
    choice = 0
    if len(product_links) > 1:
        print("\nMultiple products found with same number:")
        for idx, product in enumerate(product_links):
            print(f"{idx+1}: {product['name']} | Set: {product['set']} | Market Price: {product['market price']} | ID: {product['id']}")
    
        while True:
            try:
                choice = int(input("Select product number to lookup: ")) - 1
                if 0 <= choice < len(product_links):
                    selected_link = product_links[choice]["url"]
                    break
                else:
                    print("Invalid selection. Try again.")
            except ValueError:
                print("Please enter a valid number.")
    else:
        selected_link = product_links[0]["url"]

    return selected_link, choice


# Format product link to include condition filter
def format_product_url(product_link, condition):
    url = "https://www.tcgplayer.com"

    # Append condition to product link
    url_suffix = ""
    match condition:
        # By default, if condition is not specified, use "Near Mint"
        case "unspecified":
            url_suffix = None
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
    if url_suffix == None:
        formatted = url + product_link

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

        # Make sure to handle cases when data is not present
        price = price_td.text.strip() if price_td else "N/A"
        date = date_td.text.strip() if date_td else "N/A"
        quantity = quantity_td.text.strip() if quantity_td else "N/A"

        # Also get condition of card sold
        # Sometimes the class is displayed differently on different devices, so check for both
        toggle = sale.select_one(".tcg-tooltip__toggle, .tcg-tooltiptoggle")
        # The div containing 'condition' is toggleable(has children), so need to get only the first text node
        if toggle:
            # Get only the direct text, not from children
            condition = toggle.find(string=True, recursive=False).strip()
        else:
            condition = "N/A"

        # Create dictionary for each sale, then add to the list
        sale_data = {"Price": price, "Date": date, "Quantity": quantity, "Condition": condition}
        sales_data.append(sale_data)
    
    return sales_data


if __name__ == "__main__":

    # Use same driver for all future searches
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(options=chrome_options)
    # Keep prompting for input until user exits
    while True:
        search = input("\nEnter card search (or type 'exit' to quit): ")
        if search.strip().lower() == "exit":
            print("Exiting...")
            break
        try:
            name, number, condition, page = parse_searchterm(search)
            print(f"Searching for: name='{name}', number='{number}', condition='{condition}', pages to search={page}")
        except ValueError as e:
            print(e)
            continue

        # Search through pages for the product
        product_links = get_all_product_links(driver, name, number, page)
        # If no results, reprompt user
        if not product_links:
            print(f"Could not find that product within {page} pages. Retry your query or increase MAX_PAGES near the top of the file\n")
            continue

        # If multiple products found, let user choose
        selected_link, product_index = choose_product(product_links)

        # Add condition to product link
        formatted_product_url = format_product_url(selected_link, condition)

        # Now navigate to formatted link to view more information
        driver.get(formatted_product_url)
        loading_msg("Loading product data")

        # Wait for button to load
        try:
            view_more_data_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "modal__activator"))
            )
        except TimeoutException:
            print("Timed out waiting for data to load. Please try again.")
            continue

        # If condition filter fails, inform the user
        # Let JS load
        time.sleep(1)
        # If no results msg is not found, no_result will return an empty list
        no_results = driver.find_elements(By.CLASS_NAME, "no-result__heading")
        # Check if list is populated with something
        if no_results:
            print(f"***No search results found for condition: '{condition}'. Now displaying recent 5 sales without condition filter.***")
            condition = "unspecified"
        
        # Click button to view sale data
        view_more_data_button.click()

        # Wait for table to load before getting html
        time.sleep(1)
        table_elem = driver.find_element(By.CLASS_NAME, "latest-sales-table__tbody")
        html_table = table_elem.get_attribute("outerHTML")

        # Extract sales data from page source
        sales_data = parse_data(html_table)

        # Print out data in a table format
        print(f"\nSales Data for: {name} #{number}, condition: {condition}")
        print(f"Market Price: {product_links[product_index]['market price']}")
        print(tabulate(sales_data, headers="keys", tablefmt="pretty"))

