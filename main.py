import requests
from bs4 import BeautifulSoup
import json

# Функція для отримання інформації про цитати зі сторінки


def scrape_quotes_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    quotes = []
    for quote in soup.find_all('div', class_='quote'):
        text = quote.find('span', class_='text').text
        author = quote.find('small', class_='author').text
        tags = [tag.text for tag in quote.find_all('a', class_='tag')]
        quotes.append({
            'text': text,
            'author': author,
            'tags': tags
        })
    return quotes

# Функція для отримання інформації про всіх авторів


def scrape_authors(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    authors = {}
    for author in soup.find_all('div', class_='quote'):
        author_name = author.find('small', class_='author').text
        birthdate_tag = author.find('span', class_='author-born-date')
        birthplace_tag = author.find('span', class_='author-born-location')
        birthdate = birthdate_tag.text if birthdate_tag else None
        birthplace = birthplace_tag.text if birthplace_tag else None
        author_info = {
            'name': author_name,
            'birthdate': birthdate,
            'birthplace': birthplace
        }
        authors[author_name] = author_info
    return list(authors.values())


# Збираємо цитати зі всіх сторінок
all_quotes = []
page_number = 1
while True:
    url = f'http://quotes.toscrape.com/page/{page_number}/'
    quotes = scrape_quotes_page(url)
    if quotes:
        all_quotes.extend(quotes)
        page_number += 1
    else:
        break

# Зберігаємо цитати у файл quotes.json
with open('quotes.json', 'w', encoding='utf-8') as f:
    json.dump(all_quotes, f, ensure_ascii=False, indent=4)

# Збираємо інформацію про авторів
all_authors = scrape_authors('http://quotes.toscrape.com')
# Зберігаємо інформацію про авторів у файл authors.json
with open('authors.json', 'w', encoding='utf-8') as f:
    json.dump(all_authors, f, ensure_ascii=False, indent=4)
