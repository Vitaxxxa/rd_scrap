import json
import re
import requests
import hashlib
import os
from bs4 import BeautifulSoup



def fetch_url(url, full_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with open(full_path, 'w') as f:
            f.write(response.text)

        return response.text
    else:
        return False

def get_content(url):
    filename = hashlib.md5(url.encode('utf-8')).hexdigest()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    full_path = os.path.join(dir_path, filename)

    try:
        with open(full_path, 'r') as f:
            if os.stat(full_path).st_size > 0:
                content = f.read()
                return content
            else:
                return False
    except:
        return fetch_url(url, full_path)

def save_to_json(jobs):
    with open(os.path.dirname(os.path.realpath(__file__)) +'/result.json', 'w') as f:
        json.dump(jobs, f, indent=4)

def extract_news(content):
    soup = BeautifulSoup(content, 'lxml')
    articles = soup.find_all('li', class_=re.compile(r'ListItem'))
    news = []

    for article in articles:
        link_tag = article.find('a', href=True)
        title_tag = link_tag.find('p') if link_tag else None

        if link_tag and title_tag:
            #якщо новин більше 5, то виходимо з циклу
            if len(news) >= 5:
                break

            title = title_tag.get_text(strip=True)
            url = link_tag['href']
            
            #беремо тільки новини, пропускаючи live та інші сторінки на яких немає Related Topics
            if "/articles/" in url:
                news.append({
                    'Link': 'https://www.bbc.com'+url
                })

    return news

def get_topics(url):
    content = get_content(url)

    if content:
        soup = BeautifulSoup(content, 'lxml')
        element = soup.find('h2', text=re.compile(r'Related Topics'))
    
        if element:
            # йдемо на 2 рівні вище, щоб отримати батьківський елемент
            parent_element = element.parent.parent
            
            # від батьківського елементу шукаємо всі посилання
            links = parent_element.find_all('a', href=True)

            
            link_list = []
            for link in links:
                text = link.get_text(strip=True)
                link_list.append(text)

            return link_list
        
        return []



def main():
    url = 'https://www.bbc.com/sport'

    content = get_content(url)

    if content:
        news = extract_news(content)
        result = []
        for post in news:
            parsed_content = get_topics(post['Link'])

            if parsed_content:
                post['Topics'] = parsed_content
                result.append(post)
        
        save_to_json(result)

if __name__ == '__main__':
    main()