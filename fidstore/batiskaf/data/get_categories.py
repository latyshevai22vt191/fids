import datetime
from multiprocessing import Pool
import os
import requests
from bs4 import BeautifulSoup
import csv
from defusedxml import minidom
import xml.etree.ElementTree as ET

def get_product_on_page(url, dates):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'lxml')
    all_products = soup.find_all(class_='item-wrap')
    if len(all_products) == 0:
        return None, None, None
    for product in all_products:
        img = product.find('img').get('src')
        src = product.find('a').get('href')
        name = product.find('img').get('alt')
        price = product.find('span', class_='price').text.replace('\xa0', '')
        req = requests.get(src)

        # src_product = req.text
        # with open('index.html', 'w', encoding='utf-8') as file:
        #     file.write(src_product)
        # soup_product = BeautifulSoup(src_product, 'lxml')
        soup_product = BeautifulSoup(req.content, 'lxml')
        category = ''
        categories = soup_product.find('div', class_='breadcrumbs').find('ul').find_all('li')[1:-1]
        for cat in categories:
            category += cat.text.replace('\n', '').strip()
        id = soup_product.find('p', class_='sku')
        if id != None:
            id = id.text
        else:
            id = 'По умолчанию'
        is_available = soup_product.find('p', class_='availability in-stock')
        description = soup_product.find('div', class_='short-description')
        if description == None:
            description = 'По умолчанию'
        else:
            description = description.find('div', class_='std').text
        if is_available == None:
            is_available = soup_product.find('p', class_='availability out-of-stock')
            is_available = is_available.find('a')
            if is_available != None:
                is_available = is_available.text.strip()
        else:
            is_available = is_available.text
        if is_available =='Есть в наличии':
            is_available = 'Да'
        else:
            is_available = 'Нет'
        data = [category, img, src, name, price, id, is_available, description]
        dates.append(data)

    current = soup.find('p', class_='amount').text.strip().split(' ')
    count = soup.find('p', class_='amount').text.strip().split(' ')
    if len(current) == 6:
        current = current[3]
        count = count[5]
        if current != count:
            next_url = soup.find("a", class_="next").get('href')
        else:
            next_url = None
        print(next_url)
        return count, current, next_url
    else:
        return None, None, None,


def get_parent_links():
    url = 'https://www.batiskaf.ru'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    categories = soup.find(class_='menu-athlete store-2 menu-menu-athlete')

    links = categories.find_all('li')
    parents_links = []
    for i in links:
        if 'data-toggle' in i.attrs.keys():
            parents_links.append(i.find('a').get('href').strip().replace('\n', ''))
    return parents_links


def make_csv_for_cat(link):
    today = datetime.datetime.now()
    print(link)
    print(today)
    dates = []
    count, current, next_url = get_product_on_page(link, dates)
    while current != count:
        count, current, next_url = get_product_on_page(next_url, dates)
    print(link.split('/')[3])
    with open(f'fidstore/batiskaf/data/files_cat/{link.split("/")[3].split(".")[0]}.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in dates:
            writer.writerow(row)
    print(link)
    print(today)


def make_batiskaf_csv():
    parents_links = get_parent_links()
    pool = Pool(processes=4)
    pool.map(make_csv_for_cat, parents_links[1:5])
    pool = Pool(processes=4)
    pool.map(make_csv_for_cat, parents_links[5:9])
    pool = Pool(processes=3)
    pool.map(make_csv_for_cat, parents_links[9:])
    with open(f'fidstore/batiskaf/data/batiskaf.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        files = os.listdir('files_cat')
        for file in files:
            with open(f'fidstore/batiskaf/data/files_cat/{file}', 'r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    writer.writerow(row)

def make_batiskaf_xml_vk():
    yml_catalog = ET.Element('yml_catalog')
    yml_catalog.set('date', f'{datetime.date.today()} {datetime.datetime.today().hour}:{datetime.datetime.today().minute}')
    shop = ET.SubElement(yml_catalog, 'shop')
    name_shop = ET.SubElement(shop, 'name')
    company_shop = ET.SubElement(shop, 'company')
    url_shop = ET.SubElement(shop, 'url')

    name_shop.text = 'batiskaf'
    company_shop.text = 'Батискаф'
    url_shop.text = 'https://www.batiskaf.ru/'
    data = ET.Element('data')

    currencies = ET.SubElement(shop, 'currencies')
    currency = ET.SubElement(currencies, 'currency')
    currency.set('id', 'RUB')
    currency.set('rate', '1')
    set_cat = set()
    with open('batiskaf.csv', 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            set_cat.add(row[0])
    cats = {}
    j = 1
    for i in set_cat:
        print(i.replace('\r', '').replace('\n', ''))
        cats[i.replace('\r', '').replace('\n', '')] = str(j)
        j += 1
    print(cats)
    categories = ET.SubElement(shop, 'categories')
    for i in cats:
        category = ET.SubElement(categories, 'category')
        category.set('id', cats[i])
        category.text = i

    offers = ET.SubElement(shop, 'offers')
    products = []
    with open('batiskaf.csv', 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            data = []
            for col in row:
                data.append(col)
            product = {
                "Категория": cats[data[0].replace('\r', '').replace('\n', '')],
                "Фото": data[1].replace('\r', '').replace('\n', ''),
                "Ссылка": data[2].replace('\r', '').replace('\n', ''),
                "Название": data[3].replace('\r', '').replace('\n', ''),
                "Цена": data[4].replace('\r', '').replace('\n', ''),
                "Артикул": data[5].replace('\r', '').replace('\n', ''),
                "В наличии": data[6].replace('\r', '').replace('\n', ''),
                "Описание": data[7].replace('\r', '').replace('\n', ''),
            }
            offer = ET.SubElement(offers, 'offer')
            offer.set('id', str(product['Артикул']))
            offer.set('available', 'true')
            products.append(product)
            name = ET.SubElement(offer, 'name')
            name.text = product['Название']
            categoryId = ET.SubElement(offer, 'categoryId')
            categoryId.text = product['Категория']
            picture = ET.SubElement(offer, 'picture')
            picture.text = product['Фото']
            price = ET.SubElement(offer, 'price')
            price.text = product['Цена'][:-4]
            currencyId = ET.SubElement(offer, 'currencyId')
            currencyId.text = 'RUB'
            # url = ET.SubElement(offer, 'url')
            # url.text = '<![CDATA[ '+product['Ссылка']+' ]]>'
            description = ET.SubElement(offer, 'description')
            description.text = product['Описание']
    xml_string = ET.tostring(yml_catalog).decode()
    xml_prettyxml = minidom.parseString(xml_string).toprettyxml()
    with open("fidstore/batiskaf/data/batiskaf.xml", 'w', encoding="utf-8") as xml_file:
        xml_file.write(xml_prettyxml)
    tree = ET.parse("fidstore/batiskaf/data/batiskaf.xml")
    root = tree.getroot()
    tree.write("fidstore/batiskaf/data/batiskaf.xml", encoding='utf-8', xml_declaration=True)

def start_parse():
    make_batiskaf_csv()
    make_batiskaf_xml_vk()


