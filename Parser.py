import urllib.request
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup as BS
import os
import csv


PAGE = 1 
REG = 'RU-MOW'
URL = 'https://www.detmir.ru/catalog/index/name/mashiny/'
HEADERS = { 'cookie': 'geoCityDMIso=' + REG } 
FILE = 'data.csv'
TOYS = []

def get_html(url):
    if REG == 'RU-SPE':
        headers = { 'cookie': 'geoCityDMIso=RU-SPE' }
    else:
        headers = HEADERS
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
    return the_page

def save_file(items, path):  
    with open(path, 'w', newline='', encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['id', 'title', 'price', 'promo_price', 'url'])
        for item in items:
            writer.writerow([item['id'], item['title'], item['price'], item['promo_price'], item['url']])


def get_content(html):
    toys = []
    soup = BS(html, 'html.parser')
    items = soup.find_all('a', class_='M_7 Nz')

    for item in items:
        if not item.find('p', class_="Na").get_text():
            FLAG = False
        promo_price = item.find('div', class_='Nk No')
        if promo_price:
            promo_price = item.find('div', class_='Nw').find_next('p', class_='Nl').get_text().replace('\xa0', ' ')
            price = item.find('div', class_='Nf').find_next('div', class_='Nk No').find_next('p', class_="Nm").find_next('span', class_='Nn').get_text().replace('\xa0', ' ')
        else:
            promo_price = "Нет промо цены"
            price = item.find('div', class_='Nk').find_next('p').get_text().replace('\xa0', ' ')
        toys.append({
            'id': item.get('href')[:46].replace('https://www.detmir.ru/product/index/id/', '').replace('/', ''),
            'title': item.find('p', class_="Na").get_text(),
            'price': price,
            'promo_price': promo_price,
            'url': item.get('href')
        })

    return(toys)

def parse():
    toys = []
    try:
        html = get_html(URL)
        toys = (get_content(html))
    except HTTPError as e:
        print('Сервер не выполнил запрос(')
        print('Код ошибки: ', e.code)
    except URLError as e:
        print('Не удалось подключится к серверу')
        print('Причина: ', e.reason)
    return (toys)
    
while True:
    TOYS.extend(parse())
    print(f"Идёт парсинг {PAGE} страницы ...")
    PAGE += 1
    URL = 'https://www.detmir.ru/catalog/index/name/mashiny/page/' + str(PAGE) + '/'
    if REG == 'RU-MOW' and PAGE == 61: 
        REG = 'RU-SPE'
        PAGE = 1
        URL = 'https://www.detmir.ru/catalog/index/name/mashiny/page/' + str(PAGE) + '/'
    elif REG == 'RU-SPE' and PAGE == 61:
        save_file(TOYS, FILE)
        os.startfile(FILE)
        break



