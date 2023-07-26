import csv
import re
import requests
from bs4 import BeautifulSoup


def get_product_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    product_data = []
    products = soup.find_all("div", class_="s-result-item")

    for product in products:
        try:
            product_url = product.find("a", class_="a-link-normal").get("href")
            product_name = product.find(
                "span", class_="a-size-base-plus a-color-base a-text-normal").text.strip()
            product_price = product.find(
                "span", class_="a-price-whole").text.replace(",", "")
            product_rating = product.find(
                "span", class_="a-icon-alt").text.split()[0]

            product_reviews_text = product.find(
                "span", class_="a-size-base").text
            product_reviews = int(
                re.search(r'\d+', product_reviews_text).group())

            product_data.append({
                "Product URL": "https://www.amazon.in" + product_url,
                "Product Name": product_name,
                "Product Price": float(product_price),
                "Rating": float(product_rating),
                "Number of Reviews": product_reviews
            })
        except AttributeError:
            continue

    return product_data


def get_product_details(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    description = soup.find("span", attrs={"id": "productTitle"}).get_text(
        strip=True) if soup.find("span", attrs={"id": "productTitle"}) else "NA"

    asin = soup.find("th", string="ASIN").find_next_sibling("td").get_text(
        strip=True) if soup.find("th", string="ASIN") else "NA"

    product_description = soup.find("div", attrs={"id": "productDescription"}).get_text(
        strip=True) if soup.find("div", attrs={"id": "productDescription"}) else "NA"

    manufacturer = soup.find("a", attrs={"id": "bylineInfo"}).get_text(
        strip=True) if soup.find("a", attrs={"id": "bylineInfo"}) else "NA"

    return {
        "Description": description,
        "ASIN": asin,
        "Product Description": product_description,
        "Manufacturer": manufacturer
    }


if __name__ == "__main__":
    base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{}"
    total_pages = 20

    all_product_data = []
    for page in range(1, total_pages + 1):
        url = base_url.format(page)
        product_data = get_product_data(url)
        all_product_data.extend(product_data)

    all_product_details = []
    for product in all_product_data:
        url = product["Product URL"]
        product_details = get_product_details(url)
        all_product_details.append({**product, **product_details})

    # Export data to CSV
    with open("amazon_products.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Product URL", "Product Name", "Product Price", "Rating",
                      "Number of Reviews", "Description", "ASIN", "Product Description", "Manufacturer"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_product_details)
