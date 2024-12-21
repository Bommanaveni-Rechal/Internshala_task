from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

# Function to initialize the WebDriver
def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
# -------------or --------------- for Automatic ChromeDriver Setup --------------
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Function to log in to Amazon
def login_amazon(driver, username, password):
    driver.get("https://www.amazon.in/ap/signin")
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_email"))).send_keys(username, Keys.RETURN)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_password"))).send_keys(password, Keys.RETURN)
    except TimeoutException:
        print("Login failed: Timeout occurred.")
        driver.quit()
        exit()

# Function to scrape product details from a category page
def scrape_category(driver, category_url):
    driver.get(category_url)
    products = []
    try:
        for _ in range(10):  # Adjust scrolling to load sufficient products
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        items = driver.find_elements(By.CSS_SELECTOR, ".zg-item-immersion")
        for item in items[:1500]:
            try:
                product_name = item.find_element(By.CSS_SELECTOR, "div.p13n-sc-truncated").text
                product_price = item.find_element(By.CSS_SELECTOR, ".p13n-sc-price").text
                rating = item.find_element(By.CSS_SELECTOR, "span.a-icon-alt").text
                product_url = item.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                # Visit product page for detailed info
                driver.execute_script("window.open(arguments[0]);", product_url)
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(2)

                try:
                    description = driver.find_element(By.ID, "feature-bullets").text
                    sold_by = driver.find_element(By.ID, "merchant-info").text
                    images = [img.get_attribute("src") for img in driver.find_elements(By.CSS_SELECTOR, "img")] # Collect all image URLs
                except:
                    description, sold_by, images = "N/A", "N/A", []

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                product_data = {
                    "Name": product_name,
                    "Price": product_price,
                    "Rating": rating,
                    "Description": description,
                    "Sold By": sold_by,
                    "Images": images
                }
                products.append(product_data)
            except Exception as e:
                print(f"Error extracting product: {e}")
    except Exception as e:
        print(f"Error in category: {e}")

    return products

# Function to save data to a CSV file
def save_to_csv(data, filename):
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

# Main function
def main():
    username = "your_email@example.com"
    password = "your_password"
    category_urls = [
        "https://www.amazon.in/gp/bestsellers/kitchen",
        "https://www.amazon.in/gp/bestsellers/shoes",
        "https://www.amazon.in/gp/bestsellers/computers",
        "https://www.amazon.in/gp/bestsellers/electronics",
        "https://www.amazon.in/gp/bestsellers/books",
        "https://www.amazon.in/gp/bestsellers/toys",
        "https://www.amazon.in/gp/bestsellers/sports",
        "https://www.amazon.in/gp/bestsellers/beauty",
        "https://www.amazon.in/gp/bestsellers/grocery",
        "https://www.amazon.in/gp/bestsellers/automotive"
    ]

    driver = initialize_driver()
    login_amazon(driver, username, password)

    all_products = []
    for url in category_urls:
        print(f"Scraping category: {url}")
        category_products = scrape_category(driver, url)
        all_products.extend(category_products)

    save_to_csv(all_products, "amazon_best_sellers.csv")
    print("Data saved to amazon_best_sellers.csv")
    driver.quit()

if __name__ == "__main__":
    main()
