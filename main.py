import requests
from bs4 import BeautifulSoup
from mongoengine import connect, Document, StringField, ListField, ReferenceField
from datetime import datetime
import json

# Підключення до MongoDB Atlas
connect('my_database',
        host='mongodb+srv://brainfisher13:<"PASS">@cluster0.3ufzbcf.mongodb.net/')

# Модель для авторів


class Author(Document):
    fullname = StringField(required=True)
    born_date = StringField()
    born_location = StringField()

# Модель для цитат


class Quote(Document):
    tags = ListField(StringField())
    author = ReferenceField(Author)
    quote = StringField()

# Функція для скрапінгу та отримання даних про цитати та авторів


def scrape_quotes():
    base_url = "http://quotes.toscrape.com"
    page_url = "/page/1"
    all_quotes = []

    while page_url:
        response = requests.get(base_url + page_url)
        soup = BeautifulSoup(response.text, "html.parser")
        quotes = soup.find_all(class_="quote")

        for quote in quotes:
            text = quote.find(class_="text").get_text()
            author = quote.find(class_="author").get_text()
            tags = [tag.get_text() for tag in quote.find_all(class_="tag")]

            all_quotes.append({
                "text": text,
                "author": author,
                "tags": tags
            })

        next_page = soup.find(class_="next")
        page_url = next_page.find("a")["href"] if next_page else None

    return all_quotes

# Функція для збереження даних у JSON файл


def save_to_json(all_quotes):
    with open('quotes.json', 'w', encoding='utf-8') as file:
        json.dump(all_quotes, file, ensure_ascii=False, indent=4)

# Функція для збереження даних у базу даних


def save_to_database(all_quotes):
    for quote_data in all_quotes:
        author_name = quote_data['author']
        author = Author.objects(fullname=author_name).first()
        if not author:
            author = Author(fullname=author_name).save()
        quote_data['author'] = author
        Quote(**quote_data).save()

# Функція для завантаження даних з JSON файлу у базу даних


def load_from_json():
    with open('quotes.json', 'r', encoding='utf-8') as file:
        all_quotes = json.load(file)
        save_to_database(all_quotes)

# Функція для завантаження даних з сайту, збереження у JSON та додавання у базу даних


def load_data():
    all_quotes = scrape_quotes()
    save_to_json(all_quotes)
    load_from_json()

# Функція для пошуку цитат за тегом, ім'ям автора або набором тегів


def search_quotes(query):
    if query.startswith('name:'):
        author_name = query.split(':')[1].strip()
        author = Author.objects(fullname=author_name).first()
        if author:
            quotes = Quote.objects(author=author)
            for quote in quotes:
                print(quote.quote)
    elif query.startswith('tag:'):
        tag = query.split(':')[1].strip()
        quotes = Quote.objects(tags=tag)
        for quote in quotes:
            print(quote.quote)
    elif query.startswith('tags:'):
        tags = query.split(':')[1].strip().split(',')
        quotes = Quote.objects(tags__in=tags)
        for quote in quotes:
            print(quote.quote)

# Головна функція для виконання скрипту


def main():
    load_data()
    while True:
        query = input("Введіть команду: ")
        if query == 'exit':
            break
        search_quotes(query)


if __name__ == "__main__":
    main()
