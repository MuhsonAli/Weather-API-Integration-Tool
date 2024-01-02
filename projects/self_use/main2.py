import requests
from bs4 import BeautifulSoup
import csv

base_url = "https://books.toscrape.com/catalogue/category/books/horror_31/index.html"
base_page = requests.get(base_url)
soup = BeautifulSoup(base_page.content, "html.parser")
containers = soup.findAll('article', class_='product_pod')
#print(containers[1])
#get raw urls
book_links = []
for book in containers:
    a_tag = book.find('a')
    if a_tag is not None:
        href = a_tag.get('href')
        if href:
            book_links.append(href)
#print(book_links)
#concatenate urls
absolute_urls = []
for index_urls in book_links:
    urls = base_url + index_urls
    absolute_urls.append(urls)
#clean urls
part_to_remove = "category/books/horror_31/index.html../../.."
cleaned_absolute_urls = []
for url in absolute_urls:
    cleaned_url = url.replace(part_to_remove, "")
    cleaned_absolute_urls.append(cleaned_url)

raw_book_data = []
final_book_data = []
raw_titles = []
final_titles = []
for index_urls in cleaned_absolute_urls:
    link_page = requests.get(index_urls)
    soup = BeautifulSoup(link_page.content, "html.parser")
    raw_book_data = soup.find("table", class_="table table-striped")
    raw_titles = soup.find("li", class_="active")
    for index, val in enumerate(raw_book_data.find_all('td')):
        final_book_data.append(val.get_text(strip=True))
    for index2, val2 in enumerate(raw_titles):
        final_titles.append(val2.get_text(strip=True))
#print(final_titles)

sorted_final_book_data = []
for i in range(0, len(final_book_data), 7):
    book_data_dict = {
        'UPC': final_book_data[i],
        'Product Type': final_book_data[i+1],
        'Price': final_book_data[i+2],
        'Price After Tax': final_book_data[i+3],
        'Tax': final_book_data[i+4],
        'Stock': final_book_data[i+5],
        'Reviews': final_book_data[i+6]
    }
    sorted_final_book_data.append(book_data_dict)
print(sorted_final_book_data)

for i, val in enumerate(final_titles):
    sorted_final_book_data[i]['Title:'] = val
for i in sorted_final_book_data:
    print(i)

filename = "books_data.csv"
fieldnames = ['Title:', 'UPC', 'Product Type', 'Price', 'Price After Tax', 'Tax', 'Stock', 'Reviews']
with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for book in sorted_final_book_data:
        writer.writerow(book)























