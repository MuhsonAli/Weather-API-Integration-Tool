import requests
from bs4 import BeautifulSoup
import csv

base_url = "https://books.toscrape.com/index.html"
base_page = requests.get(base_url)
soup = BeautifulSoup(base_page.content, 'html.parser')
#print(soup)
container = soup.find('ul', class_='nav nav-list')

#here we get the working urls for each category link
category_links = []
for a_tag in container.findAll('a'):
    href = a_tag['href']
    category_links.append('https://books.toscrape.com/' + href)
del category_links[0]

#get next page links
all_urls = []
#for loop iterates over each cat link
for index in category_links:
    current_page = index
    #while loops, loops until there is no next page
    while True:
        next_page = requests.get(current_page, timeout=30)
        next_soup = BeautifulSoup(next_page.content, 'html.parser')
        next_container = next_soup.find('li', class_='next')
        #if next url not found, if statement is bypassed and while breaks, going back to for loop
        if next_container:
            next_page_url = next_container.find('a')['href']
            current_page = '/'.join(current_page.split('/')[:-1]) + '/' + next_page_url
            all_urls.append(current_page)
        else:
            break
category_links.extend(all_urls)

#store raw data of every url link
raw_books_data = []
for cat_urls in category_links:
    response_page = requests.get(cat_urls, timeout=30)
    new_soup = BeautifulSoup(response_page.content, "html.parser")
    raw_data = new_soup.findAll('article', class_='product_pod')
    raw_books_data.append(raw_data)

#get every title and raw link to each book
raw_books_links = []
titles = []
for index in raw_books_data:
    for i in index:
        h3_tag = i.find('h3')
        if h3_tag:
            a_tag = h3_tag.find('a')
            if a_tag:
                title = a_tag.get('title')
                book_links = a_tag.get('href')
                titles.append(title)
                raw_books_links.append(book_links)

#clean and concatenate every raw book link
new_base_url = 'https://books.toscrape.com/catalogue'
part_to_remove = '../../..'
final_books_url = []
full_books_url = []
for raw_url in raw_books_links:
    clean_url = new_base_url + raw_url.replace(part_to_remove, '')
    final_books_url.append(clean_url)

# #get raw data on each book
raw_table_data = []
for index_urls in final_books_url:
    book_page = requests.get(index_urls, timeout=30)
    soup3 = BeautifulSoup(book_page.content, 'html.parser')
    page_content = soup3.find('table', class_='table table-striped')
    for index in page_content.findAll('td'):
        raw_table_data.append(index.get_text(strip=True))

#organize raw book data via dict
sorted_table_date = []
for i in range(0, len(raw_table_data), 7):
    table_data_dict = {
        'UPC': raw_table_data[i],
        'Product Type': raw_table_data[i+1],
        'Price': raw_table_data[i+2],
        'Price After Tax': raw_table_data[i+3],
        'Tax': raw_table_data[i+4],
        'Stock': raw_table_data[i+5],
        'Reviews': raw_table_data[i+6]
    }
    sorted_table_date.append(table_data_dict)

#add title to each list
for i, val in enumerate(titles):
    sorted_table_date[i]['Title:'] = val
for i in sorted_table_date:
    print(i)

filename = "mod4_final_books_data.csv"
fieldnames = ['Title:', 'UPC', 'Product Type', 'Price', 'Price After Tax', 'Tax', 'Stock', 'Reviews']
with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for book in sorted_table_date:
        writer.writerow(book)

