import requests
import csv
import os
import re
import zipfile
from bs4 import BeautifulSoup


def get_category_links(base_url):
    """
    Extracts and returns all primary category links from the given base URL.
    :param base_url: The base URL of the website from which to scrape category links.
    :return: A list of strings, each string being the URL of a category.
    """
    base_page = requests.get(base_url)
    soup = BeautifulSoup(base_page.content, 'html.parser')
    container = soup.find('ul', class_='nav nav-list')
    category_links = []
    for a_tag in container.findAll('a'):
        href = a_tag['href']
        category_links.append('https://books.toscrape.com/' + href)
    del category_links[0]
    return category_links


def get_next_page(category_links):
    """
    Retrieves all next page URLs for each category.
    :param category_links: The URL of the category for which to retrieve the next page URLs.
    :return: A list of URLs, including the initial category link and any additional next page links.
    """
    all_urls = [category_links]
    while True:
        response = requests.get(category_links, timeout=60)
        next_soup = BeautifulSoup(response.content, 'html.parser')
        next_container = next_soup.find('li', class_='next')
        if next_container:
            next_page_url = next_container.find('a')['href']
            category_links = '/'.join(category_links.split('/')[:-1]) + '/' + next_page_url
            all_urls.append(category_links)
        else:
            break
    return all_urls


def scrape_data(all_urls):
    """
    Scrapes book titles and raw book links from a list of URLs.
    :param all_urls: A list of URLs to scrape for book data.
    :return: A tuple of two lists, one containing raw book links and the other
    containing book titles
    """
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
    """
    Converts raw book links to absolute URLs.
    :param raw_book_links: A list of raw book links to be cleaned.
    :return: A list of cleaned, absolute URLs for the books.
    """
    new_base_url = 'https://books.toscrape.com/catalogue'
    part_to_remove = '../../..'
    final_books_url = []
    for raw_url in raw_book_links:
        clean_url = new_base_url + raw_url.replace(part_to_remove, '')
        final_books_url.append(clean_url)
    return final_books_url

def get_book_details(final_books_url):
    """
    Extracts detailed information and image URLs for each book.
    :param final_books_url: A list of absolute URLs for each book.
    :return: A tuple of two lists, one containing raw table data for each
     book and the other containing image URLs.
    """
    raw_table_data = []
    image_url = []
    base_url = 'https://books.toscrape.com/'
    for url in final_books_url:
        response = requests.get(url, timeout=60)
        soup = BeautifulSoup(response.content, 'html.parser')
        image_container = soup.find('div', class_='image_container')
        if image_container is not None:
            image_tag = image_container.find('img')
            if image_tag is not None:
                image_relative_url = image_tag['src']
                image_absolute_url = base_url + image_relative_url.replace('../../', '')
                image_url.append(image_absolute_url)

        container = soup.find('table', class_='table table-striped')
        container2 = container.findAll('td')

        for index in container2:
            raw_table_data.append(index.get_text(strip=True))
    return raw_table_data, image_url


def sort_book_data(raw_table_data, titles, image_urls):
    """
    Organizes book data into a structured format.
    :param raw_table_data: A list of raw data entries for each book.
    :param titles: A list of titles for each book.
    :param image_urls: A list of image URLs for each book.
    :return: A list of dictionaries, each containing sorted data for a book.
    """
    sorted_table_data = []
    entries_per_book = 7
    num_books = len(titles)
    for i in range(num_books):
        book_data_index = i * entries_per_book
        if i < len(image_urls):
            image_url = image_urls[i]
        else:
            image_url = "No Image Available"

        sorted_table_data.append({
            'Title': titles[i],
            'UPC': raw_table_data[book_data_index],
            'Product Type': raw_table_data[book_data_index + 1],
            'Price': raw_table_data[book_data_index + 2],
            'Price After Tax': raw_table_data[book_data_index + 3],
            'Tax': raw_table_data[book_data_index + 4],
            'Stock': raw_table_data[book_data_index + 5],
            'Reviews': raw_table_data[book_data_index + 6],
            'Image Urls': image_url
        })

    return sorted_table_data

def write_to_csv(sorted_data, category_name):
    """
    Writes sorted book data to a CSV file.
    :param sorted_data: A list of dictionaries, each containing sorted data for a book.
    :param category_name: The name of the book category, used for naming the CSV file.
    :return: None
    """
    filename = f"{category_name}_data.csv"
    fieldnames = ['Title', 'UPC', 'Product Type', 'Price', 'Price After Tax', 'Tax', 'Stock', 'Reviews', 'Image Urls']
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for book in sorted_data:
            writer.writerow(book)


def download_image(sorted_data, category_name):
    """
    Downloads and saves images for each book in the sorted data.
    :param sorted_data: A list of dictionaries, each containing details of a book,
    including its image URL.
    :param category_name: The name of the category, used for organizing saved images
    into directories.
    :return: None
    """
    os.makedirs(category_name)
    for book in sorted_data:
        url = book['Image Urls']
        title = book['Title']
        if url != 'No Image Available':
            response = requests.get(url)
            clean_title = re.sub(r'[\\/*?:"<>|]', "", title)
            clean_title = clean_title.replace(' ', '_')
            image_path = os.path.join(category_name, f'{clean_title}.jpg')
            with open(image_path, 'wb') as file:
                file.write(response.content)


def create_zip(category_name):
    """
    Creates a ZIP file containing the CSV file and all images
    in the specified category directory.
    :param category_name: The name of the category, which is also
    the directory name.
    :return: None
    """
    zip_filename = f'{category_name}.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        csv_filename = f"{category_name}.csv_data.csv"
        csv_filename.replace('.csv_data.csv', '_data.csv')
        zipf.write(csv_filename)
        if os.path.exists(category_name):
            for root, dirs, files in os.walk(category_name):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, category_name))


def main():
    base_url = "https://books.toscrape.com/index.html"
    cat_links = get_category_links(base_url)

    for category_link in cat_links:
        all_urls = get_next_page(category_link)
        raw_book_links, book_titles = scrape_data(all_urls)
        final_book_links = clean_book_links(raw_book_links)
        book_data, image_urls = get_book_details(final_book_links)
        sorted_data = sort_book_data(book_data, book_titles, image_urls)
        category_name = category_link.split('/')[-2]
        download_image(sorted_data, category_name)
        write_to_csv(sorted_data, f"{category_name}.csv")
        create_zip(category_name)



if __name__ == "__main__":
    main()
