import requests
import csv
from bs4 import BeautifulSoup

url = "https://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")

title = soup.find("li", class_= "active")
print(f"Title: {title.string}")

table = soup.find("table", class_= "table table-striped")
table_data = []
for index, val in enumerate(table.find_all("td")):
    table_data.append(val.get_text(strip=True))

UPC = table_data[0]
product_type = table_data[1]
price = table_data[2]
stock = table_data[5]
reviews = table_data[6]
print(f"UPC: {UPC}\nProduct Type: {product_type}\nPrice: {price}\nStock: {stock}\nReviews: {reviews}")

book_data = [title.string, UPC, product_type, price, stock, reviews]
headers = ['Title', 'UPC', 'Product Type', 'Price', 'Stock', 'Reviews']
csv_file = 'book_data.csv'

with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerow(book_data)

