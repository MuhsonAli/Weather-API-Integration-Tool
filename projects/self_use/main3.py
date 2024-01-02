import requests
import csv
from bs4 import BeautifulSoup

#here we get every primary category link
def get_category_links(base_url):
    base_page = requests.get(base_url)
    soup = BeautifulSoup(base_page.content, 'html.parser')
    container = soup.find('ul', class_='nav nav-list')
    category_links = []
    for a_tag in container.findAll('a'):
        href = a_tag['href']
        category_links.append('https://books.toscrape.com/' + href)
    del category_links[0]
    return category_links

#here we get every next page link and combine it with category link
def get_next_page(category_links):
    all_urls = [category_links]
    while True:
        response = requests.get(category_links, timeout=30)
        next_soup = BeautifulSoup(response.content, 'html.parser')
        next_container = next_soup.find('li', class_='next')
        if next_container:
            next_page_url = next_container.find('a')['href']
            category_links = '/'.join(category_links.split('/')[:-1]) + '/' + next_page_url
            all_urls.append(category_links)
        else:
            break
    return all_urls


#here we get the raw book links and titles
def scrape_data(all_urls):
    raw_book_links = []
    book_titles = []
    for url in all_urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        container = soup.findAll('article', class_='product_pod')
        for book in container:
            title = book.find('h3').find('a')['title']
            href = book.find('h3').find('a')['href']
            raw_book_links.append(href)
            book_titles.append(title)
    return raw_book_links, book_titles


def clean_book_links(raw_book_links):
    new_base_url = 'https://books.toscrape.com/catalogue'
    part_to_remove = '../../..'
    final_books_url = []
    for raw_url in raw_book_links:
        clean_url = new_base_url + raw_url.replace(part_to_remove, '')
        final_books_url.append(clean_url)
    return final_books_url

def get_book_details(final_books_url):
    raw_table_data = []
    for url in final_books_url:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        container = soup.find('table', class_='table table-striped')
        container2 = container.findAll('td')
        for index in container2:
            raw_table_data.append(index.get_text(strip=True))
    return raw_table_data

def sort_book_data(raw_table_data, titles):
    sorted_table_date = []
    for i in range(0, len(raw_table_data), 7):
        table_data_dict = {
            'Title': titles[i // 7],
            'UPC': raw_table_data[i],
            'Product Type': raw_table_data[i + 1],
            'Price': raw_table_data[i + 2],
            'Price After Tax': raw_table_data[i + 3],
            'Tax': raw_table_data[i + 4],
            'Stock': raw_table_data[i + 5],
            'Reviews': raw_table_data[i + 6]
        }
        sorted_table_date.append(table_data_dict)
    return sorted_table_date

def write_to_csv(sorted_data, category_name):
    filename = f"{category_name}_data.csv"
    fieldnames = ['Title', 'UPC', 'Product Type', 'Price', 'Price After Tax', 'Tax', 'Stock', 'Reviews']
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for book in sorted_data:
            writer.writerow(book)


def main():
    base_url = "https://books.toscrape.com/index.html"
    cat_links = get_category_links(base_url)

    for category_link in cat_links:
        all_urls = get_next_page(category_link)
        data_scrape, book_titles = scrape_data(all_urls)
        final_book_links = clean_book_links(data_scrape)
        book_data = get_book_details(final_book_links)
        sorted_data = sort_book_data(book_data, book_titles)

        category_name = category_link.split('/')[-2]
        write_to_csv(sorted_data, f"{category_name}.csv")



if __name__ == "__main__":
    main()












